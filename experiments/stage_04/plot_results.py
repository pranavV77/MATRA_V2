"""Plot recorded measurements into a NEW directory; never rerun inference."""
import argparse,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'work/stage_04/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,help='New project-relative output directory')
    args=parser.parse_args();out=(ROOT/args.output).resolve()
    if ROOT not in out.parents: parser.error('Output must stay inside project')
    out.mkdir(parents=True,exist_ok=False)
    d=json.loads((ROOT/'results/stage_04/run_001/evaluation.json').read_text())
    methods=list(d['summary']); labels=['PN','Atom2Vec','Property','Weighted','RRF']
    fig,ax=plt.subplots(figsize=(8,5));bars=ax.bar(labels,[d['summary'][m]['mrr'] for m in methods]);ax.bar_label(bars,fmt='%.3f');ax.set_ylim(0,1.15);ax.set_ylabel('Mean reciprocal rank');ax.set_title('2 development references; zero held-out cases');fig.tight_layout();fig.savefig(out/'retrieval_comparison.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,5))
    for offset,c in zip([-.18,.18],d['reference_cases']): ax.bar([i+offset for i in range(5)],[c['metrics'][m]['best_known_rank'] for m in methods],.36,label=c['target']+' to '+c['known_candidate'])
    ax.set_xticks(range(5),labels);ax.set_ylabel('Known-candidate rank: lower is better');ax.legend();fig.tight_layout();fig.savefig(out/'reference_ranks.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,6));a=[[d['agreement'][m][n]['mean_top10_jaccard'] for n in methods] for m in methods];im=ax.imshow(a,vmin=0,vmax=1);ax.set_xticks(range(5),labels);ax.set_yticks(range(5),labels);ax.set_title('Top-10 overlap across 79 targets: not accuracy');fig.colorbar(im,ax=ax);fig.tight_layout();fig.savefig(out/'method_agreement.png',dpi=180);plt.close(fig)
if __name__=='__main__': main()
