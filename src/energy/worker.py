"""Isolated process boundary: validated project-local request/response files."""
import argparse,contextlib,json,traceback
from pathlib import Path
from src.similarity_validation import PROJECT_ROOT


def bounded_path(value):
    path=Path(value).resolve()
    if not path.is_relative_to(PROJECT_ROOT):raise ValueError('Worker files must remain inside project')
    return path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request',required=True);parser.add_argument('--response',required=True)
    args=parser.parse_args();request=bounded_path(args.request);response=bounded_path(args.response)
    if response.exists():raise FileExistsError('Worker response must not overwrite existing output')
    if request.stat().st_size>2_000_000:raise ValueError('Worker request exceeds bounded size')
    try:
        data=json.loads(request.read_text(encoding='utf-8'))
        if not isinstance(data,dict) or set(data)!={'tasks'} or not isinstance(data['tasks'],list) or not 1<=len(data['tasks'])<=4:
            raise ValueError('Worker requires 1..4 explicit tasks')
        # Libraries print initialization banners; protocol results go only to the response file.
        from src.energy.backend import EnergyBackend
        from pymatgen.core import Structure
        backend=EnergyBackend();results=[]
        for task in data['tasks']:
            if not isinstance(task,dict) or set(task)-{'structure','relax','max_steps','fmax','label'}:
                raise ValueError('Invalid worker task fields')
            result=backend.assess(Structure.from_dict(task['structure']),relax=task.get('relax',False),
                                  max_steps=task.get('max_steps',100),fmax=task.get('fmax',.05))
            if result['relaxation']['attempted']:
                from pymatgen.io.cif import CifWriter
                import hashlib
                relaxed=Structure.from_dict(result['relaxation']['final_structure'])
                for i,site in enumerate(relaxed):site.label=f'{site.specie.symbol}{i}'
                cif=response.parent/f'relaxed_{len(results)+1:02d}.cif'
                with cif.open('x',encoding='utf-8') as out:out.write(str(CifWriter(relaxed)))
                result['relaxation']['relaxed_cif_path']=str(cif)
                result['relaxation']['relaxed_cif_sha256']=hashlib.sha256(cif.read_bytes()).hexdigest()
            results.append({'label':task.get('label','structure'),**result})
        result={'ok':True,'model':backend.info(),'results':results}
    except Exception as exc:
        traceback.print_exc()
        result={'ok':False,'error_type':type(exc).__name__,'error':str(exc)}
    with response.open('x',encoding='utf-8') as out:json.dump(result,out,indent=2,allow_nan=False)
    if not result['ok']:raise SystemExit(1)


if __name__=='__main__':main()
