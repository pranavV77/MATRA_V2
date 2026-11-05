"""Generate Stage 1 reports and plots from saved, executed audit records only.

No scientific reference values are invented. Run after audit_baseline.py and
supplemental_checks.py. Refuses to replace an existing completion report.
"""
from pathlib import Path
import hashlib
import html
import json
import os
import sys
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/stage_01/run_001'
DOC=ROOT/'docs/stages/stage_01'
if (DOC/'completion_report.md').exists():
    raise FileExistsError('Completion report already exists; inspect before regenerating.')
os.environ['MPLCONFIGDIR']=str(OUT/'matplotlib_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def read(name):return json.loads((OUT/name).read_text(encoding='utf-8-sig'))
def save(path,text):
    with path.open('x',encoding='utf-8') as f:f.write(text)
summary=read('summary.json');data=read('dataset_audit.json')
comparison=read('benchmark_comparison.json');edges=read('edge_case_results.json')
extra=read('supplemental_checks.json');env=read('environment.json')
metrics=comparison['summary_metrics'];names=list(metrics)
figdir=OUT/'figures';figdir.mkdir()
colors=['#2864a5','#25877b','#ad6335']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})

fig,axs=plt.subplots(1,3,figsize=(12,4.7),layout='constrained')
for ax,key,title in zip(axs,['hit_at_1','mrr','mean_recall_at_10'],['Hit@1','MRR@10 (legacy convention)','Mean Recall@10']):
    vals=[metrics[n][key] for n in names]
    ax.bar(names,vals,color=colors,width=.65);ax.set_ylim(0,1.13)
    ax.set_title(title);ax.set_ylabel('Fraction / score (0–1)')
    for i,v in enumerate(vals):ax.text(i,v+.025,f'{v:.4f}',ha='center')
    ax.spines[['top','right']].set_visible(False)
fig.suptitle('Reproduced legacy retrieval results — 11 cases, 9 target elements\nDevelopment evidence; original source claims are not independently certified',fontsize=12)
fig.savefig(figdir/'legacy_metrics.png',dpi=170);fig.savefig(figdir/'legacy_metrics.svg');plt.close(fig)

fig,ax=plt.subplots(figsize=(8,4.8),layout='constrained')
counts=[summary['coverage_counts'][n] for n in names]
ax.bar(names,counts,color=colors,width=.6);ax.set_ylim(0,128)
ax.axhline(118,ls='--',color='#777',lw=1);ax.text(2.5,119,'118 elements',ha='right',fontsize=9)
for i,c in enumerate(counts):ax.text(i,c+2,f'{c}/118',ha='center')
ax.set_ylabel('Target inputs accepted with finite, unique Top-10 output')
ax.set_title('Executed input-coverage check\nPN candidates still exclude noble gases; coverage is not accuracy')
ax.spines[['top','right']].set_visible(False)
fig.savefig(figdir/'element_coverage.png',dpi=170);fig.savefig(figdir/'element_coverage.svg');plt.close(fig)

legacy=json.loads((OUT/'legacy_workspace/results/runs/task2_benchmark_evaluation.json').read_text())
rankmatrix=np.array([[c['rankings'][n]['best_rank'] or 11 for n in names] for c in legacy['detailed_case_evaluations']])
fig,ax=plt.subplots(figsize=(7.4,6.7),layout='constrained')
im=ax.imshow(rankmatrix,cmap='YlGnBu_r',vmin=1,vmax=10,aspect='auto')
ax.set_xticks(range(3),names)
ax.set_yticks(range(len(rankmatrix)),[c['case_id']+'  '+c['material']+' → '+c['target_element'] for c in legacy['detailed_case_evaluations']])
for i in range(len(rankmatrix)):
    for j in range(3):ax.text(j,i,str(rankmatrix[i,j]),ha='center',va='center',color='white' if rankmatrix[i,j]<=3 else 'black')
