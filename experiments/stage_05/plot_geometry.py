"""Render recorded host/trial positions without recomputing predictions."""
from pathlib import Path
import os,json
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'work/stage_05/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    folder=ROOT/'results/stage_05/run_002'
    output=folder/'trial_geometry.png'
    if output.exists():raise FileExistsError(output)
    record=json.loads((folder/'evaluation.json').read_text())
    case=next(c for c in record['cases'] if c['host_id']=='perovskite' and c['site_count']==40)
    trial=case['result']['configurations'][0];host=case['result']['host'];index=trial['replaced_indices'][0]
    xyz=np.array([s['fractional_coordinates'] for s in host['sites']])@np.array(host['lattice_angstrom'])
    colors={'Sr':'#8596ad','Ti':'#3267a4','O':'#d67b68',trial['candidate_element']:'#168676'}
    fig=plt.figure(figsize=(11,5.3))
    for panel in (1,2):
        ax=fig.add_subplot(1,2,panel,projection='3d')
        symbols=[s['element'] for s in host['sites']]
        if panel==2:symbols[index]=trial['candidate_element']
        for symbol in sorted(set(symbols)):
            ids=[i for i,s in enumerate(symbols) if s==symbol]
            ax.scatter(xyz[ids,0],xyz[ids,1],xyz[ids,2],s=65,c=colors[symbol],label=symbol,alpha=.8)
        ax.text(*xyz[index],f'  site {index}',fontsize=9)
        ax.set(xlabel='x (Å)',ylabel='y (Å)',zlabel='z (Å)',title='Host: SrTiO3 2×2×2' if panel==1 else f'Trial: {trial["candidate_element"]} at Ti site {index}')
        ax.legend(loc='upper left');ax.set_box_aspect((1,1,1))
    fig.suptitle('Recorded unrelaxed configuration: positions remain unchanged',fontsize=13)
    fig.text(.5,.015,'1/8 Ti sites replaced = 12.5%; 1/40 all atoms = 2.5%. No bonds, energy or stability inferred.',ha='center',fontsize=10)
    fig.tight_layout(rect=[0,.04,1,.95]);fig.savefig(output,dpi=180);plt.close(fig)


if __name__=='__main__':main()
