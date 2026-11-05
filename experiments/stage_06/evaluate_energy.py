"""Recorded potential consistency and relaxation; no fabricated external energy labels."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import hashlib,json,os,time,statistics,platform
from datetime import datetime,timezone
import numpy as np
from pymatgen.core import Lattice,Structure
from pymatgen.io.cif import CifWriter
from src.energy.backend import EnergyBackend
from src.energy.contracts import neutral_geometry_from_stage5
from src.structures.hosts import structure_fingerprint


def peak_memory():
    if os.name!='nt':return {'status':'not_measured_on_this_platform'}
    import ctypes
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(name,ctypes.c_size_t) for name in
            ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage',
             'QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
    counters=Counters();counters.cb=ctypes.sizeof(counters)
    handle=ctypes.c_void_p(-1)  # Windows current-process pseudo-handle.
    ok=ctypes.windll.psapi.GetProcessMemoryInfo(handle,ctypes.byref(counters),ctypes.sizeof(counters))
    return {'status':'measured','process_peak_working_set_bytes':int(counters.PeakWorkingSetSize),
            'process_working_set_bytes':int(counters.WorkingSetSize),'scope':'entire isolated process including imports/model/graphs'} if ok else {'status':'measurement_failed'}


def main():
    import argparse,re
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run-name',default='run_002')
    args=parser.parse_args()
    if not re.fullmatch(r'run_\d{3}',args.run_name):parser.error('Run name must match run_001 format')
    out=ROOT/'results/stage_06'/args.run_name;out.mkdir(parents=True,exist_ok=True);output=out/'evaluation.json'
    if output.exists():raise FileExistsError('Preserve the recorded run; select a fresh run directory in a reviewed rerun')
    source=ROOT/'results/stage_05/run_002/evaluation.json';stage5=json.loads(source.read_text())
    backend=EnergyBackend();records=[]
    selections=[('perovskite',40,'Zr'),('wurtzite',4,'Al'),('aflow_zns',4,'Cd')]
    for host_id,size,candidate in selections:
        case=next(c for c in stage5['cases'] if c['host_id']==host_id and c['site_count']==size)
        info=case['result']['host']
        host=Structure(Lattice(info['lattice_angstrom']),[s['species'] for s in info['sites']],
                       [s['fractional_coordinates'] for s in info['sites']])
        assert structure_fingerprint(host)==info['structure_sha256']
        original=next(c for c in case['result']['configurations'] if c['candidate_element']==candidate)
        trial=neutral_geometry_from_stage5(Structure.from_dict(original['structure']))
        host_prediction=backend.predict(neutral_geometry_from_stage5(host))
        start=time.perf_counter();assessed=backend.assess(trial,relax=True,max_steps=100,fmax=.05)
        elapsed=(time.perf_counter()-start)*1000
        r=assessed['relaxation']
        path=out/f'{host_id}_{candidate}_relaxed.cif'
        relaxed=Structure.from_dict(r['final_structure'])
        for i,s in enumerate(relaxed):s.label=f'{s.specie.symbol}{i}'
        with path.open('x',encoding='utf-8') as f:f.write(str(CifWriter(relaxed)))
        records.append({'host_id':host_id,'site_count':size,'candidate':candidate,
                        'selected_indices':original['replaced_indices'],
                        'target_sublattice_fraction':original['target_sublattice_fraction'],
                        'source_evidence_class':case['evidence_class'],'source_geometry_sha256':info['structure_sha256'],
                        'host_prediction':host_prediction,'trial':assessed,'assessment_ms':elapsed,
                        'relaxed_cif':path.relative_to(ROOT).as_posix(),
                        'comparison_policy':'Host/trial raw energies are different-composition predictions; not a stability ranking.'})
    base_case=next(c for c in stage5['cases'] if c['host_id']=='perovskite' and c['site_count']==5)
    a=base_case['result']['host'];host=Structure(Lattice(a['lattice_angstrom']),[s['species'] for s in a['sites']],
                            [s['fractional_coordinates'] for s in a['sites']])
    base=backend.predict(host)
    moved=host.copy();moved.translate_sites(list(range(len(host))),[.137,.283,.419],frac_coords=True,to_unit_cell=True)
    expanded=host.copy();expanded.make_supercell([2,1,1])
    permutation=[4,2,0,3,1];reordered=Structure(host.lattice,[host[i].specie for i in permutation],host.frac_coords[permutation])
    angle=.321;rotation=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]])
    rotated=Structure(Lattice(host.lattice.matrix@rotation.T),[s.specie for s in host],host.frac_coords)
    checks=[]
    for name,s in [('translation',moved),('permutation',reordered),('rotation',rotated),('supercell_extensivity',expanded)]:
        p=backend.predict(s);delta=abs(base['energy_ev_per_atom']-p['energy_ev_per_atom'])
        checks.append({'check':name,'absolute_energy_difference_ev_per_atom':delta,'tolerance_ev_per_atom':1e-7,'passed':delta<1e-7})
    perturbed=host.copy();perturbed.translate_sites([1],[.04,0,0],frac_coords=False)
    plus=perturbed.copy();minus=perturbed.copy();delta=1e-4
    plus.translate_sites([1],[delta,0,0],frac_coords=False);minus.translate_sites([1],[-delta,0,0],frac_coords=False)
    force=backend.predict(perturbed)['forces_ev_per_angstrom'][1][0]
    finite=-(backend.predict(plus)['total_energy_ev']-backend.predict(minus)['total_energy_ev'])/(2*delta)
    force_check={'model_force_ev_per_angstrom':force,'finite_difference_force_ev_per_angstrom':finite,
                 'absolute_difference_ev_per_angstrom':abs(force-finite),'tolerance_ev_per_angstrom':1e-3,
                 'passed':abs(force-finite)<1e-3,'displacement_angstrom':delta,'reference_type':'same-model numerical derivative, NOT DFT reference'}
    assert all(c['passed'] for c in checks) and force_check['passed']
    timings=[]
    for _ in range(2):backend.predict(host)
    for _ in range(10):
        t=time.perf_counter();backend.predict(host);timings.append((time.perf_counter()-t)*1000)
    record={'executed_utc':datetime.now(timezone.utc).isoformat(),'scope':'model_predictions_and_numerical_consistency_only',
            'model':backend.info(),'environment':{'python':platform.python_version(),'platform':platform.platform()},
            'input_snapshot':{'path':source.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()},
            'parameters':{'device':'cpu','dtype':'float64','threads':2,'fmax_ev_per_angstrom':.05,'max_steps':100,'cell':'fixed','optimizer':'FIRE',
                          'model_input_policy':'Neutral atomic identities and geometry; source formal oxidation metadata retained in Stage 5 snapshot, not interpreted as an electronic charge-state request'},
            'cases':records,'consistency_checks':checks,'force_derivative_check':force_check,
            'relaxation_convergence':{'attempted':len(records),'converged':sum(r['trial']['relaxation']['converged'] for r in records)},
            'warm_static_timing':{'atoms':5,'warmups':2,'calls':10,'cache_policy':'reset calculator before each prediction; fresh inference',
                                  'raw_ms':timings,'median_ms':statistics.median(timings),
                                  'p95_ms':float(np.percentile(timings,95))},'process_memory':peak_memory(),
            'independent_reference_cases':0,'external_energy_mae_ev_per_atom':None,'external_force_mae_ev_per_angstrom':None,
            'energy_above_hull':None,'stability_classification':None,
            'limitations':['No independent numerical DFT energy/force references admitted; no accuracy metric claimed.',
                           'Local optimizer convergence and energy decrease do not prove thermodynamic stability.',
                           'Fixed-cell relaxation excludes cell-size/shape accommodation.',
                           'High replacement fractions are periodic substitution examples, not validated dilute dopants.',
                           'No cross-composition raw-energy ranking, formation/hull energy, band-gap or activation prediction.']}
    with output.open('x',encoding='utf-8') as f:json.dump(record,f,indent=2,allow_nan=False)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(1,2,figsize=(11,4.5))
    for r in records:
        h=r['trial']['relaxation']['history'];e0=h[0]['total_energy_ev'];label=r['host_id']+' → '+r['candidate']
        axs[0].plot([x['step'] for x in h],[(x['total_energy_ev']-e0)/r['site_count'] for x in h],label=label)
        axs[1].plot([x['step'] for x in h],[max(x['maximum_force_ev_per_angstrom'],1e-12) for x in h],label=label)
    axs[0].set(xlabel='Optimizer step',ylabel='Within-case energy change (eV/atom)',title='Fixed-cell relaxation: each curve has its own zero')
    axs[1].set(xlabel='Optimizer step',ylabel='Maximum force (eV/Å)',title='Model force convergence; not stability validation',yscale='log')
    axs[1].axhline(.05,color='black',linestyle='--',label='Declared force threshold')
    axs[0].legend();axs[1].legend();fig.tight_layout();fig.savefig(out/'relaxation_trajectories.png',dpi=180);plt.close(fig)
    print(json.dumps({'model':record['model']['model_id'],'supported_elements':record['model']['supported_element_count'],
                      'convergence':record['relaxation_convergence'],'checks':checks,'force_check':force_check,
                      'warm_median_ms':record['warm_static_timing']['median_ms'],'memory':record['process_memory']},indent=2))


if __name__=='__main__':main()
