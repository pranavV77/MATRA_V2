"""Build v2.2 evidence without changing prior releases or running predictions."""
from pathlib import Path
import copy
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.stage_02.build_primary_review import condition
from src.data_audit.evidence_extension import validate_extended_review, weighted_site_composition

PARENT = ROOT / 'data/benchmark/v2_1_0/primary_evidence_reviewed.json'
LEGACY = ROOT / 'data/benchmark/v2_0_0/benchmark_review.json'


def artifact(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def full_source(sid, url, doi, directory, stem):
    directory = ROOT / directory
    return {'source_id': sid, 'url': url, 'verified_doi': doi, 'access': 'full_text',
            'identity_verified': True, 'review_depth': 'scoped_claim_and_limitations_review',
            'document': artifact(directory / (stem + '.pdf')), 'text': artifact(directory / (stem + '_pages.txt')),
            'note': 'Primary text reviewed locally; source observations are not MATRA predictions.'}


def passage(source, description, anchors):
    record = condition(source, description, anchors)
    record.pop('status')
    return record


def build_release():
    parent = json.loads(PARENT.read_text(encoding='utf-8'))
    sources = copy.deepcopy(parent['sources'])
    sn = full_source('Sn_Ga_XAS', 'https://www.osti.gov/servlets/purl/1371047', '10.1063/1.4938123', 'data/raw/stage_02_extended_sources', 'Sn_Ga_XAS')
    ba = full_source('BaSr_neutron', 'https://arxiv.org/abs/2007.00972', '10.48550/arXiv.2007.00972', 'data/raw/stage_02_primary_sources', 'BaSr_neutron')
    bi = full_source('BiTeSe_primary', 'https://arxiv.org/abs/1112.1648', '10.1103/PhysRevB.84.235206', 'data/raw/stage_02_extended_sources', 'BiTeSe_structure')
    bi['document_version'] = 'arXiv:1112.1648v1, author manuscript associated with PRB DOI'
    ba['document_version'] = 'arXiv:2007.00972; PDF journal header says Nuclear Science and Applications 28(1&2), 2019; publication status not independently adjudicated'
    sources = [sn if s['source_id'] == sn['source_id'] else ba if s['source_id'] == ba['source_id'] else s for s in sources] + [bi]
    claims = copy.deepcopy(parent['reviewed_claims'])
    families = {'BM-P01': 'Ga2O3_family', 'BM-S05': 'MoS2_family', 'BM-S04': 'SrTiO3_family', 'BM-P11': 'Bi2Te3_family'}
    for claim in claims:
        claim.update(independence_group=families[claim['related_legacy_case']], split_role='development_reference_only', held_out=False)
    claims.append({
        'claim_id': 'CUR-SUB-TE-SE-BI2TE2SE', 'related_legacy_case': 'BM-P11', 'target': 'Te', 'candidate': 'Se',
        'track': 'substitution', 'source_id': bi['source_id'], 'evidence_class': 'experimental',
        'label': 'documented_positive', 'eligible': True, 'property_preservation_validated': False,
        'scope': 'Bridgman-Stockbarger Bi2Te2Se crystal, room-temperature powder XRD model with Se primarily on inner chalcogen 3a sites and minor outer 6c mixing.',
        'reported_concentration': {'value': 1/3, 'unit': 'fraction', 'basis': 'Nominal Se/(Te+Se) chalcogen-sublattice fraction for Bi2Te2Se; not fraction of all atoms', 'kind': 'nominal'},
        'conditions': {
            'host': condition(bi, 'Bi2Te3-related tetradymite solid-solution family; investigated sample is Bi2Te2Se.', ['Bi2Se3 and Bi 2Te3 are isostructural']),
            'phase': condition(bi, 'Rhombohedral tetradymite-type layering; powder XRD collected at room temperature, not the 4 K transport state.', ['layers stack in the sequence', 'rhombohe', 'room temperature.']),
            'site': condition(bi, 'Table I: inner 3a Se occupancy 0.915(14), outer 6c Se occupancy 0.043(7); no perfect-order assumption.', ['SeII 3a 0.915(14)', 'SeI 6c 0.043(7)']),
            'concentration': condition(bi, 'Nominal 2:1 Te:Se model, checked against reported occupancy table.', ['with a 2:1 ratio of Te to Se'])},
        'limitations': ['One specific composition/preparation and structural observation; no full-composition-range claim.', 'Source also reports phase separation for differently processed samples; these are not interchangeable.', 'No independently validated preservation of band gap, stability or thermoelectric performance; no held-out evaluation.', 'Occupancy factors are refinement-model estimates, not independent bulk elemental analysis.'],
        'independence_group': 'Bi2Te3_family', 'split_role': 'development_reference_only', 'held_out': False})
    observations = [
        {'observation_id': 'OBS-SN-GA-OCTAHEDRAL', 'source_id': sn['source_id'], 'kind': 'site_preference',
         'scope': 'XAS model supports preferential octahedral Ga2-site Sn in beta-Ga2O3 single crystal.',
         'reported_concentration': None, 'eligible_for_quantitative_evaluation': False, 'property_preservation_validated': False,
         'passages': [passage(sn, 'EXAFS site alternatives and fitting residuals.', ['tion at the Ga2 octahedral site', 'R-factor ¼ 0.01', 'R-factor ¼ 0.05'])],
         'limitations': ['Specific Sn concentration of the XAS crystal is not tied to an exact tabulated value in reviewed text; figure points were not digitized.', 'EXAFS R-factor is a spectral fit residual, not model accuracy.', 'Not a fully contextual dilute-doping benchmark label.']},
        {'observation_id': 'OBS-SN-ALD-DETECTION-LIMIT', 'source_id': sn['source_id'], 'kind': 'electrical_activation_caution',
         'scope': 'Amorphous ALD film with substantial Sn content remains highly resistive; this is not a negative label for all Sn in Ga2O3.',
         'eligible_for_quantitative_evaluation': False, 'property_preservation_validated': False,
         'reported_sn_number_density': {'value': 2.3e20, 'unit': 'atoms cm^-3', 'origin': 'authors_estimate_from_RBS_stoichiometry'},
         'resistivity_bound': {'relation': '>', 'value': 2000, 'unit': 'ohm cm', 'origin': 'four_point_probe_detection_limit'},
         'carrier_density_bound': {'relation': '<=', 'value': 3.0e16, 'unit': 'cm^-3', 'origin': 'authors_conditional_upper_limit', 'assumption': 'mobility greater than 0.1 cm^2/(V s)'},
         'passages': [passage(sn, 'Sn concentration estimate and limited electrical detection.', ['to be 2.3 /C2 1020 and 2.9 /C2 1020', '>2000 X cm', 'By assuming a mobility of >0.1', 'carrier density is estimated to be 3.0 /C2 1016'])],
         'limitations': ['Transport result is detection-limited; carrier upper bound depends on an assumed mobility.', 'Carrier density is not the same quantity as dopant number density.', 'No activation-efficiency point estimate and no negative substitution ground truth inferred.']},
        {'observation_id': 'OBS-BA-SR-CONSISTENCY', 'source_id': ba['source_id'], 'kind': 'source_internal_inconsistency',
         'scope': 'Ba0.5Sr0.5TiO3 neutron-refinement source retained for review, with coordination and symmetry wording conflicts.',
         'eligible_for_quantitative_evaluation': False, 'property_preservation_validated': False,
         'passages': [passage(ba, 'Abstract and introduction give incompatible A-site coordination descriptions.', ['tetrahedral A site', 'cuboctahedral coordination']),
                      passage(ba, 'Table 4 lists unequal a/c and calls the intermediate sample pseudo-cubic.', ['3.9495 3.9517 3.9495 3.9517 3.9580 3.9518', 'Pseudo-'])],
         'limitations': ['Conflict is in source description, not evidence that Sr substitution is chemically impossible.', 'Exact space group/coordination claim remains withheld pending an independent consistent structural reference.', 'A 50% alloy must not be presented as dilute doping despite wording in the paper title.']}
    ]
    legacy = json.loads(LEGACY.read_text(encoding='utf-8'))
    needed = {
        'BM-P01': 'Separate Al and In primary experimental cases; concentration, phase and Ga-site evidence. Peelaers PDF is a proof copy and its published erratum needs review before importing numerical stability/band-gap claims.',
        'BM-P02': 'Primary AlGaN and InGaN samples with specified wurtzite phase, Ga site and composition; the Ambacher review alone is insufficient.',
        'BM-P03': 'Primary Mo-W sulfide passage matching layer count, local coordination and concentration; do not assign bulk Wyckoff sites to a monolayer.',
        'BM-P04': 'Full Gong primary paper and sample-specific S/Se site, layer form and concentration; abstract does not certify the whole asserted range.',
        'BM-P05': 'Separate BaTiO3 Zr, Sn and Hf structural cases, each with sample composition, phase and Ti-site evidence; cited DOI is unrelated.',
        'BM-P06': 'Independent consistent Ba/Sr or Ba/Ca structural reference with exact phase and composition; neutron lead has unresolved wording/symmetry conflicts.',
        'BM-P07': 'Separate SrTiO3 Zr and Hf primary structural cases; repair unrelated database identifier and verify B-site occupancy/composition.',
        'BM-P08': 'Separate Sr/Ba and Sr/Ca cases with phase-temperature and concentration evidence; mixed host/dopant studies cannot prove the unrestricted binary substitution claim.',
        'BM-P09': 'Cs-only Pb/Sn iodide primary alloy case with composition and actual alpha/beta/gamma phase at a specified temperature; exclude organic-cation examples and phase-mixed samples.',
        'BM-P10': 'Read Poudel full primary passages for actual Bi/Sb composition and cation-site structural evidence; transport improvement alone does not establish every asserted site/range.',
        'BM-P11': 'New Bi2Te2Se scope is documented; broad full-join phase/stability assertion still requires independent composition- and preparation-specific evidence.',
        'BM-S01': 'Full Si-doped beta-Ga2O3 sample concentration, Ga-site assignment and electrical activation evidence; corrected Villora abstract is not full context.',
        'BM-S02': 'Sn XAS supports octahedral preference, but obtain exact concentration tied to the XAS single crystal; do not substitute carrier density for dopant density.',
        'BM-S03': 'Full Mg-GaN sample concentration, Mg-site and treatment-dependent activation evidence; classic p-type abstract does not certify full site context.',
        'BM-S04': 'Nb-STO concentration and role are supported in selected sources; independent site occupancy and exact phase/temperature context still pending.',
        'BM-S05': 'Re-MoS2 monolayer occupancy supported; resolve phase/form scope and retain source concentration convention and adatom population separately.'}
    decisions = []
    for group in ('substitution_cases', 'doping_cases'):
        for case in legacy[group]:
            for old in case['claims']:
                decisions.append({'case_id': case['case_id'], 'candidate': old['candidate'], 'target': case['legacy_record']['target_element'],
                                  'track': case['track'], 'status': 'withheld', 'label': 'unknown',
                                  'reason': old['review_reason'], 'next_evidence_needed': needed[case['case_id']],
                                  'related_scoped_claims': [c['claim_id'] for c in claims if c['related_legacy_case'] == case['case_id'] and c['candidate'] == old['candidate']]})
    lines = (ROOT / bi['text']['path']).read_text(encoding='utf-8').splitlines()
    rows = {name: next(line for line in lines if line.startswith(name + ' ')) for name in ('SeI', 'TeI', 'SeII', 'TeII')}
    sites = [{'site': '6c', 'multiplicity': 6, 'occupancies': {'Se': .043, 'Te': .957}, 'source_rows': {'Se': rows['SeI'], 'Te': rows['TeI']}},
             {'site': '3a', 'multiplicity': 3, 'occupancies': {'Se': .915, 'Te': .085}, 'source_rows': {'Se': rows['SeII'], 'Te': rows['TeII']}}]
    return {'version': '2.2.0', 'parent_release': artifact(PARENT), 'legacy_release': artifact(LEGACY),
            'purpose': 'Development-only evidence seed with explicit holds; not a representative test benchmark',
            'sources': sources, 'reviewed_claims': claims, 'unscored_observations': observations,
            'legacy_decisions': decisions,
            'site_occupancy_check': {'source_id': bi['source_id'], 'source_locator': 'Table I, PDF page 5, hexagonal-cell Wyckoff multiplicities 6c and 3a', 'sites': sites, 'derived': weighted_site_composition(sites), 'limitations': 'Refinement-model bookkeeping only; covariance unavailable and no uncertainty propagation.'},
            'scientific_review': {'reviewers': 1, 'independent_adjudication': 'pending', 'held_out_dataset': 'not yet established', 'property_preservation': 'not evaluated'}}


def main():
    release = build_release()
    counts = validate_extended_review(release, ROOT)
    outputs = [(ROOT / 'data/benchmark/v2_2_0/extended_evidence.json', release),
               (ROOT / 'results/stage_02/run_003/evidence_counts.json', counts)]
    if any(path.exists() for path, _ in outputs):
        raise FileExistsError('Outputs exist; use a new version/run')
    for path, data in outputs:
        with path.open('x', encoding='utf-8') as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