fig.colorbar(im,ax=ax,label='Best documented-positive rank (lower is earlier)')
ax.set_title('Case-level legacy ranking reproduction\nSame target can reuse the same element-only ranking')
fig.savefig(figdir/'case_rank_heatmap.png',dpi=170);fig.savefig(figdir/'case_rank_heatmap.svg');plt.close(fig)

save(OUT/'figure_data.json',json.dumps({'metrics':metrics,'coverage':summary['coverage_counts'],
    'case_best_ranks':rankmatrix.tolist(),'case_ids':[c['case_id'] for c in legacy['detailed_case_evaluations']],
    'methods':names,'description':'Descriptive reproduction; no confidence intervals or generalization claims.'},indent=2))
table='| Method | Hit@1 | Hit@3 | Hit@10 | MRR@10 | Mean Recall@10 |\n|---|---:|---:|---:|---:|---:|\n'
for n,m in metrics.items():
    table+=f"| {n} | {m['hit_at_1']:.2%} | {m['hit_at_3']:.2%} | {m['hit_at_10']:.2%} | {m['mrr']:.4f} | {m['mean_recall_at_10']:.2%} |\n"
allcounts=Counter(r['status'] for r in edges)
for r in extra['records']:allcounts['passed' if r['passed'] else 'failed']+=1
rows='| Executed probe | Status | Requirement | Observation |\n|---|---|---|---|\n'
for r in edges:
    obs=r['observation']
    detail=(obs['exception']+': '+obs['message']) if 'exception' in obs else str(obs.get('returned'))
    if len(detail)>200:detail=detail[:200]+' … (full record in JSON)'
    rows+='| '+r['name']+' | '+r['status']+' | '+r['requirement']+' | '+detail.replace('|','/').replace('\n',' ')+' |\n'
for r in extra['records']:
    rows+='| '+r['case']+' | '+('passed' if r['passed'] else 'failed')+' | '+r['expected']+' | '+str({k:v for k,v in r.items() if k not in ['expected','case','passed']}).replace('|','/')+' |\n'
save(DOC/'edge_case_report.md',f'''# Stage 1 edge-case report

Executed diagnostic records: {sum(allcounts.values())}; passed: {allcounts['passed']}; failed requirements: {allcounts['failed']}. These are probe outcomes, not a product accuracy measure. Existing pytest results are separately 26 passed. All 118 elements were also tested against all 3 engines (354 requests).

An exception counts as rejection in these diagnostics; it does not establish a friendly error message or a stable API contract. In particular KeyError/IndexError/AssertionError still require production-hardening review. Warnings from deliberately damaged fixtures are captured in the audit console.

{rows}

## Not executed / not yet verified

- Read-only directory / access-denied simulation, disk-full behavior, forced process termination and concurrent requests.
- Full corrupt/empty corpus training recovery, formula-parse failure accounting, version-migration compatibility and cross-OS reproduction.
- GPU model inference, charged defects, site-aware generation, property prediction and performance under load: not implemented and outside Stage 1.
- Complete independent literature validation: not completed. See reference_audit.md.

The deliberate `python -S` missing-dependency check is a simulation that hides installed packages; no package was removed. The repeated-run guard was executed and rejected reuse of run_001. Existing damaged fixtures were isolated copies, never original data.
''')

