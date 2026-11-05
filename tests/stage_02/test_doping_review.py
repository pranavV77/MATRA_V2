"""Reject specimen mixing and quantity conflation using the actual Mg source."""
import json
from pathlib import Path

import pytest

from experiments.stage_02.build_doping_review import build_review
from src.data_audit.doping_review import validate_doping_review, validate_quantity
from src.data_audit.validation import DataValidationError

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def review():
    return build_review()


def test_reproducible_saved_review(review):
    saved = json.loads((ROOT / 'data/benchmark/doping_review_v1_0_0/doping_evidence.json').read_text(encoding='utf-8'))
    assert saved == review == build_review()
    assert validate_doping_review(review, ROOT)['new_full_doping_cases'] == 0


def test_real_source_quantities_are_not_merged(review):
    values = {q['kind']: q for q in review['mg_site_study']['quantities']}
    assert values['stable_dopant_number_density']['values'] == [2e19]
    assert values['radioactive_probe_peak_density']['values'] == [3e14]
    assert values['radioactive_probe_peak_density']['relation'] == '<'
    assert values['implantation_fluence']['unit'] == 'cm^-2'
    assert values['hole_number_density']['specimen_relation'] == 'similar_specimens'
    assert values['hole_number_density']['values'] == [1e17, 2e17]
    assert review['mg_site_study']['activation_efficiency'] is None


def test_reported_fits_remain_unnormalized(review):
    values = {q['kind']: q['values'][0] for q in review['mg_site_study']['quantities']}
    assert values['interstitial_fit_fraction'] + values['c_axis_aligned_fit_fraction'] == 103
    assert review['mg_site_study']['fit_fractions_normalized'] is False
    # This is not the fully occupied crystallographic site table from the Se case.
    validate_doping_review(review, ROOT)


@pytest.mark.parametrize('change', ['wrong_unit', 'nan', 'infinity', 'boolean', 'negative', 'reversed_range',
                                   'missing_basis', 'bad_percent', 'bad_relation', 'wrong_length'])
def test_quantity_edge_cases(review, change):
    q = review['mg_site_study']['quantities'][3]
    if change == 'wrong_unit': q['unit'] = 'cm^-2'
    elif change == 'nan': q['values'][0] = float('nan')
    elif change == 'infinity': q['values'][0] = float('inf')
    elif change == 'boolean': q['values'][0] = True
    elif change == 'negative': q['values'][0] = -1
    elif change == 'reversed_range': q['values'].reverse()
    elif change == 'missing_basis': q['specimen_relation'] = ''
    elif change == 'bad_percent': q.update(kind='interstitial_fit_fraction', unit='%', values=[101], relation='=')
    elif change == 'bad_relation': q['relation'] = 'approximately_whatever'
    elif change == 'wrong_length': q['values'] = [1]
    with pytest.raises(DataValidationError): validate_quantity(q)


@pytest.mark.parametrize('change', ['false_activation', 'invented_efficiency', 'normalized_fits', 'false_holdout',
                                   'full_benchmark_credit', 'unknown_as_negative', 'checksum', 'outside_path',
                                   'missing_anchor', 'invalid_lines', 'similar_as_same', 'probe_as_similar',
                                   'wrong_archive_format', 'missing_quantity', 'duplicate_lead'])
def test_evidence_and_overclaim_guards(review, change):
    mg = review['mg_site_study']
    if change == 'false_activation': mg['same_specimen_electrical_measurement'] = True
    elif change == 'invented_efficiency': mg['activation_efficiency'] = .01
    elif change == 'normalized_fits': mg['fit_fractions_normalized'] = True
    elif change == 'false_holdout': mg['held_out'] = True
    elif change == 'full_benchmark_credit': review['leads'][0]['full_doping_benchmark_eligible'] = True
    elif change == 'unknown_as_negative': review['leads'][0]['label'] = 'documented_negative'
    elif change == 'checksum': review['artifacts'][0]['sha256'] = '0'*64
    elif change == 'outside_path': review['artifacts'][0]['path'] = '../outside.json'
    elif change == 'missing_anchor': mg['quantities'][0]['source_locator']['anchors'] = ['fabricated passage']
    elif change == 'invalid_lines': mg['quantities'][0]['source_locator']['line_start'] = 0
    elif change == 'similar_as_same': mg['quantities'][3]['specimen_relation'] = 'same_experiment'
    elif change == 'probe_as_similar': mg['quantities'][1]['specimen_relation'] = 'similar_specimens'
    elif change == 'wrong_archive_format': mg['archive_format'] = 'downloaded_publisher_pdf'
    elif change == 'missing_quantity': mg['quantities'].pop()
    elif change == 'duplicate_lead': review['leads'][2] = review['leads'][0].copy()
    with pytest.raises(DataValidationError): validate_doping_review(review, ROOT)


def test_zero_fit_fraction_boundary(review):
    q = review['mg_site_study']['quantities'][-1].copy()
    q['values'] = [0]
    validate_quantity(q)
