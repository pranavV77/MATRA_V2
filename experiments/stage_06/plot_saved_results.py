"""Presentation figures from saved predictions; no new inference/reference labels."""
from pathlib import Path
import json,os
ROOT=Path(__file__).resolve().parents[2]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'work/stage_06/cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    directory=ROOT/'results/stage_06/run_002'
    png=directory/'relaxation_for_review.png';svg=directory/'relaxation_for_review.svg'
    if png.exists() or svg.exists():raise FileExistsError('Preserve existing review figures')
    d=json.loads((directory/'evaluation.json').read_text())
    names={'perovskite':'SrTiO3: Ti → Zr','wurtzite':'GaN: Ga → Al','aflow_zns':'ZnS: Zn → Cd'}
    fig,axes=plt.subplots(1,2,figsize=(11,4.8))
    for case in d['cases']:
        history=case['trial']['relaxation']['history'];initial=history[0]['total_energy_ev']
        x=[p['step'] for p in history]
        axes[0].plot(x,[(p['total_energy_ev']-initial)/case['site_count'] for p in history],label=names[case['host_id']])
        axes[1].plot(x,[max(p['maximum_force_ev_per_angstrom'],1e-12) for p in history],label=names[case['host_id']])
    axes[0].set(title='Energy change within each fixed composition',xlabel='Relaxation step',ylabel='Change from starting energy (eV/atom)')
    axes[1].set(title='Maximum force during fixed-cell relaxation',xlabel='Relaxation step',ylabel='Maximum force (eV/Å)',yscale='log')
    axes[1].axhline(.05,color='black',linestyle='--',label='0.05 eV/Å stopping threshold')
    for ax in axes:ax.legend(fontsize=9);ax.grid(alpha=.15)
    fig.text(.5,.015,'MACE-MP-0b2-small predictions. Three demonstration trials; no independent DFT accuracy or thermodynamic-stability claim.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.055,1,1]);fig.savefig(png,dpi=200);fig.savefig(svg);plt.close(fig)


if __name__=='__main__':main()