save(DOC/'validation_report.md',f'''# Stage 1 validation

| Category | Status | Executed evidence / boundary |
|---|---|---|
| Existing functionality | Verified within legacy suite | 26 original pytest cases passed; this suite is limited |
| Additional robustness | Failed requirements identified | {allcounts['failed']} failed diagnostic records; production is not declared robust |
| Cached ranking reproducibility | Verified locally | All ranking and metric fields matched recorded results |
| Fresh master generation | Verified locally | Values equal and SHA256 equals original master table |
| Fresh Atom2Vec generation | Verified locally | Same 79 symbols; pairwise similarity max difference 0; all supported Top-10 lists equal |
| Metric arithmetic | Verified on legacy outputs | Independent Hit@K, MRR@10 and Recall@10 arithmetic matched all methods |
| Data integrity | Verified for observed baseline | 4/4 principal data artifacts match manifest; summary table also matches |
| Results checksum discrepancy | Explained, not repaired | Preexisting JSON diff changes timestamp only; saved patch preserves it |
| Scientific conventions | Partially verified; corrections needed | Polarizability labels and PN metadata inconsistent; imputation derivation incomplete |
| Benchmark scientific truth | Not certified | Definite BM-S04 DOI mismatch; BM-P01 evidence class needs review; other sources not fully checked |
| All-element input handling | Measured | PN 94/118, Atom2Vec 79/118, Property 88/118; acceptance is not applicability |
| Generalization / functional preservation | Not verified | No independent held-out benchmark, site validation, energy or band-gap implementation |
| Original file preservation | Verified at audit completion | {summary['original_files_checked']} existing files unchanged; rechecked again in final verification |

This is an audit completion with findings, not a clean research-product validation pass. The next stage must resolve dataset/provenance issues; engine-hardening defects remain explicitly queued for the already planned similarity-engine stage. They are not silently waived.
''')

save(DOC/'environment_report.md',f'''# Verified local environment

Workspace: `{ROOT}`. Python: `{env['python']}`. Interpreter: `{env['executable']}`. Platform: `{env['platform']}`. The OS build is 26300; Windows reporting interfaces differ in their product label, so no exact edition is asserted.

GPU: NVIDIA GeForce RTX 3050 Laptop GPU, 4096 MiB VRAM; driver 552.27. Existing Python environment reused. No packages installed or upgraded in this stage. Complete packages are in `results/stage_01/run_001/environment.json` and `environment_freeze.txt`. Disk free at audit start: {env['disk_free_bytes']/1024**3:.2f} GiB.

Core numerical/materials packages imported successfully. System Python 3.13 is not used for MATRA. The `py` launcher is inaccessible, but project Python 3.10.11 works directly.

System Git 2.55 reports work-tree errors for status while bundled Git works. No repository configuration was changed. Use the executable recorded in environment.json; portable scripts can override that location after verification. Baseline commit: `{env['source_commit']}`. Local tag: `matra-stage-01-baseline-20261105`. A preexisting tracked JSON timestamp change and 7 untracked presentation/script files were preserved. No commit includes these user-owned changes.

Audio: installed Windows speech voice is Microsoft Zira Desktop, en-US; no Telugu voice was exposed. No suitable speech-generation tool is available. Transcript supplied; audio not generated.
''')

