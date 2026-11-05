"""Produce evidence-readiness reports from actual cached papers and test output."""
from pathlib import Path
from collections import Counter
import hashlib
import html
import importlib.metadata
import json
import os
import platform
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.stage_02.build_extended_review import build_release
from src.data_audit.evidence_extension import validate_extended_review

DOCS = ROOT / 'docs/stages/stage_02_extended_review'
RUN = ROOT / 'results/stage_02/run_003'
os.environ['MPLCONFIGDIR'] = str(RUN / 'matplotlib_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def write(path, content):
    with path.open('x', encoding='utf-8') as stream:
        stream.write(content)


def main():
    release = json.loads((ROOT / 'data/benchmark/v2_2_0/extended_evidence.json').read_text(encoding='utf-8'))
    counts = validate_extended_review(release, ROOT)
    if release != build_release(): raise ValueError('Nonidentical rebuild')
    junit = ET.parse(ROOT / 'logs/stage_02/run_003/pytest.xml').getroot().find('testsuite')
    tests = {key: junit.attrib[key] for key in ('tests', 'failures', 'errors', 'skipped', 'time')}
    if tests['failures'] != '0' or tests['errors'] != '0': raise ValueError('Test failures remain')
    previous = json.loads((RUN / 'starting_hashes.json').read_text(encoding='utf-8'))
    changed = [name for name, checksum in previous.items() if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != checksum]
    unexpected = [name for name in changed if name not in ('.gitattributes', 'docs/progress.md')]
    if unexpected: raise ValueError(f'Unexpected previous changes: {unexpected}')
    result = {'workspace': str(ROOT), 'operating_system': platform.platform(), 'python': sys.version,
              'dependencies': {name: importlib.metadata.version(name) for name in ('numpy', 'pandas', 'pymatgen', 'pytest', 'matplotlib')},
              'counts': counts, 'pytest': tests, 'previous_tracked_files_checked': len(previous),
              'previous_files_intentionally_changed': changed, 'unexpected_previous_changes': unexpected,
              'identical_rebuild': True, 'independent_scientific_adjudication': 'pending',
              'configuration': {'release': '2.2.0', 'full_context_gates': ['host', 'phase', 'site', 'concentration'],
                                'occupancy_sum_absolute_tolerance': 1e-6, 'uncertainty_propagation': False,
                                'train_model': False, 'run_dft': False, 'score_predictions': False,
                                'unknown_is_negative': False, 'development_only': True}}
    write(RUN / 'verification.json', json.dumps(result, indent=2))
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    bars = ax.bar(['Inner 3a', 'Outer 6c'], [91.5, 4.3], yerr=[1.4, .7], capsize=6, color=['#476fad', '#b78742'])
    ax.bar_label(bars, labels=['91.5 ± 1.4%', '4.3 ± 0.7%'], padding=10)
    ax.set(ylim=(0, 108), ylabel='Se occupancy on each site (%)', title='Bi₂Te₂Se: source-reported site occupancies')
    fig.text(.5, .03, 'Jia et al., Table I: refinement estimates and reported uncertainties. Not MATRA predictions.', ha='center', fontsize=8)
    fig.tight_layout(rect=(0, .06, 1, 1))
    for extension in ('png', 'svg'):
        path = RUN / f'source_site_occupancy.{extension}'
        if path.exists(): raise FileExistsError(path)
        fig.savefig(path, dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(9.3, 4.4))
    for ax, values, title in zip(axes, ([1, 1, 2], [2, 0]), ('Full-context evidence readiness', 'Eligible reference tracks')):
        labels = ['Experimental', 'Computational', 'Held'] if len(values) == 3 else ['Substitution', 'Doping']
        bars = ax.bar(labels, values, color=['#38877d', '#5071a8', '#c7944b'][:len(values)])
        ax.bar_label(bars, padding=4)
        ax.set(ylim=(0, 3), title=title, ylabel='Claim count')
        ax.set_yticks(range(4))
        ax.tick_params(axis='x', labelsize=9)
    fig.text(.5, .02, 'Development references only; zero held-out cases. Three unscored observations are excluded.', ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .05, 1, 1))
    for extension in ('png', 'svg'):
        path = RUN / f'evidence_readiness.{extension}'
        if path.exists(): raise FileExistsError(path)
        fig.savefig(path, dpi=160)
    plt.close(fig)
    write(DOCS / 'scientific_review.md', '''# Scientific review and interpretation

This release adds one experimental substitution reference to the one earlier computational
reference. Both are development cases, not independent test cases. No recommendation score,
MAE, precision, recall, ROC or confusion matrix was computed. Positive references alone cannot
establish false-positive rates or precision, and unknown candidates are not true negatives.

## New experimental scope

Jia et al., arXiv:1112.1648v1, associated journal DOI 10.1103/PhysRevB.84.235206,
report room-temperature powder XRD of a Bridgman-Stockbarger Bi2Te2Se crystal. Their
refinement places most Se on the inner chalcogen site with minor outer-site mixing.
The new scope concerns that investigated structural model and nominal composition only.
Different preparation histories in the same paper show different peak shapes/phase separation.
No whole-composition-range stability or preserved band-gap claim is admitted.

Source: https://arxiv.org/abs/1112.1648 ; cached PDF and extraction in data/raw/stage_02_extended_sources.
Table I on PDF page 5 was inspected visually; phase/form/preparation passages are in pages 4–7.

## Doping observations remain unscored

Siah et al., DOI 10.1063/1.4938123, distinguish conductive beta-Ga2O3 crystals from
resistive amorphous Sn-containing films. EXAFS supports octahedral Ga2-site preference in
the crystal. Its exact Sn concentration was not linked to a tabulated XAS specimen value
in the reviewed passages; graph points were not digitized. The full contextual doping label
therefore remains withheld. EXAFS fit residuals are not MATRA accuracy.

The paper's ALD film has an estimated Sn number density of 2.3e20 atoms/cm3 and
resistivity above the 2000 ohm cm detection limit. The authors' carrier-density upper bound
depends on an assumed mobility. It is retained as a conditional observation, without a point
estimate of activation efficiency or a universal negative label for Sn substitution.

Source: https://www.osti.gov/servlets/purl/1371047 ; PDF pages 3–5, Figures 1–4 and Table I.

## Source-quality hold

Elius et al., arXiv:2007.00972, describes the Ba/Sr A site as tetrahedral in its abstract
and 12-fold cuboctahedral in its introduction. Table 4 calls the intermediate specimen
pseudo-cubic while reporting unequal cell edges in one refinement. Exact coordination and
space-group claims remain withheld pending an independent consistent reference. This is
a source-description issue, not evidence that Sr incorporation is chemically impossible.

Source: https://arxiv.org/abs/2007.00972 ; PDF pages 1 and 4. The PDF has a 2019 journal
header; publication/review status was not independently adjudicated. Peelaers' separately
acquired Ga-Al proof copy also requires its published erratum to be checked before importing
numerical results. Neither source is silently promoted to experimental ground truth.

## Coverage and remaining work

Every one of the 23 legacy assertions has a specific hold and follow-up requirement in
the new ledger. All remain unknown at their original broad scope. Two narrowed positive
substitution references cannot demonstrate performance for all elements or all combinations.
Zero fully contextual doping references and zero held-out cases are currently available.
More independent hosts, phase/site cases, role-specific doping evidence, appropriately scoped
counterexamples and materials-expert adjudication are still required.
''')
    write(DOCS / 'implementation_and_math.md', r'''# Files, execution and scientific bookkeeping

The legacy code and v2.0/v2.1 releases are unchanged. New work is additive:

| File | Responsibility / inputs / outputs |
|---|---|
| experiments/stage_02/collect_extended_sources.py | Public PDF requests, local extraction through bundled pypdf; writes raw snapshots, retrieval errors and starting hashes once |
| experiments/stage_02/build_extended_review.py | Prior ledger + reviewed passages -> v2.2 JSON and readiness counts; refuses overwrite |
| src/data_audit/evidence_extension.py | Reuses the unchanged v2.1 admission policy; checks parent hashes, inherited decisions, host-family grouping, all 23 legacy identities, conditional observations and source-table arithmetic |
| tests/stage_02/test_evidence_extension.py | Real source-backed success checks and 38 new boundary/adversarial test cases |
| experiments/stage_02/report_extended_review.py | Actual JUnit + ledger -> reports, two figures, preservation checks and a reproducibility manifest |

`validate_extended_review` verifies data lineage and admission rules; it cannot independently
prove the scientific interpretation. Its output is a dictionary of counts, not accuracy.
`weighted_site_composition` sums occupancy times multiplicity on the listed sites. It does
not construct structures, calculate energies, predict site preferences or validate symmetry.
No new package was installed. Local dependencies are recorded in run_003/verification.json.

## Why site multiplicity matters

Occupancy means the fraction of equivalent positions filled by an element. Multiplicity
means how many such positions occur in the crystallographic cell. For element E,

    N_E = sum over sites j of (m_j * o_E,j)
    f_E = N_E / sum over listed sites j of m_j

N_E is a model atom count, m_j is site multiplicity, o_E,j is occupancy (between 0 and 1),
and f_E is the fraction on the listed sublattice. Each fully occupied site's element fractions
must sum to one. This version deliberately rejects vacancy-bearing tables instead of silently
renormalizing them; vacancies need a separately reviewed convention.

For the source's hexagonal-cell chalcogen sites:

- Outer 6c: 6 * 0.043 = 0.258 modeled Se atoms.
- Inner 3a: 3 * 0.915 = 2.745 modeled Se atoms.
- Total: 3.003 Se atoms on 9 chalcogen positions, giving 0.333666... Se fraction.
- Dividing the cell counts by three formula units gives approximately Bi2Te1.999Se1.001,
  consistent with the nominal Bi2Te2Se model within the reported refinement precision.

This is arithmetic on the reported model, not an independent chemical measurement.
The source fit constrains composition; the calculation is a consistency check, not independent
validation. Nominal Se/(Se+Te) is 1/3; nominal Se/all-atoms would be 1/5. These bases differ.

The notation 0.915(14) means 0.915 with reported refinement uncertainty 0.014, not 91.5%
MATRA confidence. The plot uses these source uncertainties directly. A combined uncertainty
for the derived composition is not calculated because refinement covariances are unavailable.

## How to run and verify

From C:Final Project, run a fresh test directory:

    .venvScriptspython.exe -m pytest tests --basetemp="C:Final Projectworkstage_02extended_reviewpytest_NEW" -q

pytest clears its selected base directory, so choose a new name. Archived actual tests are
logs/stage_02/run_003/pytest.xml and pytest.txt. For a read-only ledger check:

    .venvScriptspython.exe -c "from pathlib import Path; import json; from src.data_audit.evidence_extension import validate_extended_review; p=Path.cwd(); print(validate_extended_review(json.loads((p/'data/benchmark/v2_2_0/extended_evidence.json').read_text(encoding='utf-8')),p))"

No new ledger is automatically activated in production recommendation engines. Rollback is
to continue using the previous release; no migration or deletion is needed. Scoped .gitattributes
rules preserve exact evidence-file bytes across Git checkouts. Unrelated existing user files
and the earlier dirty result remain excluded from this stage's commit.
''')
    write(DOCS / 'edge_case_and_validation_report.md', f'''# Executed checks and validation status

Actual full suite: {tests['tests']} passed, {tests['failures']} failures, {tests['errors']} errors,
{tests['skipped']} skipped in {tests['time']} seconds. This includes 38 new tests and 105 prior tests.
No claim is made that unit tests establish chemistry correctness.

New executed cases include deterministic rebuild/saved equality; retained minor site disorder;
distinct dopant/carrier quantities; parent hash damage; deleted/altered inherited claims;
false held-out designation; missing/incorrect host grouping; missing/duplicated legacy records;
false negative legacy label; wrong cross-reference; scoring an unscored observation;
property-preservation overclaim; absent passage; missing observations; invalid observation kind;
wrong density unit; infinite density; missing mobility assumption; reversed detection bound;
invented activation-efficiency estimate; altered derived composition; altered occupancy values
even with a recomputed total; missing source-table row; wrong Wyckoff multiplicity; empty or
duplicate site tables; boolean/zero multiplicity; negative/infinite/boolean occupancies;
overfull/underfull sites; invalid element; fully ordered boundary with zero minor occupancy.

An actual second builder invocation refused overwrite with FileExistsError, as intended;
the log is repeat_build_refusal.txt. Two additional source requests returned non-PDF responses
and received no full-text credit. Their URLs, UTC times and failures are in acquisition_manifest.json.

| Validation category | Status | Limit |
|---|---|---|
| Software functionality | Verified for executed cases | Arbitrary malformed inputs/websites not exhaustively tested |
| Local reproducibility | Verified | Same cached files and environment; not clean-machine verification |
| Existing-work preservation | Verified | {len(previous)} previous tracked files checked; only .gitattributes and progress.md intentionally changed |
| Scientific interpretation | Partially verified | Traceable single-reviewer readings; expert adjudication pending |
| Experimental substitution evidence | One narrow development reference | No generalized substitution success claim |
| Dilute doping benchmark | Incomplete | Zero fully contextual eligible references |
| Property preservation / prediction accuracy | Not verified | No predictions, DFT or preservation experiments run |
| Independent generalization | Not verified | Zero held-out cases; related samples grouped by host family |

No performance benchmark was run: pytest runtime is not prediction latency or throughput.
No source covariance was available for uncertainty propagation. No concentration point was
invented from the Sn plot, and missing chemistry evidence was not relabeled as failure.
''')
    write(DOCS / 'telugu_transcript.md', '''# తెలుగు narration — Stage 2 extended evidence review

ఈ environment లో playable Telugu audio generate చేయలేదు. Speech-generation tool లేదు.
కింద ఉన్నది text-to-speech కోసం ఉపయోగించగల పూర్తి వివరణ.

1. ఈ భాగంలో మనం ఏం చేస్తున్నాం?
మన benchmark కి ఇంకొన్ని research papers ఆధారంగా నమ్మదగిన reference cases చేరుస్తున్నాం.
పాత data ని మార్చకుండా కొత్త version లో ప్రతి decision కి ఆధారం నమోదు చేస్తున్నాం.

2. ఇది ఎందుకు అవసరం?
Element recommendation అంటే రెండు elements ఒకేలా కనిపిస్తున్నాయని చెప్పడం మాత్రమే కాదు.
కొత్త element material లో సరైన స్థానంలో చేరిందా, ఏ phase లో ఉంది, ఎంత concentration వాడారో తెలుసుకోవాలి.
ఈ వివరాలు లేకుండా recommendation scientifically correct అని మార్కులు ఇవ్వలేం.

3. మనం ఏం implement చేశాం?
కొత్త evidence ledger, source-table checks, పాత 23 assertions కి follow-up requirements తయారు చేశాం.
ఒక experimental substitution reference చేరింది. మూడు అదనపు observations ని scoring బయట ఉంచాం.
పాత computational reference అలాగే ఉంది. Stage 3 మొదలుపెట్టలేదు.

4. ఏ methods వాడాం?
Local Python, JSON, SHA-256 hashes, pytest, matplotlib, PDF reading వాడాం.
కొత్త AI model train చేయలేదు. కొత్త DFT calculation కూడా నడపలేదు.
XRD అంటే X-ray diffraction: crystal లో atoms arrangement గురించి సమాచారం ఇచ్చే experiment.
XAS అంటే X-ray absorption spectroscopy: ఒక element చుట్టూ ఉన్న local environment ని పరిశీలించే పద్ధతి.

5. Site occupancy ఎలా అర్థం చేసుకోవాలి?
ఒక crystal site లో ఎంత భాగం Se ఉంది అనేదే occupancy. అదే రకం స్థానాలు cell లో ఎన్ని ఉన్నాయో multiplicity.
Outer site లో ఆరు positions ఉన్నాయి; Se occupancy 0.043. అందువల్ల modeled Se count 6 గుణించు 0.043, అంటే 0.258.
Inner site లో మూడు positions ఉన్నాయి; occupancy 0.915. Count 2.745.
మొత్తం 3.003 Se atoms ని తొమ్మిది chalcogen positions తో భాగిస్తే సుమారు 0.3337 వస్తుంది.
ఇది source model మీద చేసిన arithmetic check మాత్రమే; కొత్త chemical measurement కాదు.

6. ఏ ఫలితాలు వచ్చాయి?
ఇప్పుడు ఒక experimental substitution reference, ఒక computational substitution reference ఉన్నాయి.
పూర్తి context ఉన్న doping references ఇంకా సున్నా. మొత్తం software tests 143 pass అయ్యాయి.
ఇది పెద్ద scientific test benchmark పూర్తయిందని అర్థం కాదు.

7. Graphs అర్థం ఏమిటి?
మొదటి graph లో inner site మీద source-reported Se occupancy 91.5 percent, outer site మీద 4.3 percent చూపించాం.
Error bars paper లోని refinement uncertainty. అవి మన AI confidence కాదు.
రెండో graph లో ఎన్ని evidence records ready గా ఉన్నాయో చూపించాం. అది accuracy graph కాదు.
Se చక్కగా ఒకే site లో పూర్తిగా ఉంది అనడం తప్పు; కొంత mixing ని source report చేసింది.

8. ఏ edge cases పరీక్షించాం?
తప్పు units, infinite values, boolean values, ఖాళీ tables, duplicate sites, మొత్తం ఒకటి కాకపోయే occupancies,
మార్చిన source numbers, తప్పు multiplicity, లేని source passage, చెడిపోయిన hash పరీక్షించాం.
Unknown chemistry ని negative label చేయడం, unscored observation కి accuracy credit ఇవ్వడం కూడా reject అవుతుందా చూశాం.

9. ఏ సమస్యలు ఎదురయ్యాయి?
రెండు PDF requests కి నిజమైన PDF బదులు వేరే response వచ్చింది. వాటికి evidence credit ఇవ్వలేదు.
Sn-Ga2O3 paper లో site preference evidence దొరికింది; కానీ XAS crystal కి ఖచ్చితమైన concentration tie చేయలేకపోయాం.
Graph చూసి మనమే exact number కల్పించలేదు. Ba-Sr paper లో coordination, symmetry wording conflicts కనిపించాయి.

10. ఇంకా ఏం మిగిలింది?
మరిన్ని independent materials, site-specific doping cases, స్పష్టమైన phase-temperature details అవసరం.
పాత 23 broad assertions ఇంకా withheld గానే ఉన్నాయి. Researchers ద్వారా independent review కూడా మిగిలింది.
Band-gap preservation, energy stability, final recommendation accuracy ఇంకా పరీక్షించలేదు.

11. ఏ మేరకు విజయవంతమైంది?
Code సరిగ్గా పనిచేస్తోందని executed tests చూపించాయి. అదే cached evidence తో అదే release మళ్లీ build అవుతోంది.
కానీ రెండు development references తో అన్ని elements మీద system accurate అని చెప్పలేం.
Dopant atoms సంఖ్య, free carriers సంఖ్య ఒకటి కాదు. ఎక్కువ Sn ఉన్న amorphous film కూడా resistive గా ఉండొచ్చని source చూపించింది.
ఆ observation ని అన్ని Sn substitutions విఫలం అన్న general rule గా మార్చలేదు.

12. తర్వాతి stage తో సంబంధం ఏమిటి?
Similarity engines ని పరీక్షించడానికి సరైన answer references సిద్ధం చేస్తున్నాం.
ఇప్పుడు ఉన్న cases development కోసం మాత్రమే. Held-out test set అంటే development లో ఉపయోగించని independent పరీక్ష cases;
అవి ఇంకా సిద్ధం కాలేదు. ఒకే host family కి చెందిన samples ని వేర్వేరు independent పరీక్షలుగా లెక్కించకూడదు.
Research hold ని స్పష్టంగా ఉంచి, మీ review తర్వాతే stage మారుస్తాం.
''')
    write(DOCS / 'completion_report.md', f'''# Stage 2 extended review — completion of this curation pass

Overall Stage 2 scientific benchmark status: incomplete. No Stage 3 work performed.

1. **Objective:** expand primary evidence and make remaining benchmark gaps explicit.
2. **Implemented:** additive v2.2 ledger, one experimental substitution scope, three unscored
   observations, all-23-assertion follow-up ledger, source-linked occupancy arithmetic and safeguards.
3. **Files created:** collect/build/report_extended_review.py; src/data_audit/evidence_extension.py;
   tests/stage_02/test_evidence_extension.py; raw extended sources; benchmark/v2_2_0;
   run_003 logs/results and this report directory.
4. **Files modified:** docs/progress.md and scoped .gitattributes rules. Earlier implementations,
   datasets, results and v2.0/v2.1 releases preserved; unrelated files not edited or committed.
5. **Methods:** primary-source reading and PDF visual review; hashes and passage locators;
   unchanged full-context admission gates; host-family/development labels; occupancy bookkeeping.
6. **Actual outputs:** four scoped candidate records total: one experimental and one computational
   substitution reference eligible, two inherited doping scopes held. Three additional observations
   unscored. Zero eligible doping references, zero held-out cases. All 23 broad original assertions
   retain unknown labels and specific next evidence requirements.
7. **Edge cases:** 38 new tests covering source integrity, overclaim prevention, units, detection
   limits and occupancy boundaries. Executed overwrite refusal and retrieval failures archived.
8. **Validation:** final {tests['tests']} tests passed in {tests['time']} s. Identical rebuild;
   {len(previous)} earlier tracked files checked. Software/local reproduction verified for this scope;
   scientific interpretation single-reviewer only; expert and clean-machine validation pending.
9. **Known issues:** unavailable PDF routes, ambiguous Ba/Sr source descriptions, incomplete exact
   Sn concentration link, and correction/publication-version checks still needed for other leads.
10. **Scientific limitations:** tiny development-only, predominantly positive seed; no independent
    performance estimate, property preservation, equilibrium stability or all-element coverage proof.
11. **Incomplete:** representative benchmark, role/site-specific doping evidence, independent expert
    adjudication, held-out cases, future engine hardening and all subsequent approved stages.
12. **Telugu:** full narration script in telugu_transcript.md. No playable audio generated because
    this tool environment has no speech-generation capability.
13. **Readiness:** this evidence pass is reviewable; scientific benchmark gate remains open. Continue
    Stage 2 curation. Do not treat successful tests or one experimental reference as stage-wide
    scientific certification. Stage advancement needs the owner's informed approval.

Open index.html for figures and the 23-assertion table. implementation_and_math.md explains
each new file, its inputs/outputs, execution, verification, formula and limits.
''')
    columns = ('case_id', 'track', 'target', 'candidate', 'status', 'next_evidence_needed')
    rows = ''.join('<tr>' + ''.join('<td>' + html.escape(str(d[k])) + '</td>' for k in columns) + '</tr>' for d in release['legacy_decisions'])
    docs = ['completion_report.md', 'scientific_review.md', 'implementation_and_math.md', 'edge_case_and_validation_report.md', 'telugu_transcript.md']
    links = ''.join(f'<li><a href="{name}">{name}</a></li>' for name in docs)
    write(DOCS / 'index.html', '<!doctype html><meta charset="utf-8"><title>MATRA Stage 2 extended evidence review</title>'
          '<style>body{font:16px system-ui;max-width:1200px;margin:30px auto;padding:20px;color:#203047}img{max-width:100%}td,th{padding:10px;border:1px solid #ccd2d8;vertical-align:top}table{border-collapse:collapse}th{background:#eef2f6}p{line-height:1.6}</style>'
          f'<h1>MATRA: Stage 2 extended evidence review</h1><p><strong>Research benchmark remains incomplete.</strong> {tests["tests"]} software tests passed. '
          'One experimental and one computational substitution reference are eligible; zero doping and zero held-out cases. These counts are not accuracy.</p>'
          '<img alt="Source-reported Se occupancy, not model prediction" src="../../../results/stage_02/run_003/source_site_occupancy.png">'
          '<img alt="Evidence readiness, not accuracy" src="../../../results/stage_02/run_003/evidence_readiness.png">'
          '<ul>' + links + '</ul><h2>Original assertion follow-up ledger</h2><p>All 23 assertions remain withheld at their original broad scope. Unknown does not mean false.</p>'
          '<table><thead><tr>' + ''.join('<th>' + k + '</th>' for k in columns) + '</tr></thead><tbody>' + rows + '</tbody></table>')
    link_targets = re.findall(r'(?:href|src)="([^"]+)"', (DOCS / 'index.html').read_text(encoding='utf-8'))
    if not all((DOCS / target).is_file() for target in link_targets): raise ValueError('Broken report link')
    directories = ['data/raw/stage_02_extended_sources', 'data/benchmark/v2_2_0', 'docs/stages/stage_02_extended_review']
    files = [path for directory in directories for path in sorted((ROOT / directory).rglob('*')) if path.is_file()]
    files += [ROOT / 'src/data_audit/evidence_extension.py', ROOT / 'tests/stage_02/test_evidence_extension.py']
    files += sorted((ROOT / 'experiments/stage_02').glob('*extended*.py'))
    manifest = {'files': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                'links_verified': len(link_targets), 'new_tests': 38, 'scientific_expert_review': 'pending'}
    write(RUN / 'artifact_manifest.json', json.dumps(manifest, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
