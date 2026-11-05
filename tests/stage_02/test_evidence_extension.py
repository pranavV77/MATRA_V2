"""Source-grounded occupancy checks and conservative evidence admission."""
from pathlib import Path
import json

import pytest

from experiments.stage_02.build_extended_review import build_release
from src.data_audit.evidence_extension import validate_extended_review, weighted_site_composition
from src.data_audit.validation import DataValidationError

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def release():
    return build_release()


def test_extension_matches_saved_release_and_rebuild(release):
    saved = json.loads((ROOT / 'data/benchmark/v2_2_0/extended_evidence.json').read_text(encoding='utf-8'))
    assert release == saved == build_release()
    assert validate_extended_review(release, ROOT) == {
        'reviewed_claims': 4, 'eligible_experimental': 1, 'eligible_computational': 1,
        'held': 2, 'legacy_assertions_reviewed': 23, 'unscored_observations': 3,
        'eligible_substitution': 2, 'eligible_doping': 0,
        'eligible_host_family_groups': 2, 'held_out_cases': 0}


def test_real_refinement_table_preserves_minor_disorder(release):
    check = release['site_occupancy_check']
    result = check['derived']
    assert result['listed_site_count'] == 9
    # Hexagonal-cell counts: 6*0.043 + 3*0.915, not 0.043+0.915.
    assert result['counts']['Se'] == pytest.approx(3.003)
    assert result['counts']['Te'] == pytest.approx(5.997)
    assert result['fractions_on_listed_sites']['Se'] == pytest.approx(1.001 / 3)
    assert result['uncertainty_propagated'] is False
    assert result['counts']['Se'] / 3 == pytest.approx(1.001)
    assert check['sites'][0]['occupancies']['Se'] > 0
    assert check['sites'][1]['occupancies']['Te'] > 0


def test_sn_carrier_and_dopant_densities_are_distinct(release):
    observation = release['unscored_observations'][1]
    assert observation['reported_sn_number_density']['value'] == 2.3e20
    assert observation['carrier_density_bound']['value'] == 3e16
    assert observation['resistivity_bound']['value'] == 2000
    assert observation['carrier_density_bound']['assumption']
    assert not observation['eligible_for_quantitative_evaluation']
    assert 'activation_efficiency' not in observation


@pytest.mark.parametrize('change', [
    'parent_hash', 'removed_old_claim', 'changed_old_scope', 'held_out_claim',
    'missing_group', 'incorrect_group', 'missing_legacy', 'duplicate_legacy',
    'false_negative', 'wrong_legacy_link', 'observation_credit', 'property_credit',
    'absent_observation_anchor', 'missing_observations', 'unknown_observation_kind',
    'density_unit', 'nonfinite_density', 'missing_bound_assumption', 'inverted_bound',
    'invented_efficiency', 'occupancy_result', 'occupancy_table_changed',
    'missing_source_row', 'wrong_multiplicity',
])
def test_extension_rejects_invalid_or_overstated_records(release, change):
    claim = release['reviewed_claims'][-1]
    obs = release['unscored_observations'][1]
    site = release['site_occupancy_check']['sites'][0]
    if change == 'parent_hash': release['parent_release']['sha256'] = '0' * 64
    elif change == 'removed_old_claim': release['reviewed_claims'].pop(0)
    elif change == 'changed_old_scope': release['reviewed_claims'][0]['scope'] = 'unrestricted all compositions'
    elif change == 'held_out_claim': claim['held_out'] = True
    elif change == 'missing_group': del claim['independence_group']
    elif change == 'incorrect_group': claim['independence_group'] = 'artificially_independent_new_sample'
    elif change == 'missing_legacy': release['legacy_decisions'].pop()
    elif change == 'duplicate_legacy': release['legacy_decisions'].append(release['legacy_decisions'][0].copy())
    elif change == 'false_negative': release['legacy_decisions'][0]['label'] = 'documented_negative'
    elif change == 'wrong_legacy_link': release['legacy_decisions'][0]['related_scoped_claims'] = [claim['claim_id']]
    elif change == 'observation_credit': obs['eligible_for_quantitative_evaluation'] = True
    elif change == 'property_credit': obs['property_preservation_validated'] = True
    elif change == 'absent_observation_anchor': obs['passages'][0]['anchors'] = ['fictional measurement']
    elif change == 'missing_observations': release['unscored_observations'] = []
    elif change == 'unknown_observation_kind': obs['kind'] = 'universal_doping_failure'
    elif change == 'density_unit': obs['reported_sn_number_density']['unit'] = 'wt%'
    elif change == 'nonfinite_density': obs['reported_sn_number_density']['value'] = float('inf')
    elif change == 'missing_bound_assumption': del obs['carrier_density_bound']['assumption']
    elif change == 'inverted_bound': obs['resistivity_bound']['relation'] = '<'
    elif change == 'invented_efficiency': obs['activation_efficiency'] = 0.0001
    elif change == 'occupancy_result': release['site_occupancy_check']['derived']['counts']['Se'] = 3
    elif change == 'occupancy_table_changed':
        site['occupancies'] = {'Se': .05, 'Te': .95}
        release['site_occupancy_check']['derived'] = weighted_site_composition(release['site_occupancy_check']['sites'])
    elif change == 'missing_source_row': site['source_rows']['Se'] = 'SeI 6c 0.000(0) 0 0 0 0'
    elif change == 'wrong_multiplicity':
        site['multiplicity'] = 2
        release['site_occupancy_check']['derived'] = weighted_site_composition(release['site_occupancy_check']['sites'])
    with pytest.raises(DataValidationError):
        validate_extended_review(release, ROOT)


@pytest.mark.parametrize('change', ['empty', 'duplicate', 'bool_multiplicity', 'zero_multiplicity', 'negative_occupancy', 'infinite_occupancy', 'bool_occupancy', 'overfull', 'underfull', 'invalid_element'])
def test_site_bookkeeping_edge_cases(change):
    sites = [{'site': '3a', 'multiplicity': 3, 'occupancies': {'Se': .9, 'Te': .1}}]
    if change == 'empty': sites = []
    elif change == 'duplicate': sites.append(sites[0].copy())
    elif change == 'bool_multiplicity': sites[0]['multiplicity'] = True
    elif change == 'zero_multiplicity': sites[0]['multiplicity'] = 0
    elif change == 'negative_occupancy': sites[0]['occupancies']['Se'] = -.1
    elif change == 'infinite_occupancy': sites[0]['occupancies']['Se'] = float('inf')
    elif change == 'bool_occupancy': sites[0]['occupancies']['Se'] = True
    elif change == 'overfull': sites[0]['occupancies']['Te'] = .2
    elif change == 'underfull': sites[0]['occupancies']['Te'] = .01
    elif change == 'invalid_element': sites[0]['occupancies'] = {'Unobtainium': 1}
    with pytest.raises(DataValidationError):
        weighted_site_composition(sites)


def test_fully_ordered_boundary_is_valid():
    result = weighted_site_composition([{'site': '3a', 'multiplicity': 3, 'occupancies': {'Se': 1, 'Te': 0}}])
    assert result['fractions_on_listed_sites'] == {'Se': 1, 'Te': 0}