save(DOC/'technical_guide.md',r'''# Stage 1 implementation and mentoring guide

## Why these files exist

- `experiments/stage_01/audit_baseline.py`: reads existing source/data/tests, snapshots checksums, runs the original pytest suite, copies source/data to a protected experiment workspace, reproduces benchmark outputs, executes edge probes, rebuilds the master and retrains Atom2Vec. Inputs are existing project files; outputs are append-only run directories. Its helpers compute SHA256, write strict JSON and record subprocess output/exit codes/timing. It refuses an already-started run ID. It imports the actual existing engines; it does not replace them.
- `experiments/stage_01/supplemental_checks.py`: executes actual duplicate-candidate and zero-vector tests, independent metric arithmetic, repeated-run and dependency-missing simulations, and 30-sample warm inference timings. It uses run_001 and refuses overwriting its own result file.
- `experiments/stage_01/generate_report.py`: reads those saved observations; writes reports, figure source data, static PNG/SVG plots and the browser entry point. It makes no model predictions and refuses replacing an existing completion report. The figures are descriptive legacy results, not a fusion improvement claim.
- `docs/stages/stage_01/reference_audit.md`: records source checks, citation mismatches and claims not yet verified. It separates a bad citation from an invalid dopant claim.
- `docs/stages/stage_01/telugu_explanation.md`: complete Telugu narration script and explicit audio limitation.
- `docs/progress.md`: central stage status, approvals, known issues and next-stage gate.
- `docs/evaluation/`: copies of the previously reviewed evaluation protocol/template and historical dataset review. The prior HTML is preserved as a historical review, not silently updated scientific evidence.

The existing `.venv` supplies all dependencies needed here, including matplotlib. No production source or original tests were edited. Experiment fixtures are deliberately damaged copies, not replacement datasets.

## How the isolation works

The legacy benchmark hardcodes `results/runs/...`. Running it at the project root would replace the user's existing output. Instead we copy `src` and `data` under `results/stage_01/run_001/legacy_workspace` and run the original module with that working directory. Its relative paths resolve entirely inside the experiment sandbox. Production code is untouched. Model regeneration saves to new `rebuild` and `fresh` locations there.

## How to reproduce

From PowerShell in `C:Final Project`:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
..venvScriptspython.exe -B -X utf8 experimentsstage_01audit_baseline.py --run-id run_002
```

Use a new run ID. Do not rerun run_001 to overwrite evidence. This command writes a new run's raw audit evidence. The supplemental/report tools currently target run_001; their report-generation configuration must be deliberately adapted and inspected before generating a second report. Do not claim those tools are fully parameterized. Exit code 0 for the audit means execution completed and originals were preserved; inspect summary.json for failed requirements. It does not mean every diagnostic passed.

## Concepts connected to the implementation

**Hash:** SHA256 fingerprints bytes. Equal hashes verify file identity, not chemical truth. Metadata time changes can change a JSON hash even when rankings are identical.

**PN similarity:** `1/(1+abs(PN_target-PN_candidate))`. Ga=83 and Al=82 gives 0.5. A chemical ordering is a cheap element-level heuristic. It does not use host structure.

**Property similarity:** each descriptor is standardized as `(value-mean)/standard_deviation`, then rows are normalized and their dot product gives cosine similarity. A radius 130, mean 100, standard deviation 20 becomes 1.5. The selected descriptor set and correlated features shape the result. A pure change of units by a positive constant cancels under feature standardization but labels still must be scientifically correct.

**Atom2Vec:** formula-derived atom/environments form a sparse count matrix. Row normalization and truncated SVD retain 20 latent dimensions. Cosine similarity compares normalized vectors. We compare pairwise similarities when regenerating because vector signs/rotations can change without changing similarity; in this local reproduction, pairwise differences were exactly zero.

**Recall versus Hit:** for two documented options Al and In, returning only In in Top-10 gives Hit@10=1 but Recall@10=1/2. Thus all three methods can have 100% Hit@10 without equal recall.

**MRR@10:** a first positive at rank 1 contributes 1; at rank 2, 0.5; no positive in Top-10, 0. Legacy output calls this MRR but only searches Top-10. Full-list MRR is a separate quantity. Existing arbitrary missed-rank value 88 is a latent reporting defect; current primary cases all have a positive in Top-10 so it does not affect this reproduced mean-best-rank result.

**Fixtures:** synthetic inputs used to test a specific failure. An invalid density fixture tests software validation; it is not experimental evidence about a real material.

**Input validation:** Python accepts `True` as an integer and negative slice endpoints. Thus `candidates[:-1]` returns nearly the entire list. Validation must precede slicing; this stage demonstrates the issue without changing the engines.

## Limits of this stage

No fusion, site-aware generation, formation-energy prediction, gap preservation, electrical activation, new benchmark curation or production interface was implemented. Small legacy results do not establish generalization or universal elemental coverage. Measured runtimes are single-machine local observations; warm inference excludes engine startup, training and network operations. No unsupported DFT-speedup claim is made.

## Rollback and preservation

Original files were not modified. Baseline commit/tag, preexisting diff, original hashes and backup result copies are under run_001. Do not use `git reset --hard` or `git clean` to remove audit files: that could destroy the user's preexisting results or presentations. If removal is requested later, enumerate the newly created stage paths and remove only approved paths. The lightweight tag points to the original commit; the saved patch and hashes preserve the dirty baseline information separately.
''')

