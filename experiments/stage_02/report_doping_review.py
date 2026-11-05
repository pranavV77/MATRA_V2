"""Create an auditable Stage 2 supplement from actual review/test artifacts."""
from pathlib import Path
import hashlib
import html
import json
import platform
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.stage_02.build_doping_review import build_review
from src.data_audit.doping_review import validate_doping_review

DOCS = ROOT / 'docs/stages/stage_02_doping_review'
RUN = ROOT / 'results/stage_02/run_004'


def write(path, content):
    with path.open('x', encoding='utf-8') as stream: stream.write(content)


def main():
    review = json.loads((ROOT / 'data/benchmark/doping_review_v1_0_0/doping_evidence.json').read_text(encoding='utf-8'))
    counts = validate_doping_review(review, ROOT)
    if build_review() != review: raise ValueError('Review rebuild differs')
    suite = ET.parse(ROOT / 'logs/stage_02/run_004/pytest.xml').getroot().find('testsuite')
    tests = {key: suite.attrib[key] for key in ('tests', 'failures', 'errors', 'skipped', 'time')}
    if tests['failures'] != '0' or tests['errors'] != '0': raise ValueError('Failed tests remain')
    previous = json.loads((RUN / 'starting_hashes.json').read_text(encoding='utf-8'))
    changed = [p for p, h in previous.items() if not (ROOT / p).is_file() or hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h]
    if set(changed) - {'.gitattributes', 'docs/progress.md'}: raise ValueError('Unexpected earlier-file changes')
    verification = {'workspace': str(ROOT), 'python': sys.version, 'operating_system': platform.platform(),
                    'counts': counts, 'tests': tests, 'previous_files_checked': len(previous), 'changed_previous_files': changed,
                    'identical_local_rebuild': True, 'new_prediction_or_dft_run': False,
                    'independent_scientific_adjudication': 'pending', 'clean_machine_reproduction': 'not tested'}
    write(RUN / 'verification.json', json.dumps(verification, indent=2))
    quantities = review['mg_site_study']['quantities']
    table = '\n'.join(f"| {q['kind']} | {q['relation']} {q['values']} | {q['unit']} | {q['specimen_relation']} |" for q in quantities)
    write(DOCS / 'scientific_review.md', '''# Doping evidence review: Si, Mg, Nb

No new full-context activation benchmark case is admitted. Existing substitution references
and the v2.2 ledger are unchanged. Source evidence is not a MATRA prediction.

## Mg-GaN: direct site evidence, with a crucial specimen limitation

Wahl et al., DOI 10.1103/PhysRevLett.118.095501, study radioactive 27Mg implanted into
wurtzite GaN. Methods specify stable predoping, probe profiles, fluence and sample treatment.
The authors explicitly state that their actual p-GaN specimens were not electrically
characterized; typical Hall numbers are from similar specimens. Those values cannot establish
activation efficiency for the implanted samples. C-axis alignment alone cannot distinguish
all positions along that axis; off-axis patterns provide the site discrimination. Reported
fit fractions are retained without conversion into calibrated probabilities.

The local archive is a web-tool text extraction, publisher lines 0–396, not a downloaded
PDF. Direct CERN access returned a bot page and the APS download returned 401. The readable
web extraction provided the inspected methods/results. End matter was not fully archived,
and no claim is made that PDF figures were visually verified locally.

Primary source: https://harvest.aps.org/v2/journals/articles/10.1103/PhysRevLett.118.095501/fulltext

## Si-Ga2O3: useful primary lead, full context pending

Iwaya et al., DOI 10.1063/1.3578195, report STM/spectroscopic evidence for substitutional
Si donors in beta-Ga2O3. Full local methods, exact concentration and specific Ga-site assignment
were not obtained. Do not infer an octahedral site from the Sn case. The earlier Villora
electrical-conductivity abstract remains supporting context, not interchangeable specimen data.

Primary source: https://doi.org/10.1063/1.3578195

## Nb-SrTiO3: processing can change incorporation

Jeong et al., DOI 10.1021/nn401101y, contrast bulk substitutional doping with insulating
films containing inferred inactive interstitial Nb. This is an abstract-level lead; full local
sample concentrations, methods and exact matched site/transport evidence are still required.
It is neither a universal negative label for Nb nor a guarantee that every bulk sample activates.
Crossref metadata is archived; the primary abstract was read via web, not treated as full text.

Primary source: https://pubs.acs.org/doi/10.1021/nn401101y

## Quantity table — conventions retained

| Quantity | Relation and values | Unit | Specimen relationship |
|---|---|---|---|
''' + table + '''

The 31% interstitial and 72% c-axis-aligned values are the source's fit outputs, not
a normalized 100% population partition or MATRA confidence. Do not apply the previous
fully occupied crystallographic-table sum rule to these fitted channeling components.
No activation fraction was computed from Hall values on similar specimens.

## What is still missing

Matched specimen identity, concentration/profile convention, phase/site characterization and
electrical activation evidence must be traceable together. Full texts for the Si STM and Nb
interstitial papers would improve curation, but access alone does not guarantee a complete
benchmark. Independent expert adjudication and held-out cases remain pending. All 23 broad
legacy assertions remain unknown; the two previously eligible substitution development
references remain the only admitted candidate references.
''')
    write(DOCS / 'implementation_and_validation.md', r'''# Implementation, reasoning and actual validation

Files created and their responsibilities:

- collect_doping_sources.py: retrieves three DOI metadata records and public paper URLs;
  stores raw responses, failures and starting hashes. No previous run is overwritten.
- collect_doping_alternative.py: attempts the discovered publisher full-text URL. The attempt
  returned HTTP 401; no PDF was saved. publisher_alternative_failure.json records that outcome.
- build_doping_review.py: reads the preserved v2.2 benchmark and source extraction, then creates
  a separate, unscored doping supplement. Its seven quantities have explicit kinds, units,
  relations, specimen relationships and source line anchors. Repeat execution refuses overwrite.
- src/data_audit/doping_review.py: validate_quantity checks units/ranges/bounds and finite values;
  validate_doping_review also checks hashes, traceable passages, specimen relationships and
  prohibition of unvalidated benchmark or activation claims. It does not predict dopant behavior.
- tests/stage_02/test_doping_review.py: 29 new executed tests using actual source passages and
  damaged records. Reported raw fit values and missing activation data are preserved.
- report_doping_review.py: reads actual JUnit/review files and writes reports, a quantity table,
  preservation checks and artifact hashes. No model training, prediction or DFT calculation.

## Scientific concepts

Number density is atoms or carriers per volume: N/V, with units cm^-3. Fluence is implanted
ions per area: N/A, with units cm^-2. Converting between these requires a depth profile; no
uniform-depth conversion was used for the radioactive implantation experiment.

Stable Mg already present in an epilayer, short-lived implanted 27Mg, and mobile holes are
different populations. Equal units do not make their quantities interchangeable. A bound
such as probe density <3e14 is not an exact measurement of 3e14. A reported range is not
silently replaced by its midpoint. No radioactive-decay or implantation-profile simulation ran.

Electrical activation means incorporated dopants produce electrically active states/carriers.
Site occupation is evidence about location, not sufficient proof of carrier production.
An apparent ratio of holes to Mg would require matching specimens, populations, measurement
conditions and a justified compensation model. The current supplement supplies no such ratio.

The validator checks provenance and declared policy, not the truth of a scientific interpretation.
Numerical extraction and single-reviewer judgments still need independent scientific review.

## Executed tests and edge cases

The full suite passed 172 tests (143 previous + 29 new), zero failures/errors/skips.
Actual JUnit and runtime are in logs/stage_02/run_004/pytest.xml. New cases: identical rebuild,
saved-ledger equality, distinct densities/fluence, retained raw fitted fractions, wrong units,
NaN/infinity/boolean/negative quantities, reversed ranges, missing specimen basis, fraction
over 100%, invalid relation, wrong value count, invented activation/efficiency, normalized fit
overclaim, false held-out designation, undeserved benchmark credit, unknown-to-negative
labeling, bad checksum, escaped path, missing passage, invalid line range, specimen mix-up,
false PDF archive designation, missing quantity, duplicate lead and zero-fit boundary.

A second builder invocation actually raised FileExistsError. Source-request failures are
archived and are not passed off as retrieved papers. pip check reported no broken requirements.
No scientific performance test or cross-machine reproduction was run. Pytest runtime is not
prediction latency. Browser/network failures are observations, not chemistry failures.

## Verification categories

Functionality and local cached-data rebuild: verified for the executed scope.
Source interpretation: partially verified, independent adjudication pending.
Full dilute-doping benchmark, activation accuracy and property preservation: not verified.
All-element generalization, held-out evaluation and clean-machine reproduction: not verified.
Earlier engine audit failures remain assigned to Stage 3; passing tests do not erase them.

From C:Final Project, run a fresh test base directory:

    .venvScriptspython.exe -m pytest tests --basetemp="C:Final Projectworkstage_02doping_reviewpytest_NEW" -q

pytest clears the selected base directory; use a new name. Read-only review verification:

    .venvScriptspython.exe -c "from pathlib import Path;import json;from src.data_audit.doping_review import validate_doping_review;p=Path.cwd();print(validate_doping_review(json.loads((p/'data/benchmark/doping_review_v1_0_0/doping_evidence.json').read_text(encoding='utf-8')),p))"

No production module was changed. The new supplement is not automatically activated in an
engine. To roll back, use the earlier benchmark; no deletion or migration is needed.
''')
    write(DOCS / 'telugu_transcript.md', '''# తెలుగు narration — Stage 2 doping evidence

Playable Telugu audio generate చేయలేదు. ఈ tool environment లో speech-generation సౌకర్యం లేదు.
ఇది text-to-speech కోసం ఉపయోగించగల పూర్తి narration script.

1. ఈ భాగంలో మనం ఏం చేస్తున్నాం?
Si, Mg, Nb doping గురించి primary research evidence పరిశీలిస్తున్నాం.
మన model ని evaluate చేయడానికి సరైన reference cases సిద్ధం చేయడమే ఈ పని.

2. ఎందుకు అవసరం?
ఒక element material లో చేరిందంటే అది తప్పకుండా electricity కోసం ఉపయోగపడుతుందని చెప్పలేం.
అది ఎక్కడ కూర్చుంది, ఎంత ఉంది, free carriers ఏర్పడ్డాయా అనే విషయాలు విడివిడిగా నిర్ధారించాలి.

3. ఏం implement చేశాం?
పాత benchmark మార్చకుండా doping evidence supplement, quantity validation మరియు specimen identity checks చేశాం.
కొత్త complete doping success case చేర్చలేదు. Unknown ని failure గా కూడా మార్చలేదు.

4. ఏ technologies వాడాం?
Local Python, JSON, hashes, pytest, source passage review వాడాం.
కొత్త neural network train చేయలేదు; DFT లేదా laboratory experiment కూడా చేయలేదు.

5. Scientific concepts ఎలా పనిచేస్తాయి?
Number density అంటే ఒక volume లో ఎన్ని atoms లేదా carriers ఉన్నాయో చెప్పే సంఖ్య.
దానికి cm^-3 units ఉంటాయి. Fluence అంటే ఒక area మీద పడిన implanted ions సంఖ్య; దానికి cm^-2 units ఉంటాయి.
ఇవి ఒకటి కావు. Depth profile తెలియకుండా ఒకదాన్ని ఇంకొకదిగా మార్చకూడదు.
Stable Mg, radioactive Mg probe, mobile holes కూడా వేర్వేరు populations.

6. ఏ results వచ్చాయి?
మూడు source leads review చేశాం. Mg experiment లో ఏడు quantities ని విడిగా నమోదు చేశాం.
మొత్తం 172 software tests pass అయ్యాయి. పూర్తి context ఉన్న కొత్త doping benchmark cases మాత్రం సున్నా.

7. Results అర్థం ఏమిటి?
Mg paper లో study చేసిన అసలు samples మీద electrical characterization చేయలేదని authors స్పష్టంగా చెప్పారు.
అందులో చెప్పిన typical Hall values ఇలాంటి ఇతర samples కి చెందినవి.
వాటిని ఈ sample Mg density తో కలిపి activation efficiency calculate చేస్తే తప్పు conclusion వస్తుంది.
Site evidence ఉపయోగపడుతుంది, కానీ అది electrical activation proof కాదు.

8. ఏ edge cases పరీక్షించాం?
తప్పు units, NaN, infinity, boolean, negative values, తలకిందులైన ranges, లేని specimen identity పరీక్షించాం.
ఇతర samples measurements ని ఈ sample కి అంటించడం, false accuracy credit, తప్పుడు source passage,
మారిన hash, లేని quantity, తప్పు archive format కూడా reject అవుతాయా చూశాం.

9. ఏ సమస్యలు వచ్చాయి?
కొన్ని download routes 403 లేదా 401 ఇచ్చాయి; CERN route bot page ఇచ్చింది.
వాటిని దాటడానికి ప్రయత్నించలేదు. Mg paper text web tool ద్వారా చదవగలిగాం; దాన్ని text extraction గానే archive చేశాం.
PDF download అయిందని చెప్పలేదు. Figures ని local PDF లో visually verify చేశామని కూడా చెప్పడం లేదు.

10. ఇంకా ఏం మిగిలింది?
Si మరియు Nb papers పూర్తి methods, concentration, site మరియు sample-specific electrical data అవసరం.
Independent expert review, కొత్త hosts, held-out tests కూడా మిగిలాయి.
Band gap, stability preservation ఇంకా evaluate చేయలేదు.

11. ఏ మేరకు విజయవంతమైంది?
Data కలిసిపోకుండా checks పనిచేస్తున్నాయని tests చూపించాయి. Saved evidence మళ్లీ అదే విధంగా build అవుతోంది.
Paper లోని 31 percent interstitial fit, 72 percent c-axis-aligned fit ని అలాగే ఉంచాం.
వాటిని మనమే 100 percent కి normalize చేయలేదు. ఇవి MATRA confidence values కావు.
C-axis alignment ఒక్కటే atom ఖచ్చితంగా Ga site లో ఉందని నిరూపించదు; off-axis measurements కూడా అవసరం.

12. తర్వాతి stage తో సంబంధం ఏమిటి?
Similarity engines తరువాత recommendations ఇస్తాయి. వాటిని scientific evidence తో పోల్చేటప్పుడు
location, concentration, activation వివరాలు కలిసిపోకుండా ఈ checks ఉపయోగపడతాయి.
Stage 3 ఇంకా మొదలుపెట్టలేదు. మిగిలిన evidence limitations ని స్పష్టంగా ఉంచి మీ review కోసం reports సిద్ధం చేశాం.
''')
    write(DOCS / 'completion_report.md', f'''# Stage 2 doping-source review — curation pass report

1. **Objective:** assess Si/Mg/Nb sources without conflating site location and activation.
2. **Implemented:** immutable supplement; seven typed quantities; specimen-identity, bounds,
   archive-format and overclaim guards. No new full-context doping admission.
3. **Created:** four experiments/stage_02 scripts (collect sources/alternative, build, report);
   src/data_audit/doping_review.py; tests/stage_02/test_doping_review.py; raw doping sources;
   doping_review_v1_0_0 data; run_004 logs/results; this report directory.
4. **Modified:** docs/progress.md and scoped .gitattributes. Earlier code/data/results preserved.
5. **Methods:** primary-text/abstract review, metadata resolution, hashes and passage anchors;
   typed units, explicit bounds/ranges, specimen identity. No new prediction algorithm.
6. **Actual results:** three leads, seven quantities distinguished. No new complete doping
   case or held-out case. Earlier two substitution development references unchanged.
7. **Executed edge cases:** 29 new tests; total {tests['tests']} passing tests, zero failures,
   errors or skips. Detailed cases in implementation_and_validation.md; overwrite refusal logged.
8. **Validation:** same cached review rebuilds identically; {len(previous)} previous tracked files
   checked. Software/local reproducibility verified for tested scope. Scientific adjudication pending.
9. **Known issues:** local full-text routes blocked; Mg study explicitly lacks electrical
   characterization of actual study specimens; Si/Nb full contextual evidence unavailable.
10. **Scientific limits:** no activation efficiency, calibrated probability, recommendation
    accuracy, property preservation or generalization result established.
11. **Incomplete:** matched site/concentration/transport cases; independent expert review;
    representative held-out benchmark and later implementation stages. All 23 broad old assertions
    remain withheld. Earlier Stage 1 engine issues remain unresolved until Stage 3.
12. **Telugu:** complete narration script in telugu_transcript.md. No playable audio generated.
13. **Readiness:** this source-review pass is delivered. Stage 2 scientific benchmark remains
    incomplete; Stage 3 not started. A stage transition still requires informed owner approval.

Tables are used instead of a misleading numeric comparison plot because the quantities
have different units/populations and no MATRA predictions were produced. Source extraction
is honestly marked as web text, with partial coverage, not a downloaded PDF.
''')
    docs = ['completion_report.md', 'scientific_review.md', 'implementation_and_validation.md', 'telugu_transcript.md']
    links = ''.join(f'<li><a href="{p}">{p}</a></li>' for p in docs)
    rows = ''.join('<tr>' + ''.join('<td>' + html.escape(str(q[k])) + '</td>' for k in ('kind', 'relation', 'values', 'unit', 'specimen_relation')) + '</tr>' for q in quantities)
    write(DOCS / 'index.html', '<!doctype html><meta charset="utf-8"><title>MATRA doping evidence review</title>'
          '<style>body{font:16px system-ui;max-width:1150px;margin:35px auto;padding:20px}td,th{border:1px solid #ccd2dc;padding:12px;text-align:left}table{border-collapse:collapse}p{line-height:1.6}</style>'
          f'<h1>Stage 2: doping evidence</h1><p><strong>{tests["tests"]} software tests passed. Zero new full-context doping cases.</strong> Site evidence and activation evidence remain separate. '
          'No held-out accuracy or property-preservation claim. Earlier benchmark releases are unchanged.</p><ul>' + links + '</ul>'
          '<h2>Source quantities and specimen relationships</h2><table><tr><th>Quantity</th><th>Relation</th><th>Values</th><th>Unit</th><th>Specimen relationship</th></tr>' + rows + '</table>'
          '<p>Other-sample Hall values cannot establish activation in the actual study specimens. Fit fractions were not normalized. Archive is partial web text, not a downloaded PDF.</p>')
    targets = re.findall(r'href="([^"]+)"', (DOCS / 'index.html').read_text(encoding='utf-8'))
    if not all((DOCS / p).is_file() for p in targets): raise ValueError('Broken report link')
    files = [p for directory in ('data/raw/stage_02_doping_sources', 'data/benchmark/doping_review_v1_0_0', 'docs/stages/stage_02_doping_review') for p in sorted((ROOT / directory).rglob('*')) if p.is_file()]
    files += [ROOT / 'src/data_audit/doping_review.py', ROOT / 'tests/stage_02/test_doping_review.py'] + sorted((ROOT / 'experiments/stage_02').glob('*doping*.py'))
    write(RUN / 'artifact_manifest.json', json.dumps({'files': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}, 'links_verified': len(targets)}, indent=2))
    print(json.dumps(verification, indent=2))


if __name__ == '__main__': main()
