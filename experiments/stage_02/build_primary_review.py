r"""Create an additive, deliberately small primary-evidence seed release.

Run from the project: .venv\Scripts\python.exe experiments/stage_02/build_primary_review.py
Existing output files are never overwritten. No recommendation engine runs.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.data_audit.primary_evidence import validate_primary_evidence

RAW = ROOT / 'data/raw/stage_02_primary_sources'
OUT = ROOT / 'data/benchmark/v2_1_0'


def artifact(name):
    path = RAW / name
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def condition(source, description, anchors=None):
    if anchors is None:
        return {'status': 'unverified', 'description': description}
    lines = (ROOT / source['text']['path']).read_text(encoding='utf-8').splitlines()
    positions = [next(i for i, line in enumerate(lines, 1) if a in line) for a in anchors]
    return {'status': 'verified', 'description': description, 'line_start': min(positions), 'line_end': max(positions), 'anchors': anchors}


def build_release():
    manifest = json.loads((RAW / 'acquisition_manifest.json').read_text(encoding='utf-8'))
    sources = []
    full = {
        'GaAl_HSE': ('GaAl_HSE.pdf', 'GaAl_HSE_pages.txt', '10.1103/PhysRevApplied.10.011003'),
        'Re_MoS2': ('Re_MoS2.pdf', 'Re_MoS2_pages.txt', '10.1002/adma.201304985'),
        'Nb_STO': ('Nb_STO.html', 'Nb_STO_text.txt', '10.1038/s41598-021-03199-7'),
    }
    for entry in manifest:
        sid = entry['source_id']
        source = {'source_id': sid, 'url': entry['requested_primary_url'] or 'https://doi.org/' + entry['candidate_doi'],
                  'candidate_doi': entry['candidate_doi'], 'access': 'metadata_only',
                  'review_depth': 'screened_not_claim_curated', 'identity_verified': False,
                  'note': 'Metadata/abstract screening only; no quantitative admission.'}
        if sid in full:
            document, text, doi = full[sid]
            source.update(access='full_text', identity_verified=True, verified_doi=doi,
                          document=artifact(document), text=artifact(text), review_depth='scoped_claim_review',
                          note='Source identity and scoped passages reviewed; source values are not MATRA predictions.')
        elif sid in ('MoW_atomic', 'Nb_STO_polar'):
            source.update(access='blocked', note='Local HTML is a client challenge, not the paper. No full-text credit.')
        elif sid == 'Sn_Ga_XAS':
            source.update(access='unavailable', note='Repository retrieval returned HTTP 429; no local paper evidence.')
        elif sid in ('Al_Ga_Peelaers', 'BaSr_neutron'):
            source.update(access='acquired_unreviewed', note='PDF acquired; detailed claim and publication-version review pending. Not admitted.')
        if sid == 'Nb_STO':
            source['note'] = 'Acquisition candidate DOI was wrong and rejected. Correct DOI read from article header, line 44. No retrospective alteration of acquisition log.'
        sources.append(source)
    by_id = {s['source_id']: s for s in sources}
    ga, re, nb = (by_id[k] for k in ('GaAl_HSE', 'Re_MoS2', 'Nb_STO'))
    claims = [
        {'claim_id': 'CUR-SUB-GA-AL-MODEL-050', 'related_legacy_case': 'BM-P01', 'target': 'Ga', 'candidate': 'Al',
         'track': 'substitution', 'source_id': ga['source_id'], 'evidence_class': 'computational',
         'scope': 'Ordered monoclinic AlGaO3 model, Al on octahedral cation sites and Ga on tetrahedral sites, x=0.5 of cation sublattice.',
         'label': 'documented_positive', 'eligible': True, 'property_preservation_validated': False,
         'reported_concentration': {'value': 0.5, 'unit': 'fraction', 'basis': 'Al/(Al+Ga) cation fraction', 'kind': 'model'},
         'conditions': {
             'host': condition(ga, 'Ga2O3 alloy model.', ['Ga2O3 and (AlxGa1−x)2O3 alloys']),
             'phase': condition(ga, 'Monoclinic beta model, not a synthesis claim.', ['AlGaO3 in the monoclinic phase']),
             'site': condition(ga, 'Al octahedral; Ga tetrahedral, Fig. 1 also inspected.', ['Al occupying the octahedral sites', 'tetrahedral sites.']),
             'concentration': condition(ga, 'Model cation fraction x=0.5; not dilute doping.', ['withx=0.5'])},
         'limitations': ['Primary author manuscript arXiv:1806.03360v2 associated with journal DOI; no new DFT run.', 'Restricted model evidence, not experimental confirmation or equilibrium stability proof.', 'No band-gap preservation label; no unrestricted concentration-range endorsement.']},
        {'claim_id': 'CUR-DOP-MO-RE-SINGLELAYER', 'related_legacy_case': 'BM-S05', 'target': 'Mo', 'candidate': 'Re',
         'track': 'doping', 'source_id': re['source_id'], 'evidence_class': 'experimental',
         'scope': 'STEM-observed Re occupying Mo sites in single-layer MoS2; adatoms also observed.',
         'label': 'documented_positive', 'eligible': False, 'property_preservation_validated': False,
         'reported_concentration': {'value': 0.6, 'unit': 'at% as reported', 'basis': 'Figure 1 counts about 10 Re per about 1500 MoS2 unit cells; retained as reported, no conversion to all-atom fraction', 'kind': 'observed'},
         'conditions': {
             'host': condition(re, 'Single-layer MoS2, not bulk.', ['single-layered MoS']),
             'phase': condition(re, 'Bulk 2H space group/Wyckoff identity in legacy record not established for this single-layer observation.'),
             'site': condition(re, 'Mo-site occupation directly imaged, not every Re atom substitutional.', ['clearly shows that Re atoms sit at the Mo sites.']),
             'concentration': condition(re, 'Reported approximately 0.6 at%, source convention retained.', ['0.6 at% Re'])},
         'limitations': ['Full contextual benchmark held; useful site-occupancy reference only.', 'Reported 89% substitutional Re and 11% Re adatoms are microscopy population statistics, not MATRA accuracy.', 'Donor interpretation uses calculated electronic states; experimental electrical activation not established here.']},
        {'claim_id': 'CUR-DOP-TI-NB-WEIGHT', 'related_legacy_case': 'BM-S04', 'target': 'Ti', 'candidate': 'Nb',
         'track': 'doping', 'source_id': nb['source_id'], 'evidence_class': 'experimental',
         'scope': 'Nb-doped SrTiO3 single crystals; representative reported 0.1 wt% sample, nominal SrTi0.998Nb0.002O3.',
         'label': 'documented_positive', 'eligible': False, 'property_preservation_validated': False,
         'reported_concentration': {'value': 0.1, 'unit': 'wt%', 'basis': 'Mass of elemental Nb / total sample mass times 100; nominal formulas separately reported', 'kind': 'nominal'},
         'conditions': {
             'host': condition(nb, 'SrTiO3 single crystals.', ['Nb-doped SrTiO3 single crystals with Nb doping concentration']),
             'phase': condition(nb, 'Temperature-dependent transition investigated; exact phase-specific benchmark conditions require additional curation.'),
             'site': condition(nb, 'Nominal Ti substitution and ionic-radius interpretation; direct site-occupancy refinement not established in selected passage.'),
             'concentration': condition(nb, '0.1 wt% sample; Methods defines mass basis and lists nominal formulas.', ['00106 (001)-oriented Nb-doped SrTiO3', 'SrTi0.998Nb0.002O3'])},
         'limitations': ['Nominal chemistry is not independently measured site occupancy.', 'No wt%-to-at% substitution, no generic room/low-temperature phase equivalence.', 'Correct DOI differs from initial retrieval candidate and from legacy unrelated citation.']}
    ]
    return {'version': '2.1.0', 'purpose': 'Small source-audited seed, not a representative evaluation dataset',
            'legacy_release': 'data/benchmark/v2_0_0/benchmark_review.json',
            'legacy_claim_policy': 'All 23 original claims remain withheld in frozen v2.0.0; a new narrowed claim does not validate its original broader claim.',
            'review_method': 'Single technical reviewer; source identity, local full text, conditions and limitations checked. Independent materials-expert adjudication pending.',
            'sources': sources, 'reviewed_claims': claims}


def main():
    release = build_release()
    counts = validate_primary_evidence(release, ROOT)
    targets = [OUT / 'primary_evidence_reviewed.json', ROOT / 'results/stage_02/run_002/reviewed_evidence_counts.json']
    if any(p.exists() for p in targets):
        raise FileExistsError('Review outputs already exist; use a new version/run rather than overwrite')
    for path, value in zip(targets, (release, counts)):
        with path.open('x', encoding='utf-8') as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