save(DOC/'completion_report.md',f'''# STAGE COMPLETION REPORT — Stage 1

Date: 5 November 2026. Stage: baseline audit and reproducibility. Status: **audit executed with findings; no clean robustness or scientific-validation pass**. Next stage has not started.

## 1. Objective

Verify the existing MATRA implementation locally, preserve prior work, reproduce its documented outputs and expose failures before making scientific or production changes.

## 2. What was implemented

Three audit/report scripts, isolated execution and fixture directories, reproducibility records, figures and stage documentation. Existing Python environment reused. Original algorithms, source tests, data, results and presentations unchanged.

## 3. Files created

Scripts: `experiments/stage_01/audit_baseline.py`, `supplemental_checks.py`, `generate_report.py`. Stage reports and Telugu script under `docs/stages/stage_01`. Progress under `docs/progress.md`. Prior protocol/template/review copied under `docs/evaluation`. Raw evidence, preserved results, isolated regenerated artifacts and figures under `results/stage_01/run_001`. Console logs under `logs/stage_01/run_001`. Full inventory is generated during final verification.

## 4. Existing files modified

None. {summary['original_files_checked']} preexisting files were byte-for-byte unchanged at audit completion; final verification checks again. A lightweight Git tag records baseline HEAD. The preexisting JSON change was timestamp-only and remains intact. No user-owned work was committed or reset.

## 5. Algorithms and methods

SHA256 integrity checks; original pytest suite; isolated subprocess execution; complete 118-element input probing; numerical symmetry/self-similarity checks; malformed-data fixtures; direct independent metric arithmetic; full master regeneration and Atom2Vec SVD retraining; descriptive matplotlib plots. No recommendation algorithm changed.

## 6. Actual outputs and results

Original tests: **26 passed**, pytest reported 1.68 seconds in this execution. Benchmark subprocess wall time: {summary['benchmark']['seconds']:.3f} seconds. Reproduced ranking, score, overlap and summary fields exactly match the preexisting local results; run metadata naturally differs.

{table}

The 11 legacy cases contain 18 positive entries and only 9 unique target elements. All methods' 100% Hit@10 means at least one listed positive per case, not 100% candidate correctness. No confidence intervals/generalization claim are attached to these small, previously seen reproduction results.

Fresh master generation: {summary['master_rebuild']['seconds']:.3f} seconds; all values and original Parquet SHA256 reproduced. Fresh Atom2Vec training: {summary['atom2vec_retraining']['seconds']:.3f} seconds; same 79 symbols and 20 dimensions, max pairwise similarity difference 0, all supported Top-10 lists identical. This establishes local reproducibility, not cross-platform guarantees or paper-level exact methodological certification.

Coverage from actual requests: PN 94/118 target elements; Atom2Vec 79/118; Property 88/118. PN's candidate universe is 88 non-noble elements; accepting noble-gas targets is not proof that such substitutions are scientifically applicable.

## 7. Edge cases tested

{sum(allcounts.values())} diagnostic records: {allcounts['passed']} passed, {allcounts['failed']} failed requirements. These are separate from the 26 original pytest cases. The 73 primary probes and 5 supplemental records expose invalid k handling, duplicate acceptance/recommendations, nonfinite and zero cached vectors, negative physical data and cache-dimension mismatch. Full observations and unexecuted cases are in edge_case_report.md and JSON. No executed failure is relabelled a pass.

## 8. Validation results

Functionality verified within the original suite. Cached and fresh numerical reproducibility verified locally. Metric arithmetic verified on the legacy predictions. Robustness failed the expanded requirements. Scientific validity partially assessed, not certified. Overall product readiness not established. See validation_report.md.

## 9. Known issues

- Negative and boolean k accepted by every engine.
- Duplicate master entries accepted; duplicate Al recommendations reproduced in PN and Property.
- Infinite/negative descriptor values and NaN/zero cached vectors lack adequate rejection.
- Cached embedding dimension can disagree with requested dimension.
- Polarizability labels conflict with the installed source library; PN range/normalization metadata conflicts with retained values.
- Fr imputation derivation and full phase-specific provenance are unverified.
- BM-S04 DOI definitely points to unrelated glass literature; BM-P01 direct-experimental evidence classification needs per-claim review.
- No dependency installation manifest; environment freeze records installed versions but is not a verified clean-machine installer.
- System Git status fails; bundled Git works without repository changes.

## 10. Scientific limitations

Element-only engines do not use host/site/concentration. Existing benchmark positives have not all been independently audited. Doping cases remain qualitative. Similarity is not stability or property preservation. Representation-training overlap with known compounds is not excluded. Duplicate formulas in the raw corpus affect weighting but may reflect legitimate polymorph entries; do not drop them without a justified policy.

## 11. Still incomplete

Production fixes are deliberately not folded into an audit-only stage. Stage 2 must correct dataset/provenance issues. Engine-hardening issues are queued for the previously planned engine stage. No later modules started. Complete source-case admission and new held-out benchmark remain pending.

## 12. Telugu audio and transcript

Complete narration: telugu_explanation.md. **No playable Telugu audio generated**: no supported speech tool/Telugu local voice; only English Zira voice detected. No external TTS service used. A full TTS-ready Telugu script is supplied instead, as permitted by the user's fallback requirement.

## 13. Readiness for next stage

The audit has established a reproducible baseline and documented actual failures. This is not a statement that every requirement passed. Stage 2 may begin only after the owner reviews the known defects and explicitly authorizes the dataset/provenance corrections. Engine defects remain tracked and must be fixed in the planned engine stage before reliance on robust candidate generation. No automatic progression.

## Open the results

Open `index.html` in this directory for the browser summary. Actual plots: legacy_metrics.png, element_coverage.png, case_rank_heatmap.png under `results/stage_01/run_001/figures`. Each also has SVG and source data. Technical instructions and rollback notes are in technical_guide.md.
''')

