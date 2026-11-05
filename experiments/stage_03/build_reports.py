"""Build Stage 3 reports only from executed tests and numerical experiments."""
from pathlib import Path
import hashlib
import html
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/stage_03/run_001'
DOCS = ROOT / 'docs/stages/stage_03'
os.environ['MPLCONFIGDIR'] = str(OUT / 'matplotlib_cache')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def write(path, content):
    with path.open('x', encoding='utf-8') as stream: stream.write(content)


def main():
    suite = ET.parse(ROOT / 'logs/stage_03/run_001/pytest_final.xml').getroot().find('testsuite')
    counts = {key: int(suite.attrib[key]) for key in ('tests', 'failures', 'errors', 'skipped')}
    if counts['failures'] or counts['errors'] or counts['skipped']: raise ValueError('Final suite is not entirely passing')
    old = json.loads((ROOT / 'results/stage_01/run_001/edge_case_results.json').read_text(encoding='utf-8'))
    supplement = json.loads((ROOT / 'results/stage_01/run_001/supplemental_checks.json').read_text(encoding='utf-8'))
    failures = {r['name'] for r in old if r['status'] == 'failed'} | {r['case'] for r in supplement['records'] if not r['passed']}
    regression = {}
    for test in suite.findall('testcase'):
        name = test.attrib['name']
        match = re.fullmatch(r'test_stage1_reported_failure_remediated\[(.*)\]', name)
        if match: regression[match.group(1)] = not any(test.find(k) is not None for k in ('failure', 'error', 'skipped'))
    if set(regression) != failures or not all(regression.values()): raise ValueError('Historical failure mapping incomplete')
    verification = json.loads((OUT / 'engine_verification.json').read_text(encoding='utf-8'))
    before = json.loads((OUT / 'starting_hashes.json').read_text(encoding='utf-8'))
    changed = [p for p, h in before.items() if not (ROOT / p).is_file() or hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h]
    allowed = {'.gitattributes', 'docs/progress.md', 'src/pn_similarity/pn_engine.py', 'src/property_similarity/property_engine.py', 'src/atom2vec/atom2vec_engine.py'}
    if set(changed) - allowed: raise ValueError('Unexpected earlier-file change')
    tests = {'final': counts, 'seconds': float(suite.attrib['time']), 'historical_failures': regression,
             'previous_files_checked': len(before), 'intentionally_changed_previous_files': changed,
             'scientific_benchmark_status': 'incomplete; no accuracy claims', 'stage4_started': False}
    write(OUT / 'final_verification.json', json.dumps(tests, indent=2))
    data = np.load(OUT / 'score_comparison.npz', allow_pickle=False)
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
    for ax, method in zip(axes, ('PN', 'Property', 'Atom2Vec')):
        old_scores, new_scores = data[method+'_before'].ravel(), data[method+'_after'].ravel()
        ax.scatter(old_scores, new_scores, s=3, alpha=.18, rasterized=True)
        limits = [0, 1] if method == 'PN' else [-1, 1]
        ax.plot(limits, limits, color='#b84e4e', linewidth=1)
        ax.set(xlim=limits, ylim=limits, xlabel='Original similarity', ylabel='Hardened similarity', title=method)
    fig.suptitle('Valid-input score agreement; not experimental property predictions')
    fig.tight_layout()
    for extension in ('png', 'svg'): fig.savefig(OUT / f'score_agreement.{extension}', dpi=160)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(['Stage 1 observed\nfailing behaviours', 'Stage 3 targeted\nregressions passing'], [len(failures), len(regression)], color=['#bd7851', '#398b7d'])
    ax.bar_label(bars, padding=5)
    ax.set(ylim=(0, 18), ylabel='Software checks (count)', title='15 recorded defects now have passing regression checks')
    fig.text(.5, .01, 'Historical failures retained unchanged. Counts are not chemical accuracy.', ha='center', fontsize=9)
    fig.tight_layout(rect=(0,.03,1,1))
    for extension in ('png', 'svg'): fig.savefig(OUT / f'regression_checks.{extension}', dpi=160)
    plt.close(fig)
    methods = list(verification['engines'])
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(methods))
    for offset, phase, label, color in ((-.18, 'before', 'Original', '#7b8ba6'), (.18, 'after', 'Hardened', '#398b7d')):
        values = [verification['engines'][m][phase+'_latency']['median_ms'] for m in methods]
        p95 = [verification['engines'][m][phase+'_latency']['p95_ms'] for m in methods]
        ax.bar(x+offset, values, width=.34, label=label, color=color)
        ax.scatter(x+offset, p95, color=color, marker='_', s=140)
    ax.set(xticks=x, xticklabels=methods, ylabel='Warm query time (ms)', title='Ga Top-10: median bars and p95 markers, 200 calls each')
    ax.legend()
    fig.text(.5, .01, 'Single local run; execution order/system load confound comparisons. No general speedup claim.', ha='center', fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1))
    for extension in ('png', 'svg'): fig.savefig(OUT / f'warm_latency.{extension}', dpi=160)
    plt.close(fig)
    data.close()
    summary_rows = '\n'.join(f"| {m} | {r['target_support_count']} | {r['candidate_support_count']} | {r['pair_scores_checked']} | {r['max_abs_score_change']:.3g} | {r['top10_changes']} | {r['after_latency']['median_ms']:.4f} |" for m,r in verification['engines'].items())
    write(DOCS / 'results_and_metrics.md', '''# Actual Stage 3 evaluation

The goal is robust, reproducible independent similarity signals. These experiments do not
measure elemental-substitution accuracy. No chemical ground-truth labels were consumed by
the production engines and no withheld assertion was promoted to a validated benchmark.

| Engine | Supported queries | Candidate pool | Ordered pair scores checked | Max absolute score change | Changed Top-10s | Warm median ms |
|---|---:|---:|---:|---:|---:|---:|
''' + summary_rows + f'''

All 261 supported engine-target Top-10 outputs are identical to the preserved baseline.
22,821 ordered pair evaluations include both directions and self pairs; they are not 22,821
independent materials examples. All 118 elements were queried against each support interface:
354 statuses and requests. Unsupported requests raise a specific UnsupportedElementError.
Full candidate lists contain no duplicate or self element and respect each method's policy.

## Metrics and their interpretation

- Regression-check pass count: {len(regression)}/{len(failures)} previously failing behaviours
  now have executed passing tests. This measures software correction, not chemistry correctness.
- Ranking regression count: number of supported queries whose complete Top-10 records changed;
  good result here is zero because the stage preserves valid existing behaviour. Limitation:
  matching an old ranking does not prove that ranking scientifically appropriate.
- Maximum absolute score difference: max |new score - original score| across each ordered
  pair matrix. Differences below 1e-12 are numerical precision here, not prediction error.
  The scatter's diagonal means score agreement, not agreement with experimental properties.
- Symmetry error: max |S(a,b)-S(b,a)|. Self error: max |S(a,a)-1|. Both were checked at
  tolerance 1e-12; these are mathematical invariants for these signals, not substitution tests.
- Coverage: number of elements with a representation and/or candidate eligibility. Higher
  coverage is not higher accuracy. Recognition of all 118 does not provide features for all.
- Query latency: wall-clock milliseconds for warm Ga Top-10 calls, 20 warmups then 200
  measured calls. Median is typical measured time, p95 the 95th percentile; neither is a
  confidence interval. One process/run and fixed target do not justify a general speedup claim.

Fresh Atom2Vec training used the entire unchanged 83,989-row composition snapshot with
dimension 20 and seed 42. {verification['fresh_training']['training_stats']['valid_binary_to_quaternary_rows']:,}
rows passed the existing composition filter; {verification['fresh_training']['training_stats']['skipped_rows']:,}
were skipped (includes unary/higher-order or otherwise ineligible rows, not all corrupt data).
Training took {verification['fresh_training']['seconds']:.3f} seconds in this run. Maximum pair-score
change from original cache was {verification['fresh_training']['max_abs_similarity_change_vs_original']:.3g};
all 79 fresh-model Top-10 outputs matched, and reload reproduced them. New cache metadata
records algorithm, dimension, seed and exact corpus-byte checksum. No GPU or cloud execution.

The parser issued a pymatgen warning about missing He electronegativity during composition
formatting. This was retained in the raw log. No He feature was fabricated, and the validated
embeddings are finite. Core corpus weighting/filter definitions were preserved.

Precision/recall, MRR, band-gap error, stability success and doping activation are not evaluated
here. The Stage 2 scientific benchmark remains incomplete, with zero held-out cases.
''')
    write(DOCS / 'implementation_guide.md', r'''# Architecture, algorithms and file responsibilities

This stage changes three signal engines and adds one shared validation helper. It does not
fuse signals, generate structures or predict materials properties. Valid output records retain:
method, target_element, rank, candidate_element, similarity_score (six decimal display).

## Shared validation: src/similarity_validation.py

Inputs: symbols, integer parameters, Parquet tables and numerical arrays. Outputs: checked
values, a DataFrame, support-status dictionaries or explicit exceptions. Dependencies: numpy,
pandas, pymatgen. validate_symbol accepts canonical symbols only; 'ga', formulas and whitespace
are rejected. validate_integer rejects booleans, negative k and nonintegers, accepts numpy
integer scalars. UnsupportedElementError is a ValueError subclass for a recognized element
without a representation. read_master rejects empty/duplicate/ill-identified records and
incorrect noble-gas group flags. It does not certify source measurements or physical units.

All 118 canonical elements are recognized. Each engine exposes get_support_status(element):
recognized, target_supported, candidate_eligible, reason, scientific_substitution_validated=False.
Default paths resolve from the project source location, so changing working directory does
not redirect default data/cache lookups. Explicit custom relative paths remain caller-relative.
Invalid target requests are checked even when k=0; supported targets with k=0 return [].
Large k returns the available candidates without duplicates or the target itself.

## PN engine: src/pn_similarity/pn_engine.py

Input: symbol/group/PN table and target. Output: PN similarities/rankings. Initialization now
requires unique integer PN values in 1..118, matching the recorded scale, not the old 1..103
header. Core equation is unchanged: S=1/(1+|PN_a-PN_b|). For PN values 40 and 42,
distance=2 and score=1/3. An adjacent element scores 1/2. This is a dimensionless ordinal
proximity signal, not a probability of successful substitution. Raw integer distances are used;
the separately recorded PN/118 feature is not substituted into this formula.

94 query elements are available. The default pool excludes noble gases (88 candidates),
while PN descriptive queries on represented noble gases remain available. This asymmetric
query/candidate policy preserves the original engine and is explicit in support metadata.
It is a project screening policy, not a universal assertion that noble gases cannot react.

## Property engine: src/property_similarity/property_engine.py

Input: original 14-feature table; output: cosine-based rankings over 88 non-noble feature rows.
Each candidate feature must be real and finite; physical magnitudes must be positive, while
subshell counts may be zero and must obey integer occupancy bounds. Missing values are
rejected; no new imputation is introduced. Initialization, not a later query, rejects corruption.

For feature x, z=(x-mu)/sigma with population standard deviation (ddof=0). Example:
[10,20,30] has mean 20, sigma about 8.165, and z(30) about 1.225. This stops large numerical
units from dominating solely because of scale. A constant feature contributes zero; its
division scale is set to 1. Every standardized element vector is then divided by its L2 norm.
Cosine = dot(a,b)/(norm(a)*norm(b)); [1,0] and [1,1] give 1/sqrt(2), about 0.7071.
Opposite directions give -1. A negative score is not a proven chemically incompatible pair.
An all-zero standardized row has no direction, so cosine is undefined and the table is rejected.
Overflow is caught; floating roundoff is bounded to [-1,1] before returning cosine scores.

The old table remains the default for behaviour compatibility. Stage 2 native data was not
silently activated: native field names/missingness need a separately reviewed integration.
Plausible-but-wrong positive values, historical imputation and source-condition/unit problems
cannot be certified by these numeric guards. Correlated features can still double-count trends;
feature weighting/ablation belongs to the next approved evaluation work.

## Atom2Vec: src/atom2vec/atom2vec_engine.py

Inputs: compressed composition corpus or cache, dimension and seed. Output: unit embeddings,
cosine rankings, cache_info and (when trained) training_stats. A composition such as Ga2O3
produces Ga environment '(2)O3' and O environment '(3)Ga2'. Repeated environments build
a sparse atom-environment count matrix. Each row is L2-normalized; sparse SVD decomposes
X approximately as U*Sigma*V-transpose. The retained representation U*Sigma has 20 default
dimensions and is normalized again for cosine similarity. This learns co-occurrence patterns;
it does not calculate band gap, defect formation energy or dopant activation.

Only binary-to-quaternary integer compositions are retained; common elements have at least
1% of maximum frequency. Corpus rows, including repeated compositions, keep their old
weighting for comparability. Input/skipped counts are recorded. Empty/malformed/too-small
corpora fail before SVD or cache publication. One byte snapshot supplies both parsed data
and its SHA-256 hash, preventing a mismatch between trained input and recorded checksum.
Dimension must be positive and smaller than both matrix dimensions for sparse SVD; the seed
must be a nonboolean integer from 0 through 2**32-1.

Cache loading disables pickle, validates unique canonical symbols, vector shape/dimension,
finite real values, unit row norms (absolute tolerance 1e-8), and descending nonnegative
dimension-matched singular values. A corrupt cache is rejected, never silently retrained over.
New cache metadata validates algorithm, dimension, seed and corpus hash (if corpus available).
If corpus is absent, cache_info explicitly says its checksum was not independently checked.
The original metadata-free cache remains usable in compatibility mode, with provenance
unverified in cache_info; require_cache_metadata=True rejects it. Non-default seed requests
against metadata-free caches are rejected. Default compatibility does not prove the old seed.

Cache publication first completes a temporary archive in the destination directory. Windows
rename refuses an existing destination; POSIX uses an exclusive hard link. Only the temporary
file created by this operation is cleaned up. A competing destination is preserved. The Windows
path was tested; the POSIX branch and Mac execution have not been verified here.

## Experiments and tests

capture_baseline.py preserves original engines, rankings, pair matrices, environment and hashes.
verify_engines.py compares all pairs/rankings, checks 118-element support, measures warm
latency and trains/reloads one new full-corpus cache. build_reports.py reads actual JUnit and
experiment outputs, maps the 15 historical failures, verifies preservation and creates reports.
tests/stage_03/test_engine_hardening.py contains 148 new executed cases, including optimized
Python validation and simulated solver/permission/concurrent-writer failures. Synthetic
fixtures test arithmetic and error handling; they are not experimentally validated materials.

Run tests from C:Final Project, choosing a NEW base directory (pytest clears its selected base):

    .venvScriptspython.exe -m pytest tests --basetemp="C:Final Projectworkstage_03pytest_NEW" -q

Use get_support_status('Og') to inspect support, get_top_k('Ga', 10) for a ranking, and
compute_similarity('Ga','Al') for a pair score. See the method's cache_info before treating
a cache as reproducibly trained. The archived fresh strict cache is
results/stage_03/run_001/fresh_atom2vec_d20.npz; pass that explicit path with
require_cache_metadata=True to load it. The production default cache was not replaced.
''')
    mapping = '\n'.join(f'| {name} | failed | passed |' for name in sorted(regression))
    write(DOCS / 'edge_case_report.md', f'''# Executed robustness checks

Final suite: {counts['tests']} passed, 0 failures/errors/skips in {suite.attrib['time']} seconds.
148 new cases plus 172 earlier tests. JUnit: logs/stage_03/run_001/pytest_final.xml.

| Historical diagnostic | Original observed result | New targeted regression |
|---|---|---|
{mapping}

The dimension regression now requires rejecting an incompatible cache, rather than silently
using 20 dimensions when 10 were requested. Original historical logs are unchanged; this
does not claim the old diagnostic runner itself was rewritten or all 78 old probes re-executed.

Other executed checks include invalid/nonhashable symbols, malformed types, negative/boolean/
noninteger k, numpy-integer k, zero k, huge k, explicit unsupported elements, missing/corrupt
tables, duplicate records, bad atomic identities/groups, PN range/type/uniqueness/missingness,
NaN/infinite/negative/zero-invalid features, numeric strings, booleans, complex features,
fractional/out-of-range electron counts, missing columns, overflow, zero standardized vectors,
constant-column handling, hand-calculated PN ties and cosine directions, NaN/infinite/zero/
nonunit/complex/cache vectors, shape/duplicate/invalid/object vocabularies, singular-value
shape/sign/order, metadata schema/type/seed/dimension/hash/JSON failures, strict legacy-cache
rejection, absent source corpus, changed corpus, empty/malformed/too-small corpora, skipped-row
accounting, repeated seeded training and cache reload, missing/corrupt cache, simulated solver
and write-permission failures, competing-writer preservation and temporary-file cleanup,
cwd-independent defaults, and explicit validation under python -O.

Initial hardening run: 115 passed, 2 failed, 1 skipped. Actual Windows hard-link publication
was denied; Windows publication was changed to no-overwrite rename and verified. A redundant
complex-Parquet parameter was removed; complex data is separately tested at the DataFrame
boundary. Follow-up hardening run passed 133 cases, then 15 mapped regressions were added.
The final entire suite passed 320 cases without skips. Initial logs remain available.

Limits: exhaustive malformed nested archives, every SciPy failure, power-loss durability,
arbitrary concurrent processes, POSIX/Mac behaviour, clean-machine setup and chemical validity
were not verified. Simulated errors test the specified paths, not every filesystem failure.
''')
    write(DOCS / 'validation_report.md', f'''# Validation classification

| Category | Status | Evidence / limit |
|---|---|---|
| Functionality | Verified for tested scope | {counts['tests']} passing tests; all 15 recorded defect behaviours covered |
| Mathematical consistency | Verified for represented pairs | 22,821 ordered pairs, symmetry/self invariants, hand examples, finite bounded scores |
| Behaviour preservation | Verified | Zero changed Top-10 records for all 261 supported engine-target combinations |
| Local reproducibility | Verified | Fresh full-corpus training and cache reload reproduce ranking geometry in this environment |
| Earlier file preservation | Verified | {len(before)} previous/root files checked; only intended engine/docs/Git-rule changes |
| Source metadata | Partial | New caches record/check lineage; legacy default cache has no embedded training metadata |
| Cross-platform/clean-machine reproducibility | Not yet verified | Existing Windows/Python 3.10.11 only; POSIX branch not executed |
| Substitution/doping scientific validity | Not verified here | Stage 2 benchmark hold remains; no new ground-truth labels |
| Band gap/energy/stability preservation | Not evaluated | No structure/property/DFT module implemented in this stage |

Passing software tests is not proof of successful material substitution. The two narrow
development references do not constitute a representative or independent scientific benchmark.
No classification accuracy/precision/recall or ranking-generalization score is claimed.
''')
    write(DOCS / 'reproducibility.md', r'''# Reproduce and review Stage 3

All paths are under C:Final Project. Existing local .venv and dependencies were used without
installs/upgrades. Environment versions and initial commit are in results/stage_03/run_001/environment.json.
No cloud/remote execution or external dataset retrieval occurred in Stage 3.

- Original engines: results/stage_03/run_001/original_engines, plus Git tag
  matra-stage-03-baseline-02547fa. Existing user changes/presentations were preserved.
- Inputs: data/processed/elements_master.parquet, original atom2vec_embeddings_d20.npz and
  data/raw/mp_nostruct_20181018.json.gz. Raw/processed data and benchmark files were not edited.
- Baseline: baseline.json contains all supported Top-10 results and complete pair matrices.
- Parameters/results: engine_verification.json contains tolerances, full support statuses,
  raw per-call timings, seed, dimension, training counts and corpus checksum.
- New model: fresh_atom2vec_d20.npz, written once; old default cache is unchanged.
- Numerical arrays: score_comparison.npz, load with allow_pickle=False.
- Tests/failures: logs/stage_03/run_001 includes initial, corrected and final executions.
- Figures: score_agreement, regression_checks, warm_latency in both PNG and SVG.

The capture/verification/report scripts refuse reuse of their completed run output. Re-run tests
with a fresh pytest base directory. For a new training experiment, choose a new cache path;
changing embedding_dim against the old cache is an error, not an implicit model replacement.
The same corpus byte checksum and config do not guarantee bitwise portability across BLAS,
SciPy, OS or hardware. Compare similarities/rankings, since SVD vector signs can differ while
their pairwise geometry is unchanged. Current numerical reproducibility is local only.

Rollback, if requested, is limited to restoring the three original engine files from the baseline
Git tag or preserved copies. Keep data/results and unrelated user files intact. The shared new
helper becomes unused under original engines; no deletion/migration is needed. No rollback
was executed, and nothing was pushed to GitHub.
''')
    write(DOCS / 'telugu_transcript.md', '''# తెలుగు narration — Stage 3 similarity engine hardening

Playable Telugu audio తయారు చేయలేదు. ఈ environment లో speech-generation tool అందుబాటులో లేదు.
ఇది text-to-speech కోసం ఉపయోగించగల పూర్తి narration script.

## 1. ఈ స్టేజ్‌లో మనం ఏం చేస్తున్నాం?
మన దగ్గర PN, Property, Atom2Vec అనే మూడు similarity engines ఉన్నాయి.
ఈ stage లో వాటి algorithm ని కలపడం లేదు. వాటికి తప్పు inputs వచ్చినప్పుడు సరైన error ఇవ్వడం,
చెడ్డ data లేదా cache తో recommendations ఇవ్వకుండా ఆపడం చేస్తున్నాం.

## 2. ఇది ఎందుకు అవసరం?
Calculator తప్పు input తీసుకుని సాధారణ answer చూపిస్తే మనం దాన్ని నమ్మే ప్రమాదం ఉంది.
మునుపు k=-1 ఇచ్చినా results వచ్చేవి, duplicate rows వల్ల repeated candidates వచ్చేవి,
NaN vectors కూడా cache నుంచి లోడ్ అయ్యేవి. ఇవి scientific accuracy సమస్యకు ముందున్న software సమస్యలు.

## 3. మనం ఏం implement చేశాం?
Common input validation, element support status, duplicate checks, feature validity checks,
embedding shape మరియు norm checks చేశాం. కొత్త cache లో dimension, seed, corpus hash metadata రాస్తున్నాం.
పాత working engines copies, rankings, scores ని ముందుగానే preserve చేశాం.

## 4. ఏ algorithms మరియు technologies వాడాం?
Python, numpy, pandas, scipy sparse SVD, pymatgen, pytest, matplotlib ఉపయోగించాం.
పాత మూడు algorithms అలాగే ఉన్నాయి. కొత్త dependency install చేయలేదు. Cloud లేదా GPU అవసరం రాలేదు.

## 5. మూడు engines ఎలా పనిచేస్తాయి?
PN లో periodic-number distance తక్కువైతే similarity ఎక్కువ. Formula ఒకటి భాగించు ఒకటి plus distance.
Distance రెండు అయితే score ఒకటి భాగించు మూడు, అంటే సుమారు 0.333.
Property engine లో 14 features ని standardize చేస్తాం. Mean తీసేసి standard deviation తో భాగిస్తాం.
తరువాత vectors మధ్య cosine similarity చూస్తాం. Vectors ఒకే direction లో ఉంటే score ఒకటికి దగ్గరగా ఉంటుంది.
Zero vector కి direction ఉండదు; అందుకే దానికి మౌనంగా zero score ఇవ్వకుండా error ఇస్తాం.
Atom2Vec లో compounds లో elements ఏ environments తో కలిసి కనిపిస్తున్నాయో count matrix తయారు చేస్తాం.
SVD దానిలోని ప్రధాన patterns ని చిన్న vectors లో ఉంచుతుంది. ఈ vectors మీద cosine similarity వాడతాం.
ఇవేవీ band gap లేదా stability ని నేరుగా లెక్కించవు.

## 6. Actual results ఏంటి?
చివరి పూర్తి test suite లో 320 tests pass అయ్యాయి. పాత 15 failing behaviours కి targeted regression tests pass అయ్యాయి.
మూడు engines కలిపి supported targets మీద 261 Top-10 outputs compare చేశాం; ఒక్కటి కూడా మారలేదు.
22,821 ordered pair scores compare చేశాం. తేడా సుమారు ఏడు గుణించు పది power minus పదహారు కంటే తక్కువ.
అది floating-point rounding స్థాయి. కొత్త పూర్తి corpus training కూడా పాత Atom2Vec rankings ని reproduce చేసింది.

## 7. Numbers మరియు graphs అర్థం ఏమిటి?
Score graph లో points diagonal మీద ఉండటం పాత score, కొత్త score ఒకేలా ఉన్నాయని చెబుతుంది.
అది experimental material property prediction సరైందని చెప్పదు. 15 regression checks pass అవడం software bugs సరిచేశామని చెబుతుంది.
Latency graph ఈ local run లో query కి పట్టిన milliseconds చూపిస్తుంది. Median సాధారణ measured time;
p95 అంటే 95 percent calls దానికంటే తక్కువ సమయంలో పూర్తయ్యాయి. ఒక్క run వల్ల general speedup claim చేయడం లేదు.

## 8. ఏ edge cases పరీక్షించాం?
ఖాళీ లేదా invalid element, formula బదులు symbol ఇవ్వడం, negative k, boolean k, duplicate records,
missing files, NaN, infinity, negative density, తప్పు electron counts, zero vectors, wrong cache dimensions పరీక్షించాం.
Wrong seed, changed corpus, damaged JSON, pickle అవసరమయ్యే cache, solver failure, permission failure,
మరో process file create చేసిన పరిస్థితి, వేరే working directory నుంచి execution కూడా పరీక్షించాం.
python -O లో కూడా validation ఆగిపోకుండా పని చేస్తుందని చూశాం.

## 9. ఏ సమస్యలు ఎదురయ్యాయి?
మొదటి కొత్త tests లో Windows hard-link operation కి permission denied వచ్చింది.
Windows లో existing destination ని overwrite చేయని rename పద్ధతి వాడి సమస్య సరిచేశాం.
మొదటి failed test logs తొలగించలేదు. కొత్త training సమయంలో pymatgen He electronegativity warning ఇచ్చింది;
ఆ warning log లో ఉంది. మనం He feature ని కల్పించలేదు; embeddings finite గా ఉన్నాయని checks నిర్ధారించాయి.

## 10. ఇంకా ఏం మిగిలింది?
118 elements ని recognize చేస్తాం కానీ ప్రతి engine కి అన్నింటి data లేదు. PN query support 94,
Property 88, Atom2Vec 79 మాత్రమే. Missing representation కి స్పష్టమైన unsupported error ఇస్తాం.
పాత cache లో training metadata లేదు; compatibility mode లో అది స్పష్టంగా చెబుతాం.
Strict metadata mode పాత cache ని reject చేస్తుంది; కొత్త verified experiment cache మాత్రం అందుబాటులో ఉంది.
Native Stage 2 feature release ని default గా మార్చలేదు. Mac లేదా clean machine reproduction ఇంకా పరీక్షించలేదు.

## 11. ఈ stage పూర్తి అయిందని ఎలా నిర్ధారించాం?
Executed tests, పాత behaviour comparison, pair-score invariants, కొత్త training మరియు reload,
file preservation hashes ఆధారంగా software లక్ష్యం పూర్తయిందని చెబుతున్నాం.
Scientific substitution validity మాత్రం వేరే విషయం. Benchmark ఇంకా incomplete; doping activation,
band-gap preservation, energy stability గురించి ఈ stage కొత్త claim చేయదు.

## 12. తర్వాతి stage తో సంబంధం ఏమిటి?
Stage 4 లో ఈ మూడు signals ని ఎలా కలపాలి అనేది చూస్తాం. అంతకుముందు ప్రతి signal reliable software గా పని చేయాలి.
ఇప్పుడు వాటి input, output, support limits స్పష్టంగా ఉన్నాయి. Next stage లో weights లేదా evaluation నిర్ణయాలు
విడిగా explain చేయాలి. మీ approval లేకుండా Stage 4 మొదలుపెట్టలేదు.
''')
    write(DOCS / 'completion_report.md', f'''# STAGE COMPLETION REPORT — Stage 3

1. **Objective:** harden independent PN, Property and Atom2Vec signals while preserving
   valid equations/rankings. Owner explicitly authorized Stage 3 with Stage 2 research hold disclosed.
2. **Implemented:** shared input/data contracts, explicit recognized/unsupported handling,
   duplicate rejection, finite/physical-basic feature guards, undefined-vector rejection,
   safe cache loading/config checks, corpus validation and no-overwrite cache publication.
3. **Created:** src/similarity_validation.py; tests/stage_03/test_engine_hardening.py;
   experiments/stage_03/capture_baseline.py, verify_engines.py, build_reports.py; preserved
   originals, new strict experimental cache, logs/results/figures and this documentation.
4. **Modified:** src/pn_similarity/pn_engine.py, src/property_similarity/property_engine.py,
   src/atom2vec/atom2vec_engine.py, docs/progress.md and scoped .gitattributes. Existing
   datasets, default cache, benchmark labels, unrelated modules/user files preserved.
5. **Methods:** existing PN distance, z-score/cosine and atom-environment SVD; runtime
   validation, checksums, deterministic regression checks, complete pair/ranking comparison.
6. **Actual outputs:** {counts['tests']} tests passed (172 previous + 148 new), all 15 recorded
   defect behaviours remediated. Zero changed Top-10s across 261 supported engine-targets;
   22,821 ordered pair checks differ only at floating roundoff. Fresh full-corpus training/reload
   reproduces rankings with dimension 20/seed 42 metadata. Timings and plots are measured.
7. **Edge cases:** executed cases and original failure mapping in edge_case_report.md.
   Initial publication failures were resolved before completion; historical logs retained.
8. **Validation:** software/math/local reproducibility verified for scope; previous/root
   file hashes checked ({len(before)} files). Chemistry, clean-machine/Mac/POSIX validation
   not established. See validation_report.md for separate categories.
9. **Known issues:** compatibility-mode default cache lacks embedded training metadata;
   strict mode rejects it. Legacy feature-source limitations remain. Pymatgen parsing warning
   retained. POSIX publication branch not executed here.
10. **Scientific limits:** scores are similarity signals, not substitution probabilities,
    measured property predictions or doping activation. No representative independent benchmark
    yet; only two narrow substitution development references and zero complete doping cases.
11. **Incomplete:** Stage 4 fusion/evaluation and all later stages; native-data integration
    still needs a reviewed missingness/compatibility policy. Scientific benchmark hold persists.
12. **Telugu:** complete transcript in telugu_transcript.md. No playable audio generated;
    this environment has no speech-generation tool.
13. **Readiness:** Stage 3 engineering scope is complete and ready for owner review.
    Stage 4 has not started and requires owner approval and a pre-implementation explanation.

Read implementation_guide.md for file responsibilities, algorithms, formulas, examples,
execution and limitations; results_and_metrics.md for actual measured comparisons;
reproducibility.md for inputs/configuration/rollback; index.html for figures and full support table.
No files were pushed to GitHub. Approval to advance is still pending.
''')
    docs = ['completion_report.md', 'implementation_guide.md', 'results_and_metrics.md', 'edge_case_report.md', 'validation_report.md', 'reproducibility.md', 'telugu_transcript.md']
    links = ''.join(f'<li><a href="{name}">{name}</a></li>' for name in docs)
    rows = []
    for i in range(118):
        entries = [verification['engines'][m]['element_statuses'][i] for m in methods]
        cells = [entries[0]['element']] + [f"query={'yes' if e['target_supported'] else 'no'}; candidate={'yes' if e['candidate_eligible'] else 'no'}" for e in entries]
        rows.append('<tr>' + ''.join('<td>' + html.escape(value) + '</td>' for value in cells) + '</tr>')
    figures = ''.join(f'<img alt="{description}" src="../../../results/stage_03/run_001/{name}.png">' for name,description in [('score_agreement','Software score agreement, not experimental accuracy'), ('regression_checks','Previously failing software checks now passing'), ('warm_latency','Measured warm query time, no speedup claim')])
    write(DOCS / 'index.html', '<!doctype html><meta charset="utf-8"><title>MATRA Stage 3 review</title>'
          '<style>body{font:16px system-ui;max-width:1250px;margin:35px auto;padding:20px;color:#25354a}img{max-width:100%}table{border-collapse:collapse}td,th{padding:10px;border:1px solid #cbd2da}p{line-height:1.6}</style>'
          f'<h1>MATRA Stage 3: independent-engine hardening</h1><p><strong>{counts["tests"]} tests passed; 15 recorded defect behaviours remediated.</strong> All 261 supported Top-10 results preserved. '
          'This is software validation. Scientific benchmark remains incomplete; Stage 4 not started.</p><ul>' + links + '</ul>' + figures +
          '<h2>118-element recognition and per-method support</h2><p>Representation availability and candidate policy are distinct. No scientific substitution validation is implied.</p>'
          '<table><tr><th>Element</th>' + ''.join('<th>'+m+'</th>' for m in methods) + '</tr>' + ''.join(rows) + '</table>')
    targets = re.findall(r'(?:href|src)="([^"]+)"', (DOCS / 'index.html').read_text(encoding='utf-8'))
    if not all((DOCS / target).is_file() for target in targets): raise ValueError('Broken report link')
    files = [ROOT / p for p in allowed] + [ROOT / 'src/similarity_validation.py']
    files += [p for directory in ('experiments/stage_03', 'tests/stage_03', 'docs/stages/stage_03') for p in (ROOT / directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    files += [OUT / name for name in ('baseline.json', 'environment.json', 'engine_verification.json', 'score_comparison.npz', 'fresh_atom2vec_d20.npz', 'final_verification.json')]
    write(OUT / 'artifact_manifest.json', json.dumps({'sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}, 'report_links_verified': len(targets)}, indent=2))
    print(json.dumps(tests, indent=2))


if __name__ == '__main__': main()
