"""Create local, inspectable Stage 2 reports from executed source/test records."""
from pathlib import Path
from collections import Counter
import html
import json
import os
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
OUT=ROOT/'results/stage_02/run_001';DOC=ROOT/'docs/stages/stage_02'
if (DOC/'completion_report.md').exists():raise FileExistsError('Reports already exist')
os.environ['MPLCONFIGDIR']=str(OUT/'matplotlib_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.data_audit.schema import FEATURES
from src.data_audit.validation import load_json,validate_elements,validate_registry,validate_benchmark

def write(path,text):
    with path.open('x',encoding='utf-8') as f:f.write(text)
def table(df):return '<div class="scroll">'+df.to_html(index=False,escape=True,na_rep='Missing',float_format=lambda x:f'{x:.6g}')+'</div>'
def jsontext(value):return json.dumps(value,ensure_ascii=False,indent=2)

data=ROOT/'data/processed/v2_0_0';benchdir=ROOT/'data/benchmark/v2_0_0'
frame=pd.read_parquet(data/'elements_native.parquet')
registry=load_json(data/'element_registry.json');fit=load_json(data/'radius_estimates.json')
metadata=load_json(data/'feature_metadata.json');benchmark=load_json(benchdir/'benchmark_review.json')
provenance=[json.loads(line) for line in (data/'cell_provenance.jsonl').read_text(encoding='utf-8').splitlines()]
checks={'native':validate_elements(frame,provenance,registry),'registry':validate_registry(registry),'benchmark':validate_benchmark(benchmark)}
cases=benchmark['substitution_cases']+benchmark['doping_cases']
status=Counter(c['claims'][0]['review_status'] for c in cases)
rootxml=ET.parse(OUT/'final_tests.xml').getroot()
testcases=rootxml.findall('.//testcase');failures=rootxml.findall('.//failure')+rootxml.findall('.//error')
newtests=[c for c in testcases if 'stage_02' in c.attrib['classname']]
testcounts={'total':len(testcases),'stage_02':len(newtests),'legacy':len(testcases)-len(newtests),'failed':len(failures)}
plt.rcParams.update({'font.size':10,'font.family':'DejaVu Sans'})
figdir=OUT/'figures';figdir.mkdir()

missing=frame[list(FEATURES)].isna().sum();missing=missing[missing>0]
fig,ax=plt.subplots(figsize=(10,4.6),layout='constrained')
ax.barh(['Pauling electronegativity','Native atomic radius','Thermal conductivity'],missing.to_numpy(),color=['#2864a5','#bb7534','#25877b'])
for i,n in enumerate(missing):ax.text(n+.08,i,str(n),va='center')
ax.set_xlim(0,6);ax.set_xlabel('Missing cells retained (not zero-filled)')
ax.set_title('Native release: 9 known gaps among 1,316 feature cells\n5 radius estimates are separate; unsupported Fr conductivity remains missing')
ax.spines[['top','right']].set_visible(False)
fig.savefig(figdir/'native_missingness.png',dpi=170);fig.savefig(figdir/'native_missingness.svg');plt.close(fig)

train=frame.dropna(subset=['atomic_radius_slater_pm']);x=train.covalent_radius_cordero_pm.to_numpy();y=train.atomic_radius_slater_pm.to_numpy()
fig,ax=plt.subplots(figsize=(8.5,5.8),layout='constrained')
ax.scatter(x,y,s=22,color='#2864a5',alpha=.7,label='89 source-library radius pairs')
grid=np.linspace(min(x),max(x),100);ax.plot(grid,fit['slope']*grid+fit['intercept_pm'],color='#25877b',label='OLS fitted line')
for i,estimate in enumerate(fit['estimates']):
    ex=frame.set_index('symbol').loc[estimate['symbol'],'covalent_radius_cordero_pm'];ey=estimate['estimated_atomic_radius_slater_pm']
    ax.scatter([ex],[ey],marker='x',s=65,color='#bb7534',label='Separate estimates (unvalidated)' if i==0 else None)
    ax.annotate(estimate['symbol'],(ex,ey),xytext=(5,6 if i%2 else -12),textcoords='offset points',fontsize=9)
ax.set_xlabel('Cordero covalent radius (pm)');ax.set_ylabel('Slater atomic radius (pm)')
ax.set_title(f"Radius estimation audit — training R²={fit['training_r2']:.3f}\nLeave-one-element-out MAE={fit['leave_one_element_out_mae_pm']:.2f} pm; no validated error for missing elements")
ax.legend(loc='upper left',fontsize=9);ax.spines[['top','right']].set_visible(False)
fig.savefig(figdir/'radius_estimation.png',dpi=170);fig.savefig(figdir/'radius_estimation.svg');plt.close(fig)

keys=['citation_mismatch','unresolved_identifier','partial_support','review_source']
fig,ax=plt.subplots(figsize=(9,4.8),layout='constrained')
values=[status[k] for k in keys];labels=['Citation mismatch','Identifier unresolved','Partial topic support','Review source']
ax.bar(labels,values,color=['#b35443','#bb7534','#358c8b','#527fa8'])
for i,n in enumerate(values):ax.text(i,n+.1,str(n),ha='center')
ax.set_ylim(0,7);ax.set_ylabel('Legacy case entries (16 total)')
ax.set_title('Evidence triage — none admitted yet to strict contextual evaluation\nThis classifies supporting records, not chemical truth or model accuracy')
ax.spines[['top','right']].set_visible(False)
fig.savefig(figdir/'benchmark_evidence_status.png',dpi=170);fig.savefig(figdir/'benchmark_evidence_status.svg');plt.close(fig)

reviewrows=[]
for c in cases:
    r=c['claims'][0]
    reviewrows.append({'case_id':c['case_id'],'track':c['track'],'host':c['legacy_record']['formula'],
        'target':c['legacy_record']['target_element'],'candidates':', '.join(v['candidate'] for v in c['claims']),
        'legacy_doi':r['legacy_doi'],'resolved_title':'; '.join(r['resolved_titles']) or 'Unresolved in queried registry',
        'status':r['review_status'],'eligible':False,'reason':r['review_reason']})
write(OUT/'benchmark_case_review.json',jsontext(reviewrows))
write(OUT/'figure_data.json',jsontext({'missing_cells':missing.to_dict(),'radius_fit':fit,'benchmark_case_status_counts':dict(status),
    'statement':'Diagnostic data-quality results, not new prediction accuracy.'}))
summary={'checks':checks,'tests':testcounts,'native_shape':list(frame.shape),'native_complete_elements':int((frame.native_feature_count==14).sum()),
    'missing_cells':int(frame[list(FEATURES)].isna().sum().sum()),'case_review_status_counts':dict(status),
    'radius_training_r2':fit['training_r2'],'radius_loo_mae_pm':fit['leave_one_element_out_mae_pm'],
    'production_engines_modified':False,'scientific_benchmark_ready':False,'audio_generated':False}
write(OUT/'summary.json',jsontext(summary))

testtable='| Executed test | Result |\n|---|---|\n'
for c in newtests:
    passed=c.find('failure') is None and c.find('error') is None
    testtable+='| '+c.attrib['name'].replace('|','/')+' | '+('passed' if passed else 'failed')+' |\n'
write(DOC/'edge_case_report.md',f'''# Stage 2 executed edge-case report

Final suite: {testcounts['total']} passed; {testcounts['stage_02']} new tests plus {testcounts['legacy']} legacy tests. Each row below is an actually executed pytest record. Logs and JUnit XML are under results/stage_02/run_001 and logs/stage_02/run_001.

{testtable}

## Boundaries

The initial run had 43 new tests; a later 70-test run added persisted-artifact reproduction; the final 73-test run also added boolean feature-count and invalid benchmark symbol/target checks. Earlier logs are preserved. No final failing test was hidden.

Dependency consistency was checked with pip check: no broken requirements found. Five unique DOI queries returned HTTP 404; these are recorded source-resolution failures, not positive test results or proof that the referenced chemistry is impossible. Responses and error details are cached.

Not tested: physical disk-full/access-denied interruption, concurrent release writers, every malformed nested JSON shape, live DOI-service outage recovery beyond recorded request errors, clean-machine installation, cross-platform regeneration, and chemistry correctness of every property/reference. The new validators protect the new data pipeline; the legacy engines still retain Stage 1 robustness defects for Stage 3.
''')

write(DOC/'dataset_guide.md',f'''# Stage 2 dataset guide — release 2.0.0-audit

This release is additive. Original data, results and engines remain unchanged. The suffix `audit` means the data lineage and review state are explicit; it does not certify all properties as measurements or the benchmark as scientific ground truth.

## What is stored and why

| File | Purpose |
|---|---|
| data/raw/stage_02_sources/source_snapshot.json | Captured pinned-library values, selected fallback sources, source property metadata, 118-element registry source and warnings; offline rebuild input |
| data/raw/stage_02_sources/doi_lookup.json and DOI files | Raw registry responses and resolution outcomes; bibliographic checks only |
| data/processed/v2_0_0/elements_native.parquet | 94-element native/explicitly derived feature table; nine source gaps retained |
| data/processed/v2_0_0/cell_provenance.jsonl | One source/origin/unit/value record for every one of the 1,316 feature cells |
| data/processed/v2_0_0/element_registry.json | Recognizes all 118 elements; reports native-feature availability and legacy engine support separately |
| data/processed/v2_0_0/feature_metadata.json | Correct units, PN convention, source annotations, scope and source hashes |
| data/processed/v2_0_0/radius_estimates.json | Optional estimated radii, fit coefficients and leave-one-out diagnostics; not merged into native table |
| data/processed/v2_0_0/release_manifest.json | Versioned artifact hashes and explicit nonactivation in old engines |
| data/benchmark/v2_0_0/benchmark_review.json | All original 16 cases retained inside a claim-level review ledger; no unsupported evaluation credit |

## Four important corrections

1. Polarizability is stored in the source's bohr^3 convention. Existing numeric values are not falsely relabelled Angstrom^3 and no unnecessary conversion is performed.
2. PN source metadata cites Pettifor1984/Villars2004 with a source extension to all elements. The new convenience field is PN/118. Its name identifies the denominator; the old PN/103 field remains only in legacy data. Source agreement is not a complete historical rederivation of every published PN convention.
3. Density follows documented source conditions, with gases and theoretical estimates. Upstream At/Fr density estimates and derived volumes are flagged. None are promoted to experimentally verified measurements.
4. The derived volume is atomic weight divided by source density, in cm^3/mol atoms. It is not uniformly a condensed-solid molar volume. Source phase/temperature context must travel with it.

## Imputation explained

Native values are not project-imputed. Three Pauling gaps, five radius gaps and one Fr conductivity gap remain. The regression line for radius uses 89 observed source pairs. Slope={fit['slope']:.9f}; intercept={fit['intercept_pm']:.9f} pm. Training R²={fit['training_r2']:.6f}; leave-one-element-out MAE={fit['leave_one_element_out_mae_pm']:.6f} pm, RMSE={fit['leave_one_element_out_rmse_pm']:.6f} pm. These are executed diagnostics, not validation of missing-element estimates. The old reported R²=0.963 is not supported by this executed fit. No prediction intervals are claimed.

An upstream source estimate and a project imputation are different. Storing a library value does not imply it was measured experimentally. Cell provenance explicitly says independent measurement classification has not been completed.

## Feature dictionary

'''+ '\n'.join(f'- `{k}`: **{u}**. {description}.' for k,(u,description) in FEATURES.items())+'''

## Benchmark rules

Every case is retained for traceability. Unknown chemistry is not a negative label. A matching DOI/title is not enough to verify host, phase, site, concentration and property behavior. The current strict contextual benchmark has zero eligible claims; no revised scientific accuracy figure is produced. Legacy results remain reproducible as legacy diagnostics.

Six case entries have a definite citation/topic mismatch in resolved metadata; five have unresolved identifiers, four have partial topic support and one relies on a review. These counts are case-level; the review contains 23 candidate assertions in total. Complete experimental/DFT passage extraction remains a research task. Do not display original blanket EXPERIMENTAL_DIRECT labels as newly verified truth.
''')

write(DOC/'implementation_guide.md',r'''# Stage 2 code and reproduction guide

## File responsibilities

- `src/data_audit/schema.py`: authoritative unit-explicit feature names, legacy-name mapping, expected native gaps for the pinned release, and upstream-density estimate flags. This is a new data contract, not a recommendation model.
- `src/data_audit/validation.py`: checks identities, dimensions, units, finiteness, bounds, provenance equality, missingness, registry truthfulness and benchmark admission. It raises DataValidationError. A data-validation pass establishes contract consistency, not chemical truth.
- `src/data_audit/release.py`: reads frozen local source snapshots, prepares native data/provenance, fits separately stored radius estimates, creates the coverage registry and evidence-review ledger, validates in memory, and writes only into empty versioned output directories. No existing engines are modified or redirected.
- `experiments/stage_02/collect_sources.py`: captures actual pinned-library values and DOI metadata. It reads existing feature conventions and records warnings. HTTPS requests fetch bibliographic data; all execution and storage are local. It is not a literature-truth oracle. The source snapshot and network records are intentionally frozen after capture.
- `tests/stage_02/test_data_release.py`: actual new tests for scientific units, native missingness, provenance, estimates, registry scope, admission controls, corrupt inputs, reproducibility and overwrite/path safeguards.
- `experiments/stage_02/build_reports.py`: reads completed artifacts and tests, builds plots, full native/registry/provenance viewer, stage reports and final review summary. It refuses replacing an existing completion report.
- `experiments/stage_02/verify_release.py`: final data checks, hashes, report links, code compilation and Git status capture. It runs after report generation.

The preexisting source builder/tests are preserved as a reproducible legacy baseline; their known wrong comments are superseded by the versioned release documentation, not silently rewritten.

## How to run

In PowerShell at `C:Final Project`, rebuild to NEW empty locations:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
..venvScriptspython.exe -B -X utf8 -m src.data_audit.release `
  --data-output results/stage_02/rebuild_002/native `
  --benchmark-output results/stage_02/rebuild_002/benchmark
```

The offline release rebuild uses source_snapshot.json and cached DOI metadata. It does not need network. All paths are resolved and must stay inside the project root. The existing versioned release is intentionally not replaceable. To rerun tests, choose a NEW basetemp and log/output location so evidence is preserved. The exact executed final command is in logs/stage_02/run_001/final_tests.txt and the experiment manifest.

Dependencies reuse the existing Python 3.10.11 environment; no packages were installed or upgraded. environment_freeze.txt records observations, not a verified clean-machine installation recipe. pip check passed.

## Why the engines still use legacy data

The native table has explicit units in its field names and genuine missing values. Automatically switching the old 14-feature engine would either fail or hide a new imputation policy. Stage 3 must explicitly decide support and missing-data behavior and compare any resulting ranking changes. No silent change to inference is made here.

## Reproducibility and rollback

The source snapshot and emitted tables, registry, provenance, estimates and benchmark ledger reproduce exactly in the persisted-artifact tests. Release timestamps are administrative metadata and may change for a newly created release. No live API response is assumed permanent.

Original tracked files are protected by starting hashes and a saved diff. The Stage 2 baseline tag is matra-stage-02-baseline-20261105. The previous progress document is backed up in results/stage_02/run_001/progress_before.md. Restoring the legacy workflow requires no data migration because its paths and engines were not changed. Do not use git clean/reset to remove reports: it could destroy user-owned untracked presentations.
''')

write(DOC/'validation_report.md',f'''# Stage 2 validation status

| Category | Status | Evidence / limitation |
|---|---|---|
| Data-release functionality | Verified | {testcounts['stage_02']} new tests passed |
| Legacy regression | Verified | {testcounts['legacy']} existing tests passed |
| Source-value preservation | Verified | Every native cell compared with captured source snapshot |
| Units/source conventions | Verified against pinned library metadata | Source metadata and explicit names stored; individual measurements not independently certified |
| Radius-estimate reproducibility | Verified | 89 training pairs, coefficients, LOO diagnostics; not mixed with native values |
| Missingness honesty | Verified | Nine gaps preserved; no unsupported Fr conductivity |
| Full element recognition | Verified | 118 registry rows; only 94 native-feature rows, no invented extra vectors |
| Claim admission safeguards | Verified | Unknowns cannot earn credit; source/condition checks enforced |
| Benchmark chemical validity | **Not yet verified** | 0 strict contextual claims admitted; primary passage/site/concentration curation remains |
| Reproducibility | Verified locally | Frozen inputs regenerate emitted native table, provenance, estimates, registry and ledger |
| Dependencies | Consistency check passed | pip check reports no broken requirements; clean machine not tested |
| Original file preservation | Final hash check recorded separately | Original tracked files must match Stage 2 starting hashes |
| Production engine robustness | Unchanged / not fixed here | Stage 1 defects remain queued for Stage 3 |
| Band-gap, stability and doping effectiveness | Not assessed | Later modules; DOI metadata is not scientific evidence for effectiveness |

Engineering deliverables are complete within scope. The scientific benchmark remains withheld. Do not characterize this stage as a fully verified substitution benchmark or use the new release to claim improved accuracy.
''')

write(DOC/'completion_report.md',f'''# STAGE COMPLETION REPORT — Stage 2

Date: 5 November 2026. **Data engineering implemented and tested; scientific benchmark admission remains incomplete.** No Stage 3 work has begun.

## 1. Objective

Correct units/conventions, record data lineage and estimates, establish honest all-element coverage, and prevent unsupported benchmark assertions from earning quantitative credit.

## 2. What was implemented

An additive versioned data release, native/estimate separation, cell-level provenance, 118-element registry, full legacy-case evidence triage, validation/admission rules, tests, figures and inspectable viewer. Execution is local in C:/Final Project.

## 3. Files created

New modules under src/data_audit, tests under tests/stage_02, scripts under experiments/stage_02, captured local/registry sources under data/raw/stage_02_sources, release under data/processed/v2_0_0 and data/benchmark/v2_0_0. Reports/transcript under docs/stages/stage_02; results/figures/logs under their stage_02/run_001 locations. The final verification record includes an inventory.

## 4. Files modified

Only the central docs/progress.md is intentionally updated; its prior version is backed up. Original tracked source, datasets, tests, results and prior reports are unchanged. Git metadata records the Stage 2 baseline checkpoint; no user changes are reset or broadly staged.

## 5. Algorithms and methods

Pinned-library extraction; Crossref/DataCite bibliographic resolution; strict numeric/provenance validation; OLS radius regression with leave-one-element-out checks; claim-level eligibility gating; immutable versioned outputs; hashes and pytest.

## 6. Actual outputs and results

- Native feature table: **94 rows, 14 features, 1,316 provenance records**, nine missing cells across eight elements.
- Fully populated native rows: **{summary['native_complete_elements']}**. Completeness does not mean every upstream value is experimental.
- Element registry: **118 recognized**, no invented physical vectors beyond the 94-element scope.
- Radius estimation: 89 known pairs, R²={fit['training_r2']:.6f}, LOO MAE={fit['leave_one_element_out_mae_pm']:.6f} pm. Five estimates stored separately.
- Case review: **6 citation mismatches, 5 unresolved identifiers, 4 partially related sources, 1 review source**. All 16 legacy records and 23 assertions preserved.
- Strict contextual benchmark eligibility: **0 claims**. This is an evidence-admission result, not proof that the chemistry is false. No new scientific accuracy score is reported.
- Final test suite: **{testcounts['total']} passed** ({testcounts['stage_02']} new + {testcounts['legacy']} legacy); zero failures. pip check passed.

## 7. Edge cases tested

Empty/duplicate/missing/incorrectly typed tables; wrong symbols/Z/PN/normalization; negative/infinite/missing data; nonintegral electron counts; provenance and unit mismatch; registry overclaims; invalid benchmark labels/admission/track mixing; JSON errors; output traversal and overwrite refusal; frozen-source/persisted-artifact reproduction. Full executed list and unexecuted cases: edge_case_report.md.

## 8. Validation results

Data engineering and reproducibility verified within the local tested environment. Library convention alignment verified from captured source metadata. Benchmark scientific validity not certified. No property preservation or stability conclusion established. Details: validation_report.md.

## 9. Known issues

Correct primary references and full contextual evidence are still required. A registry HTTP 404 is not a universal invalid-DOI determination. Metadata classification is manual and tied to captured responses, not an automated semantic truth model. Stored source values can contain upstream estimates and uncertainty. The legacy engines still have Stage 1 input/cache defects.

## 10. Scientific limitations

No entire benchmark family is declared experimentally valid based on title matching. No new experimental data were obtained. No missing-element estimate has independent ground truth. 118-element recognition does not establish substitution capability for all combinations. No prospective/held-out predictive validation yet.

## 11. Still incomplete

Primary-source passage extraction and full site/concentration admission; clean-machine installation; Stage 3 missing-data policy and engine fixes; all subsequent scientific and interface modules. The benchmark is deliberately inactive for validated accuracy claims.

## 12. Telugu audio and transcript

Complete narration: telugu_explanation.md. Actual Telugu audio not generated: no suitable local voice/tool; external TTS not used. Transcript is provided as the agreed fallback, not described as a playable file.

## 13. Readiness for next stage

Review the engineering release and the unresolved evidence work separately. Recommended scientific next action is continued primary-source curation within Stage 2. Proceeding to Stage 3 with the benchmark withheld would require the owner's informed approval; it would permit engineering work, not validated accuracy claims. No automatic transition.

Open index.html for full data, source registry, claim ledger, graphs, reports and machine-readable files. Plots are quality diagnostics, not new model performance comparisons.
''')

css='body{font:15px system-ui,sans-serif;background:#f5f8fb;color:#172b3c;margin:28px}section{background:white;border:1px solid #d8e1e9;padding:22px;border-radius:10px;margin:22px 0}h1{font-size:30px}p,li{line-height:1.65;max-width:1100px}.scroll{overflow:auto;max-height:650px}table{border-collapse:collapse;font-size:12px}td,th{padding:9px;border:1px solid #dce3ea;text-align:left;white-space:nowrap}th{position:sticky;top:0;background:#eaf1f8}tr:nth-child(even){background:#f7f9fc}img{max-width:100%;max-height:760px}a{color:#175e9a}.hold{border-left:5px solid #b35443}pre{white-space:pre-wrap}details{margin:15px 0}'
def sec(title,body,cls=''):return f'<section class="{cls}"><h2>{title}</h2>{body}</section>'
links=''.join(f'<li><a href="{f}">{label}</a></li>' for f,label in [('completion_report.md','Stage completion report'),('dataset_guide.md','Dataset guide and feature definitions'),('implementation_guide.md','Code responsibilities and reproduction'),('edge_case_report.md','Executed edge cases'),('validation_report.md','Validation status'),('telugu_explanation.md','Complete Telugu narration script')])
charts=''.join(f'<figure><img src="../../../results/stage_02/run_001/figures/{f}" alt="{name}"><figcaption>{name}</figcaption></figure>' for f,name in [('native_missingness.png','Known missingness; not model errors'),('radius_estimation.png','Source-pair fit with separate, unvalidated estimates'),('benchmark_evidence_status.png','Reference triage, not chemical truth')])
featuretable=pd.DataFrame([{'feature':k,'unit':v[0],'meaning':v[1]} for k,v in FEATURES.items()])
page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MATRA Stage 2 data review</title><style>'+css+'</style><h1>MATRA — Stage 2 data and evidence review</h1><p>5 November 2026 | Local release 2.0.0-audit | Original data and engines preserved</p>'
page+=sec('Important: scientific benchmark not yet admitted',f'<p><strong>73 tests passed; zero strict contextual benchmark claims are currently eligible.</strong> These statements answer different questions. The pipeline safeguards work, while the original scientific evidence needs repair and passage-level review. Unknown claims are not negative chemistry.</p>','hold')
page+=sec('Reports and narration','<ul>'+links+'</ul><p>No playable Telugu audio was generated; full narration text is available.</p>')
page+=sec('Executed data-quality results',charts)
page+=sec('Full feature dictionary',table(featuretable))
page+=sec('Full native element table — all 94 rows',table(frame))
page+=sec('All-element registry — all 118 records',table(pd.DataFrame(registry)))
page+=sec('All 16 legacy case reviews',table(pd.DataFrame(reviewrows)))
page+=sec('All 1,316 feature-cell provenance records',table(pd.DataFrame(provenance).map(lambda x:json.dumps(x,ensure_ascii=False) if isinstance(x,(list,dict)) else x)))
page+=sec('Machine-readable records','<ul><li><a href="../../../data/processed/v2_0_0/feature_metadata.json">Feature metadata and original source annotations</a></li><li><a href="../../../data/processed/v2_0_0/radius_estimates.json">Separate radius fit and estimates</a></li><li><a href="../../../data/benchmark/v2_0_0/benchmark_review.json">Complete claim-level review with original records</a></li><li><a href="../../../data/raw/stage_02_sources/doi_lookup.json">DOI response index</a></li><li><a href="../../../results/stage_02/run_001/summary.json">Executed results summary</a></li><li><a href="../../progress.md">Central progress</a></li></ul>')
write(DOC/'index.html',page+'</html>')
write(OUT/'experiment_manifest.json',jsontext({'stage':2,'experiment':'E00 data/provenance correction and claim triage',
    'scope':'engineering and source audit; no new predictive benchmark','source_versions':metadata['source_versions'],
    'source_snapshot_sha256':metadata['source_snapshot_sha256'],'parameters':{'feature_scope':[1,94],'registry_scope':[1,118],
    'pn_denominator':118,'project_imputation_in_native':False,'radius_fit':'OLS, 89 source pairs','radius_validation':'leave-one-element-out'},
    'results':summary,'limitations':['0 strict contextual claims admitted','primary scientific curation remains','legacy engines unchanged'],
    'execution':'Python 3.10.11 local Windows environment; cached registry responses for offline rebuild'}))
print(jsontext(summary))