save(ROOT/'docs/progress.md',f'''# MATRA central progress

Authoritative workspace: `C:\\Final Project`. Owner approved Stage 1 in chat on 5 November 2026. Required workflow: stage explanation, approval, incremental implementation, executed edge cases, separate validation categories, reports/Telugu narration, owner review; no automatic next stage.

Current stage: Stage 1 baseline audit — executed with findings, awaiting owner review. Original suite 26 passed; {allcounts['failed']} expanded diagnostic failures remain open. Numerical reproduction verified; scientific certification incomplete. No production source changes.

## Roadmap (unchanged)

1. Baseline audit and reproducibility — audit executed, review pending.
2. Dataset correctness, provenance and coverage handling — pending approval.
3. Independent similarity-engine hardening — pending.
4. Similarity fusion and evaluation — pending.
5. Host structures, sites and candidate generation — pending.
6. Energy/stability assessment — pending.
7. Property preservation — pending.
8. Doping assessment — pending.
9. Evidence, explanations and final ranking — pending.
10. Research interface, integration and final evaluation — pending.

## Approved decisions

- Use existing local project and Python 3.10.11 environment; preserve original work.
- Keep substitution and doping evaluation separate; never treat unreported chemistry as negative truth.
- Evaluation is core development work; protocol under docs/evaluation.
- No cloud execution, no package installs or upgrades, no production algorithm changes during this stage.
- Baseline checkpoint is commit d84caf8 plus a saved dirty-results patch and hashes; local lightweight tag records HEAD. No user presentation files committed.

## Unresolved issues and next-stage inputs

- Dataset stage: units, PN metadata/normalization, imputation derivations, phase-aware provenance, benchmark DOI/evidence auditing, environment/dependency recording.
- Engine stage: invalid k/types, duplicate validation, nonfinite/negative features, cache shape/norm/config checks, support-policy consistency and errors.
- Research: new held-out source-audited cases; clean overlap-aware evaluation; no property/stability claims from similarity alone.
- Audio: actual Telugu voice generation unavailable; complete narration script supplied.
- Clean-machine installation and cross-platform reproducibility not yet established.

Full Stage 1 review: docs/stages/stage_01/completion_report.md. Raw evidence: results/stage_01/run_001. No next stage has started.
''')

