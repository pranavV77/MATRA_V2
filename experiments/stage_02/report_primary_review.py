"""Write review reports once, using actual release and pytest artifacts."""
from pathlib import Path
from collections import Counter
import hashlib
import html
import json
import os
import platform
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.data_audit.primary_evidence import validate_primary_evidence
from experiments.stage_02.build_primary_review import build_release

RESULTS = ROOT / 'results/stage_02/run_002'
DOCS = ROOT / 'docs/stages/stage_02_source_verification'
os.environ['MPLCONFIGDIR'] = str(RESULTS / 'matplotlib_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def write(path, content):
    with path.open('x', encoding='utf-8') as stream:
        stream.write(content)


def main():
    release = json.loads((ROOT / 'data/benchmark/v2_1_0/primary_evidence_reviewed.json').read_text(encoding='utf-8'))
    counts = validate_primary_evidence(release, ROOT)
    if release != build_release():
        raise ValueError('Saved release differs from reproducible builder')
    suite = ET.parse(ROOT / 'logs/stage_02/run_002/pytest_final.xml').getroot().find('testsuite')
    tests = {k: suite.attrib[k] for k in ('tests', 'failures', 'errors', 'skipped', 'time')}
    if tests['failures'] != '0' or tests['errors'] != '0':
        raise ValueError('Failed tests must not be reported as complete')
    previous = json.loads((RESULTS / 'starting_hashes.json').read_text(encoding='utf-8'))
    changed = [name for name, checksum in previous.items() if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != checksum]
    unexpected = [name for name in changed if name != 'docs/progress.md']
    if unexpected:
        raise ValueError(f'Unexpected previous-file changes: {unexpected}')
    inventory = dict(Counter(s['access'] for s in release['sources']))
    verification = {'python': sys.version, 'operating_system': platform.platform(), 'workspace': str(ROOT),
                    'source_inventory': inventory, 'evidence_counts': counts, 'pytest': tests,
                    'previous_tracked_files_checked': len(previous), 'changed_previous_files': changed,
                    'unexpected_previous_changes': unexpected, 'release_rebuilt_identically': True,
                    'clean_machine_reproducibility': 'not tested', 'expert_adjudication': 'pending'}
    write(RESULTS / 'verification.json', json.dumps(verification, indent=2))
    fig, ax = plt.subplots(figsize=(8, 4.6))
    values = [counts['eligible_computational'], counts['eligible_experimental'], counts['held']]
    bars = ax.bar(['Computational\ncontext complete', 'Experimental\ncontext complete', 'Held\ncontext incomplete'], values, color=['#5069a8', '#33877d', '#cd9751'])
    ax.bar_label(bars, padding=4)
    ax.set(ylim=(0, 3), ylabel='New narrowed claims (count)', title='Primary-source seed review: 3 claims')
    ax.set_yticks(range(4))
    fig.text(.5, .015, 'Evidence readiness counts; these are not model accuracy or chemical failure rates.', ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .04, 1, 1))
    for extension in ('png', 'svg'):
        path = RESULTS / f'evidence_readiness.{extension}'
        if path.exists(): raise FileExistsError(path)
        fig.savefig(path, dpi=160)
    plt.close(fig)
    source_rows = '\n'.join(f"| {s['source_id']} | {s['access']} | {s.get('verified_doi') or s.get('candidate_doi') or 'unverified'} | {s['note']} |" for s in release['sources'])
    write(DOCS / 'source_review.md', '''# Primary-source review ledger

This is a bounded curation pass, not completion of a representative benchmark.
Full text does not automatically establish every original assertion. Source identity,
material form, phase, site and concentration must match the particular claim.

| Source | Access/review status | DOI (candidate unless verified) | Decision |
|---|---|---|---|
''' + source_rows + '''

Three detailed source cards are stored in data/benchmark/v2_1_0/primary_evidence_reviewed.json,
including local extraction line ranges, exact anchor fragments, document/text SHA-256 hashes,
concentration conventions and limitations. These are single-reviewer decisions; independent
materials-expert adjudication is pending. The initial primary_evidence.json is retained as
an intermediate build; use primary_evidence_reviewed.json for the final reviewed release.

## What the three sources establish

- Wang et al., DOI 10.1103/PhysRevApplied.10.011003, author manuscript arXiv:1806.03360v2:
  a computed monoclinic AlGaO3 arrangement at cation fraction x=0.5, with octahedral Al
  and tetrahedral Ga. This is a computational reference, not experimental validation or
  evidence of preserved band gap. Figure 1 and the abstract were checked visually.
- Lin et al., DOI 10.1002/adma.201304985: atomic microscopy identifies Re on Mo sites
  in single-layer MoS2 and also observes Re adatoms. The reported concentration convention
  is retained. Bulk space-group/Wyckoff assumptions are not transferred to this monolayer.
  Figure 1 was inspected. Electrical activation is not independently established here.
- Zhang et al., DOI 10.1038/s41598-021-03199-7: Nb-doped SrTiO3 single crystals have
  explicitly defined weight-percent concentrations and nominal formulas. Selected passages
  do not establish direct occupancy refinement and a fully specified phase/temperature case.
  The acquisition DOI candidate was incorrect; article-header DOI corrected in the reviewed
  record while retaining the original acquisition history.

## Remaining scientific work

All 23 broad legacy assertions remain withheld in frozen v2.0.0. The new computed case
does not certify the broader old Ga–Al range. Other acquired papers require complete
claim review; sources available only as metadata need primary passages. Add independent
expert review, broader held-out host/site cases and documented counterexamples before
claiming benchmark representativeness. Absence of evidence is not a negative label.
''')
    write(DOCS / 'implementation.md', r'''# Implementation and execution

- experiments/stage_02/collect_primary_sources.py downloads public paper/metadata snapshots
  once and records failed requests. Candidate identifiers are search leads, not verified facts.
  No API credentials, remote execution or challenge bypass is used.
- experiments/stage_02/build_primary_review.py reads those snapshots and constructs the new
  scoped evidence ledger. It finds source-line locators and hashes both extraction and paper.
  A second execution refuses to overwrite existing outputs.
- src/data_audit/primary_evidence.py validates identities, units/bases, passage anchors,
  checksums and admission conditions. It returns readiness counts, never model accuracy.
  It rejects incomplete contextual claims from scoring but cannot prove a scientific reading
  is correct; independent review remains necessary.
- tests/stage_02/test_primary_evidence.py exercises cached real passages and deliberately
  damaged records, including inaccessible sources and misleading challenge pages.
- experiments/stage_02/report_primary_review.py reads actual JUnit results, verifies earlier
  tracked-file hashes, and produces reports and a readiness-count figure. No predictions run.

Run from C:Final Project:

    .venv\Scripts\python.exe -m pytest tests --basetemp="C:Final Projectworkstage_02primary_reviewpytest_NEW" -q

Use a fresh basetemp name: pytest clears its chosen base directory. The archived executed
command and JUnit are in logs/stage_02/run_002. To verify the saved release without modifying it:

    .venv\Scripts\python.exe -c "from pathlib import Path; import json; from src.data_audit.primary_evidence import validate_primary_evidence; p=Path.cwd(); print(validate_primary_evidence(json.loads((p/'data/benchmark/v2_1_0/primary_evidence_reviewed.json').read_text(encoding='utf-8')),p))"

Production similarity engines, feature releases and earlier benchmark records are unchanged.
The new native data is still not automatically activated in legacy engines. Rollback consists
of excluding this additive evidence release; no legacy migration is required.
''')
    write(DOCS / 'edge_case_report.md', f'''# Executed edge cases

Final full suite: {tests['tests']} tests, {tests['failures']} failures, {tests['errors']} errors,
{tests['skipped']} skipped; runtime {tests['time']} seconds. This includes 32 new evidence tests
and 73 earlier tests. JUnit: logs/stage_02/run_002/pytest_final.xml.

Executed cases: empty source/claim collections; missing IDs; duplicate source and claim IDs;
invalid element and self-substitution; unknown label earning credit; missing phase verification;
boolean, NaN, negative and overfull concentrations; unknown units and missing concentration
basis; absent passage anchors and out-of-range source lines; altered source checksum;
path traversal; missing files and source references; metadata-only evidence; challenge page
with an otherwise valid checksum; unsupported property-preservation assertion; missing DOI;
incorrect URL/conditions/concentration types; deterministic rebuild; final saved/build equality;
retained legacy unknowns; retained incorrect retrieval identifier alongside corrected DOI.

First test invocation used a nonexistent tests/stage_01 folder: collection failed and no
tests executed. It is retained in pytest.txt/pytest.xml. Corrected invocation ran tests/.
A docstring escape warning was then fixed. Final invocation passed without warnings.

Not tested: authenticated publisher retrieval, arbitrary website formats, every malformed
nested JSON possibility, clean-machine installation, independent scientific adjudication,
chemistry generalization or future prediction performance. No chemical negatives fabricated.
''')
    write(DOCS / 'validation_report.md', f'''# Validation classification

| Category | Status | Evidence / limitation |
|---|---|---|
| Functionality | Verified for tested behavior | {tests['tests']} passing tests; no new prediction code |
| Local reproducibility | Verified for this seed | Rebuilt ledger equals saved artifact; paper/text hashes checked |
| Previous work preservation | Verified | {len(previous)} tracked files checked; only intentional progress update permitted |
| Scientific source interpretation | Partially verified | Three scoped single-reviewer readings with passage locators; expert adjudication pending |
| Experimental benchmark readiness | Not verified | Zero new fully contextual experimental cases |
| Computational benchmark readiness | Seed only | One fully contextual computational case; too small for general conclusions |
| Accuracy/property preservation | Not evaluated | No MATRA predictions or band-gap/stability calculations run |
| Clean-machine reproducibility | Not yet verified | Existing Windows environment only |

The plotted counts measure evidence readiness, not recommendation correctness. One eligible
reference out of three reviewed scopes is a curation result, not 33% model accuracy. No
confusion matrix, precision/recall or error bars are appropriate for this evidence ledger.
The 23 historical assertions remain separate and withheld. Two held doping records are
not failed chemistry cases. All source access errors are retained in acquisition_manifest.json.
''')
    write(DOCS / 'telugu_transcript.md', '''# తెలుగు వివరణ — Stage 2 primary-source verification

Playable Telugu audio ఈ environment లో తయారు చేయలేదు. Telugu speech-generation సౌకర్యం
అందుబాటులో లేదు. కింద ఉన్నది text-to-speech కోసం ఉపయోగించగల పూర్తి narration script.

## 1. ఈ భాగంలో మనం ఏం చేస్తున్నాం?
మన MATRA కోసం ఉపయోగించే reference cases నిజంగా ఏ పరిశోధన ఆధారంగా ఉన్నాయో చూస్తున్నాం.
Reference case అంటే మన సిస్టమ్ ఇచ్చే సలహాను పోల్చి చూడటానికి ఉపయోగించే ఆధారంతో కూడిన ఉదాహరణ.
ఒక paper పేరు ఉండటం సరిపోదు. మనం చెప్పే విషయం ఆ paper లో నిజంగా ఉందా అనేది చూడాలి.

## 2. ఇది ఎందుకు అవసరం?
తప్పు answer key తో పరీక్ష దిద్దితే మంచి సమాధానానికి కూడా తప్పు మార్కులు రావచ్చు.
అలాగే benchmark తప్పుగా ఉంటే model accuracy కూడా నమ్మదగినది కాదు.
అందుకే ముందుగా evidence ని సరిచూస్తున్నాం. సమాచారం దొరకలేదంటే ఆ chemistry తప్పు అని కాదు.

## 3. ఏం implement చేశాం?
పాత files మార్చకుండా కొత్త evidence ledger తయారు చేశాం. ఇందులో source link, paper file hash,
ఏ passage ఆధారమో line numbers, material, phase, site, concentration వివరాలు ఉన్నాయి.
Hash అంటే file మారిందా అని గుర్తించడానికి ఉపయోగించే digital fingerprint లాంటిది.

## 4. ఏ technologies వాడాం?
Local Python, pathlib, JSON, SHA-256, pytest, matplotlib ఉపయోగించాం.
PDF text తో పాటు ముఖ్యమైన figures ని కూడా చూశాం. కొత్త neural network train చేయలేదు.
DFT అంటే electron ప్రవర్తనను quantum-mechanics ఆధారంగా లెక్కించే పద్ధతి.
ఈసారి మనం DFT నడపలేదు; పరిశోధకులు చేసిన calculation ని reference గా నమోదు చేశాం.

## 5. Evidence check ఎలా పనిచేస్తుంది?
మొదట file hash సరిపోతుందా చూస్తాం. తరువాత చెప్పిన passage నిజంగా text లో ఉందా చూస్తాం.
Host అంటే అసలు material. Phase అంటే దాని crystal arrangement. Site అంటే crystal లో atom కూర్చునే స్థానం.
Concentration అంటే ఎంత భాగాన్ని కొత్త element తో మార్చామో చెప్పే పరిమాణం.
ఈ నాలుగు విషయాలు నిర్ధారణ కాకపోతే full contextual scoring లో case చేరదు.
Software check interpretation ని తానే నిజం చేయలేదు; మన scientific review కూడా అవసరం.

## 6. ఏ ఫలితాలు వచ్చాయి?
పద్నాలుగు source leads screen చేశాం. వాటిలో మూడు sources నుంచి మూడు ప్రత్యేక claims ని వివరంగా పరిశీలించాం.
ఒక computational substitution case కి అవసరమైన context దొరికింది.
రెండు experimental doping records కి పూర్తి context లేకపోవడంతో quantitative scoring లో పెట్టలేదు.
చివరి test run లో మొత్తం 105 tests pass అయ్యాయి. ఇవి software tests మాత్రమే.

## 7. ఈ సంఖ్యల అర్థం ఏమిటి?
Ga-Al case లో x=0.5 అంటే మొత్తం Al మరియు Ga cation స్థానాల్లో సగం Al అన్నమాట.
అది dilute doping కాదు. Re-MoS2 paper లో Mo స్థానంలో Re కనిపించింది; కొన్ని Re atoms
surface మీద adatoms గా కూడా కనిపించాయి. అందువల్ల ప్రతి Re atom substitutional అని చెప్పలేం.
Nb-SrTiO3 paper లో wt% అంటే బరువు శాతం. దాన్ని atomic percentage గా నేరుగా మార్చకూడదు.
మూడు claims లో ఒకటి ready అంటే MATRA accuracy 33 percent అని అర్థం కాదు.

## 8. ఏ edge cases పరీక్షించాం?
ఖాళీ inputs, duplicate IDs, తప్పు element పేరు, negative concentration, NaN, boolean value,
తప్పు units, లేని source file, మారిన checksum, project బయటకు వెళ్లే path, లేని passage,
metadata మాత్రమే ఉన్న source ని evidence గా చూపించడం వంటి పరిస్థితులు పరీక్షించాం.
Browser challenge page ని paper గా తీసుకోకుండా కూడా పరీక్షించాం.

## 9. ఏ సమస్యలు వచ్చాయి?
కొన్ని websites పూర్తి paper ఇవ్వలేదు. ఒక initial DOI తప్పుగా ఉంది; article header ఆధారంగా
సరైన DOI నమోదు చేసి పాత retrieval history అలాగే ఉంచాం. మొదటి test command లో లేని folder
ఇచ్చాం; దాన్ని సరిచేసి పూర్తి tests నడిపాం. ఆ failed attempt log కూడా అలాగే ఉంచాం.

## 10. ఇంకా ఏం మిగిలింది?
పాత 23 broad assertions ఇంకా scoring కి అంగీకరించలేదు. కొత్త narrow case వల్ల పాత పెద్ద
concentration range మొత్తం నిజమైపోదు. మరిన్ని primary passages, phase-specific details,
వేరే hosts, independent expert review అవసరం. Band gap లేదా stability preservation పరీక్షించలేదు.

## 11. ఏ మేరకు విజయవంతమైంది?
Evidence validation software పని చేస్తోందని, ఈ local release మళ్లీ అదే విధంగా build అవుతుందని
పరీక్షించాం. కానీ complete scientific benchmark సిద్ధమైందని చెప్పడం లేదు.
Graph లో కనిపించేవి evidence readiness counts మాత్రమే; material success rates కావు.

## 12. తర్వాతి stage తో సంబంధం ఏమిటి?
Similarity engines ని పరీక్షించేటప్పుడు trustworthy reference cases అవసరం.
ఇప్పటి evidence seed ఆ దిశగా చిన్న ముందడుగు. Stage 3 మొదలుపెట్టలేదు.
Research hold ని స్పష్టంగా ఉంచి, మిగిలిన evidence గురించి నిర్ణయం తీసుకున్న తర్వాతే ముందుకు వెళ్తాం.
''')
    write(DOCS / 'completion_report.md', f'''# Stage 2 primary-source verification review

Status: bounded curation pass delivered; Stage 2 scientific benchmark remains incomplete.

1. **Objective:** replace unsupported benchmark assumptions with traceable, scoped evidence.
2. **Implemented:** local source acquisition, three detailed source cards, evidence admission
   validator, deterministic additive release, adversarial tests and evidence-readiness figure.
3. **Files created:** three experiments/stage_02 scripts for collection/build/report;
   src/data_audit/primary_evidence.py; tests/stage_02/test_primary_evidence.py;
   data/raw/stage_02_primary_sources; data/benchmark/v2_1_0; run_002 logs/results;
   this report directory. Intermediate initial build retained separately.
4. **Files modified:** docs/progress.md only among previous tracked files. Legacy engines,
   original datasets and v2.0.0 release preserved; unrelated user changes excluded.
5. **Methods:** primary-source reading, PDF figure inspection, SHA-256, passage locators,
   explicit condition/unit gates; no new ML training or DFT calculations.
6. **Actual results:** 14 source leads screened, 3 detailed scoped claims. One computational
   substitution seed eligible; zero experimental fully contextual cases eligible; two doping
   scopes withheld. All 23 old broad assertions remain withheld. Graph is readiness only.
7. **Edge cases:** 32 new test cases; detailed executed and untested cases in edge_case_report.md.
8. **Validation:** {tests['tests']} full-suite tests passed in the final run; no failures,
   errors or skips. Rebuild identical; earlier tracked-file hashes checked. Source interpretation
   single-reviewer only; clean-machine reproducibility and expert adjudication pending.
9. **Known issues:** blocked/unavailable publisher responses, metadata-only references,
   one rejected retrieval DOI, incomplete experimental phase/site context. Logs retain failures.
10. **Scientific limits:** a single computed seed cannot establish ranking quality, coverage,
    equilibrium stability, band-gap preservation or reliable chemical recommendations.
11. **Incomplete:** representative held-out benchmark, remaining primary-source case curation,
    independent review, negative/counterexample evidence. Stage 1 engine issues still pending.
12. **Telugu:** complete narration script in telugu_transcript.md; no playable audio generated.
13. **Next-stage readiness:** engineering checks pass; research hold remains. Stage 3 has not
    started. Continue curation, or obtain informed owner approval for engine-only work while
    keeping scientific performance claims withheld. Do not describe this as a complete benchmark.

Read source_review.md for exact scope and implementation.md for commands. Final machine-readable
ledger is data/benchmark/v2_1_0/primary_evidence_reviewed.json. Verification evidence is
results/stage_02/run_002/verification.json. Nothing has been pushed to GitHub.
''')
    links = ['completion_report.md', 'source_review.md', 'implementation.md', 'edge_case_report.md', 'validation_report.md', 'telugu_transcript.md']
    items = ''.join(f'<li><a href="{p}">{html.escape(p)}</a></li>' for p in links)
    write(DOCS / 'index.html', '<!doctype html><meta charset="utf-8"><title>MATRA Stage 2 source verification</title>'
          '<style>body{font:17px system-ui;max-width:1000px;margin:40px auto;padding:20px}img{max-width:100%}table{border-collapse:collapse}td,th{padding:10px;border:1px solid #bbb}</style>'
          '<h1>MATRA Stage 2: primary-source verification</h1><p>Research hold remains. These are evidence-readiness counts, not model accuracy.</p>'
          '<table><tr><th>New scoped claims reviewed</th><th>Computational eligible</th><th>Experimental eligible</th><th>Held</th></tr>'
          f'<tr><td>3</td><td>1</td><td>0</td><td>2</td></tr></table><p>All 23 historical assertions remain withheld. Final full suite: {tests["tests"]} passing tests.</p>'
          '<img alt="Evidence readiness counts, not accuracy" src="../../../results/stage_02/run_002/evidence_readiness.png">'
          '<ul>' + items + '</ul>')
    print(json.dumps(verification, indent=2))


if __name__ == '__main__':
    main()
