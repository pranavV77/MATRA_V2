"""Additional executed diagnostics; does not change production code or datasets."""
from pathlib import Path
import json
import os
import statistics
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
os.chdir(ROOT)
OUT=ROOT/'results/stage_01/run_001'
if (OUT/'supplemental_checks.json').exists():
    raise FileExistsError('Supplemental results already exist; do not overwrite.')
os.environ['MPLCONFIGDIR']=str(OUT/'matplotlib_cache')
import numpy as np
import pandas as pd
from src.pn_similarity.pn_engine import PNSimilarityEngine
from src.property_similarity.property_engine import PropertySimilarityEngine
from src.atom2vec.atom2vec_engine import Atom2VecEngine

engines={'PN':PNSimilarityEngine(),'Atom2Vec':Atom2VecEngine(),'Property':PropertySimilarityEngine()}
master=pd.read_parquet('data/processed/elements_master.parquet')
records=[]
dup=pd.concat([master,master[master.symbol=='Al']],ignore_index=True)
path=OUT/'fixtures/duplicate_candidate.parquet';dup.to_parquet(path,index=False)
for name,cls in [('PN',PNSimilarityEngine),('Property',PropertySimilarityEngine)]:
    result=cls(str(path)).get_top_k('Ga',1000)
    names=[r['candidate_element'] for r in result]
    records.append({'case':name+':duplicate_candidate','expected':'Reject duplicate or return unique candidates',
                    'passed':len(names)==len(set(names)), 'total':len(names),'unique':len(set(names)),
                    'Al_count':names.count('Al')})
zero=OUT/'fixtures/zero_cache.npz'
np.savez_compressed(zero,common_symbols=np.array(['Ga','Al']),F_norm=np.zeros((2,2)))
e=Atom2VecEngine(cache_embedding_path=str(zero))
records.append({'case':'Atom2Vec:zero_vectors','expected':'Reject zero-norm cached vectors',
                'passed':False,'observed_self_similarity':e.compute_similarity('Ga','Ga'),
                'observed_ranking':e.get_top_k('Ga')})
benchmark=json.loads((OUT/'legacy_workspace/results/runs/task2_benchmark_evaluation.json').read_text())
arithmetic={}
for name in engines:
    cases=benchmark['detailed_case_evaluations'];count=len(cases)
    ranks=[];recalls=[];hits={k:0 for k in [1,3,5,10]}
    for c in cases:
        ranked=[r['candidate_element'] for r in c['rankings'][name]['top_10']]
        pos=set(c['known_substituents']);rs=[i+1 for i,s in enumerate(ranked) if s in pos]
        best=min(rs) if rs else None;ranks.append(best)
        recalls.append(len(set(ranked)&pos)/len(pos))
        for k in hits:hits[k]+=int(any(s in pos for s in ranked[:k]))
    independently={'hit_at_'+str(k):round(v/count,4) for k,v in hits.items()}
    independently.update(mrr=round(sum(1/r if r else 0 for r in ranks)/count,4),
                         mean_recall_at_10=round(sum(recalls)/count,4))
    arithmetic[name]={'computed':independently,'matches':all(benchmark['summary_metrics'][name][k]==v for k,v in independently.items())}
timings={}
for name,engine in engines.items():
    for _ in range(5):engine.get_top_k('Ga',10)
    samples=[]
    for _ in range(30):
        t=time.perf_counter();engine.get_top_k('Ga',10);samples.append(1000*(time.perf_counter()-t))
    timings[name]={'query':'Ga','k':10,'warmups':5,'repeats':30,'cache':'warm, engines already initialized',
                   'milliseconds_samples':samples,'p50_ms':statistics.median(samples),
                   'p95_ms':float(np.percentile(samples,95))}
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONUTF8']='1'
rerun=subprocess.run([sys.executable,'-B','-X','utf8','experiments/stage_01/audit_baseline.py','--run-id','run_001'],env=env,capture_output=True,text=True,encoding='utf-8')
(OUT/'repeated_run_guard.txt').write_text(rerun.stdout+rerun.stderr,encoding='utf-8')
records.append({'case':'audit_runner:existing_run_id','expected':'Reject repeated run rather than overwrite',
                'passed':rerun.returncode!=0 and 'FileExistsError' in rerun.stderr,'exit_code':rerun.returncode})
# Simulated dependency-unavailable environment; -S deliberately hides site packages.
missingdep=subprocess.run([sys.executable,'-B','-S','-c','import numpy'],capture_output=True,text=True,encoding='utf-8')
(OUT/'dependency_unavailable.txt').write_text(missingdep.stdout+missingdep.stderr,encoding='utf-8')
records.append({'case':'environment:simulated_missing_dependency','expected':'Import failure when site-packages are deliberately hidden',
                'passed':missingdep.returncode!=0 and 'ModuleNotFoundError' in missingdep.stderr,
                'scope':'Simulation only; no installed dependency was removed.'})
payload={'records':records,'independent_metric_arithmetic':arithmetic,'warm_inference_timings':timings}
(OUT/'supplemental_checks.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
print(json.dumps(payload,indent=2))
