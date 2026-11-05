"""Admission checks use real cached source passages, with adversarial mutations."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from experiments.stage_02.build_primary_review import build_release
from src.data_audit.primary_evidence import validate_primary_evidence
from src.data_audit.validation import DataValidationError

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def release():
    return build_release()


def test_review_rebuild_is_deterministic(release):
    assert release == build_release()
    assert validate_primary_evidence(release, ROOT) == {
        'reviewed_claims': 3, 'eligible_experimental': 0,
        'eligible_computational': 1, 'held': 2}


def test_final_saved_release_matches_builder(release):
    saved = json.loads((ROOT / 'data/benchmark/v2_1_0/primary_evidence_reviewed.json').read_text(encoding='utf-8'))
    assert saved == release


@pytest.mark.parametrize('change', [
    'duplicate_claim', 'duplicate_source', 'invalid_element', 'self_substitution',
    'unknown_credit', 'missing_phase', 'bool_concentration', 'nan_concentration',
    'negative_concentration', 'overfull_fraction', 'unknown_unit', 'missing_basis',
    'missing_passage', 'invalid_lines', 'altered_hash', 'escaped_path',
    'missing_source', 'metadata_credit', 'property_credit', 'missing_doi',
])
def test_rejects_invalid_evidence(release, change):
    claim = release['reviewed_claims'][0]
    source = next(s for s in release['sources'] if s['source_id'] == claim['source_id'])
    concentration = claim['reported_concentration']
    if change == 'duplicate_claim': release['reviewed_claims'].append(copy.deepcopy(claim))
    elif change == 'duplicate_source': release['sources'].append(copy.deepcopy(source))
    elif change == 'invalid_element': claim['candidate'] = 'Unobtainium'
    elif change == 'self_substitution': claim['candidate'] = claim['target']
    elif change == 'unknown_credit': claim['label'] = 'unknown'
    elif change == 'missing_phase': claim['conditions']['phase']['status'] = 'unverified'
    elif change == 'bool_concentration': concentration['value'] = True
    elif change == 'nan_concentration': concentration['value'] = float('nan')
    elif change == 'negative_concentration': concentration['value'] = -0.5
    elif change == 'overfull_fraction': concentration['value'] = 1.01
    elif change == 'unknown_unit': concentration['unit'] = 'percent'
    elif change == 'missing_basis': concentration['basis'] = ''
    elif change == 'missing_passage': claim['conditions']['site']['anchors'] = ['fabricated observation']
    elif change == 'invalid_lines': claim['conditions']['site']['line_start'] = 0
    elif change == 'altered_hash': source['document']['sha256'] = '0' * 64
    elif change == 'escaped_path': source['document']['path'] = '../outside.pdf'
    elif change == 'missing_source': claim['source_id'] = 'not-a-source'
    elif change == 'metadata_credit': source['access'] = 'metadata_only'
    elif change == 'property_credit': claim['property_preservation_validated'] = True
    elif change == 'missing_doi': source['verified_doi'] = ''
    with pytest.raises(DataValidationError):
        validate_primary_evidence(release, ROOT)


def test_challenge_not_full_text_even_with_matching_hashes(release, tmp_path):
    source = next(s for s in release['sources'] if s['source_id'] == 'GaAl_HSE')
    page = tmp_path / 'challenge.html'
    page.write_text('Client Challenge\n' + 'x' * 2000, encoding='utf-8')
    reference = {'path': 'challenge.html', 'sha256': hashlib.sha256(page.read_bytes()).hexdigest()}
    source['text'] = reference.copy()
    source['document'] = reference.copy()
    # A minimal release isolates access validation before passage validation.
    release['sources'] = [source]
    release['reviewed_claims'] = [release['reviewed_claims'][0]]
    with pytest.raises(DataValidationError, match='Challenge'):
        validate_primary_evidence(release, tmp_path)


def test_missing_file_is_rejected(release, tmp_path):
    with pytest.raises(DataValidationError, match='missing'):
        validate_primary_evidence(release, tmp_path)


def test_legacy_23_claims_remain_withheld():
    old = json.loads((ROOT / 'data/benchmark/v2_0_0/benchmark_review.json').read_text(encoding='utf-8'))
    claims = [c for group in ('substitution_cases', 'doping_cases') for case in old[group] for c in case['claims']]
    assert len(claims) == 23
    assert not any(c['eligible_for_quantitative_evaluation'] for c in claims)


def test_rejected_initial_nb_identifier_is_preserved(release):
    source = next(s for s in release['sources'] if s['source_id'] == 'Nb_STO')
    assert source['candidate_doi'] != source['verified_doi']
    assert source['verified_doi'] in (ROOT / source['text']['path']).read_text(encoding='utf-8')


@pytest.mark.parametrize('change', ['empty_sources', 'empty_claims', 'missing_id', 'invalid_url_type', 'invalid_conditions_type', 'invalid_concentration_type'])
def test_malformed_inputs_fail_explicitly(release, change):
    if change == 'empty_sources': release['sources'] = []
    elif change == 'empty_claims': release['reviewed_claims'] = []
    elif change == 'missing_id': del release['sources'][0]['source_id']
    elif change == 'invalid_url_type': release['sources'][0]['url'] = 7
    elif change == 'invalid_conditions_type': release['reviewed_claims'][0]['conditions'] = None
    elif change == 'invalid_concentration_type': release['reviewed_claims'][0]['reported_concentration'] = None
    with pytest.raises(DataValidationError):
        validate_primary_evidence(release, ROOT)