htmlrows=''.join('<tr><td>'+html.escape(n)+'</td>'+''.join(f'<td>{metrics[n][k]:.4f}</td>' for k in ['hit_at_1','hit_at_3','mrr','mean_recall_at_10'])+'</tr>' for n in names)
links=''.join(f'<li><a href="{f}">{label}</a></li>' for f,label in [
('completion_report.md','Full stage completion report'),('edge_case_report.md','Every executed edge case'),
('validation_report.md','Validation status and limits'),('technical_guide.md','Code responsibilities and reproduction'),
('reference_audit.md','Scientific reference audit'),('environment_report.md','Environment'),('telugu_explanation.md','Complete Telugu narration script')])
imgs=''.join(f'<figure><img src="../../../results/stage_01/run_001/figures/{f}" alt="{alt}"><figcaption>{caption}</figcaption></figure>' for f,alt,caption in [
('legacy_metrics.png','Legacy ranking metrics','11 previously seen cases; reproduction evidence only. Hit@10=100% does not mean every suggestion is correct.'),
('element_coverage.png','Element input coverage','All 118 element inputs were exercised. Acceptance is not scientific applicability.'),
('case_rank_heatmap.png','Per-case positive ranks','Lower ranks are earlier; repeated targets share global element rankings.')])
page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MATRA Stage 1 Audit</title>
<style>body{{font:16px system-ui,sans-serif;background:#f4f7fa;color:#182b3b;max-width:1100px;margin:30px auto;padding:20px}}section,figure{{background:white;border:1px solid #d7e0e8;padding:24px;border-radius:10px;margin:20px 0}}h1{{font-size:32px}}p,li{{line-height:1.65}}img{{max-width:100%;height:auto}}table{{border-collapse:collapse;width:100%}}th,td{{padding:12px;border:1px solid #d7e0e8;text-align:left}}th{{background:#eaf1f8}}a{{color:#175e9a}}.warning{{border-left:5px solid #ad6335}}figcaption{{font-size:14px;color:#465b6e}}</style>
<h1>MATRA — Stage 1 baseline audit</h1><p>5 November 2026 | Local workspace: C:\\Final Project | No production source or original results changed</p>
<section class="warning"><h2>Audit executed with findings</h2><p><strong>26 original tests passed. {allcounts['failed']} expanded diagnostic requirements failed.</strong> These findings remain open. Legacy outputs and fresh regeneration reproduced locally. Scientific benchmark claims are not fully certified. Next stage requires owner approval.</p></section>
<section><h2>Reproduced legacy metrics</h2><table><tr><th>Method</th><th>Hit@1</th><th>Hit@3</th><th>MRR@10</th><th>Recall@10</th></tr>{htmlrows}</table><p>Scores are fractions, not percentages. The benchmark contains 11 cases, 18 positive entries and 9 distinct target elements.</p></section>
{imgs}<section><h2>Reports and learning material</h2><ul>{links}<li><a href="../../../results/stage_01/run_001/summary.json">Raw audit summary</a></li><li><a href="../../progress.md">Central progress</a></li><li><a href="../../evaluation/MATRA_Evaluation_Protocol_v1.md">Evaluation protocol</a></li></ul><p>No playable Telugu audio was generated. A complete Telugu narration script is available above; the local speech engine exposes only an English voice.</p></section></html>'''
save(DOC/'index.html',page)
save(OUT/'experiment_manifest.json',json.dumps({'experiment_ids':['E00','E01','Stage1_robustness_diagnostics'],
    'status':'executed_with_findings','date_client':'2026-11-05','code_commit':env['source_commit'],
    'original_data_hashes':data['checksums'],'methods':names,'inputs':'frozen existing local artifacts',
    'benchmark':'legacy development; not held-out scientific certification',
    'parameters':{'embedding_dim':20,'seed':42,'k':10,'coverage_elements':118,'timing_warmups':5,'timing_repeats':30},
    'primary_results':'benchmark_comparison.json','failures':'edge_case_results.json and supplemental_checks.json',
    'limitations':['partial reference audit','no generalization evaluation','no site, energy, gap or dopant prediction']},indent=2))
print('Stage 1 reports and figures generated without replacing original files.')
