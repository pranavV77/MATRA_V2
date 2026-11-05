"""Frozen geometric validation experiment, not substitution-accuracy evaluation."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import hashlib
import importlib.metadata
import json
import os
import platform
from time import perf_counter
import statistics
import numpy as np
from pymatgen.core import Structure
from src.structures.service import StructureService
from src.structures.candidates import export_configurations
from src.structures.hosts import load_cif, structure_fingerprint


def main():
    import argparse,re
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-name',default='run_001')
    args=parser.parse_args()
    if not re.fullmatch(r'run_\d{3}',args.run_name):parser.error('Run name must match run_001 format')
    out=ROOT/'results/stage_05'/args.run_name
    out.mkdir(parents=True,exist_ok=True)
    output=out/'evaluation.json'
    if output.exists():raise FileExistsError('Preserve this run; explicitly select a fresh output path for a new experiment')
    service=StructureService()
    cases=[]
    for host_id,target in [('perovskite','Ti'),('wurtzite','Ga'),('aflow_zns','Zn')]:
        for scale in ([1,1,1],[2,1,1],[2,2,2]):
            request={'host_id':host_id,'supercell':scale}
            start=perf_counter();analysis=service.analyze(request);analysis_ms=(perf_counter()-start)*1000
            a=analysis['analysis'];index=next(s['index'] for s in a['sites'] if s['element']==target)
            p={**request,'target':target,'site_index':index,'k':3}
            start=perf_counter();result=service.generate(p);generation_ms=(perf_counter()-start)*1000
            expected_target_count=sum(s['element']==target for s in a['sites'])
            checks=[]
            for trial in result['configurations']:
                parsed=Structure.from_dict(trial['structure'])
                changed=[i for i,s in enumerate(parsed) if s.specie.symbol!=a['sites'][i]['element']]
                checks.append({'candidate':trial['candidate_element'],
                               'exact_selected_site_changed':changed==[index],
                               'site_count_preserved':len(parsed)==a['site_count'],
                               'coordinates_unchanged':bool(np.allclose(parsed.frac_coords,[s['fractional_coordinates'] for s in a['sites']],atol=0,rtol=0)),
                               'lattice_unchanged':bool(np.array_equal(parsed.lattice.matrix,a['lattice_angstrom'])),
                               'concentration_arithmetic_correct':trial['target_sublattice_fraction']==1/expected_target_count,
                               'gross_geometry_passed':trial['geometry']['gross_geometry_passed']})
            assert all(all(v is True for key,v in row.items() if key!='candidate') for row in checks)
            target_orbits=sum(o['element']==target for o in a['orbits'])
            cases.append({'host_id':host_id,'evidence_class':analysis['provenance']['evidence_class'],
                          'request':p,'site_count':a['site_count'],'spacegroup':a['spacegroup'],
                          'target_sites':expected_target_count,'symmetry_distinct_target_orbits':target_orbits,
                          'symmetry_reduction_fraction':1-target_orbits/expected_target_count,
                          'target_sublattice_fraction':1/expected_target_count,
                          'analysis_ms':analysis_ms,'generation_ms':generation_ms,'checks':checks,
                          'result':result})
            if scale==[1,1,1]:
                saved=export_configurations(result,out/'example_bundles')
                for path in Path(saved['directory']).glob('*.cif'):
                    imported,_=load_cif(path)
                    assert len(imported)==a['site_count']
    # Explicit charge examples are arithmetic checks, not reference chemistry labels.
    charge=service.generate({'host_id':'perovskite','target':'Ti','site_index':1,'k':2,
                             'candidate_symbols':['Zr','Nb'],'candidate_oxidation_states':{'Zr':4,'Nb':5}})
    samples=[]
    q={'host_id':'perovskite','supercell':[2,2,2],'target':'Ti','site_index':8,'k':3}
    for _ in range(2): service.generate(q)
    for _ in range(10):
        start=perf_counter();service.generate(q);samples.append((perf_counter()-start)*1000)
    record={'scope':'geometric_and_software_validation_only','environment':{'python':platform.python_version(),'os':platform.platform(),
            'dependencies':{p:importlib.metadata.version(p) for p in ['pymatgen','spglib','numpy']},'compute':'local CPU; no GPU/DFT/training'},
            'dataset':{'analytical_host_count':2,'database_host_count':1,'host_supercell_requests':len(cases),
                       'source_acquisition':json.loads((ROOT/'data/raw/stage_05_hosts/acquisition.json').read_text()),
                       'reference_roles':'AFLOW prototype topology/spacegroup plus analytical geometry, NOT substitution-success labels'},
            'parameters':{'k':3,'scales':[[1,1,1],[2,1,1],[2,2,2]],'symprec_angstrom':0.01,'mode':'single_site',
                          'seed':'not applicable: deterministic enumeration'},
            'cases':cases,'generated_trial_count':sum(len(c['checks']) for c in cases),
            'checks_passed':sum(all(v is True for k,v in row.items() if k!='candidate') for c in cases for row in c['checks']),
            'formal_charge_examples':[{'candidate':c['candidate_element'],**c['formal_charge_screen']} for c in charge['configurations']],
            'warm_performance':{'request':q,'warmups':2,'calls':10,'raw_ms':samples,'median_ms':statistics.median(samples),
                                'p95_ms':float(np.percentile(samples,95))},
            'scientific_substitution_accuracy':None,'held_out_substitution_cases':0,
            'limitations':['27 geometric constructions are not 27 chemical reference positives.',
                           'Unchanged coordinates make collision-check retention expected by construction.',
                           'Symmetry reduction counts single-site orbits, not distinct multi-site orderings.',
                           'Source CIF is database geometry; experimental refinement not independently checked.',
                           'No stability, energy, gap, solubility, carrier activation or preference claim.']}
    with output.open('x',encoding='utf-8') as f:json.dump(record,f,indent=2,allow_nan=False)
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'work/stage_05/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(1,2,figsize=(11,4.6))
    for host in ('perovskite','wurtzite','aflow_zns'):
        rows=[c for c in cases if c['host_id']==host]
        axs[0].plot([c['site_count'] for c in rows],[100*c['target_sublattice_fraction'] for c in rows],'o-',label=host)
        axs[1].plot([c['site_count'] for c in rows],[100*c['symmetry_reduction_fraction'] for c in rows],'o-',label=host)
    axs[0].set(xlabel='Atoms in periodic cell',ylabel='Target sites replaced (%)',title='One-site replacement: exact concentration')
    axs[1].set(xlabel='Atoms in periodic cell',ylabel='Single-site representatives avoided (%)',title='Symmetry reduction: not chemical filtering')
    axs[0].legend();axs[1].legend();fig.tight_layout();fig.savefig(out/'concentration_and_symmetry.png',dpi=180);plt.close(fig)
    print(json.dumps({'requests':len(cases),'trials':record['generated_trial_count'],'passed':record['checks_passed'],'warm_performance':{k:v for k,v in record['warm_performance'].items() if k!='raw_ms'}},indent=2))


if __name__=='__main__':main()
