"""Fusion arithmetic and edge cases. Synthetic numbers are not material evidence."""
import math
import numpy as np
import pytest

from src.fusion.fusion_engine import FusionEngine, METHODS, normalized_weights
from src.fusion.evaluation import retrieval_metrics, top_k_jaccard, spearman_rank
from src.similarity_validation import UnsupportedElementError


class FakeSignal:
    def __init__(self, method, symbols=('Li','Be','B')):
        self.method, self.symbols = method, symbols
    def get_support_status(self, symbol):
        return {'target_supported': symbol in self.symbols, 'candidate_eligible': symbol in self.symbols}
    def compute_similarity(self, target, candidate):
        return {'PN': {'Li':.5,'B':.25}, 'Atom2Vec': {'Li':1.,'B':-1.}, 'Property': {'Li':-1.,'B':1.}}[self.method][candidate]


@pytest.fixture
def synthetic(): return FusionEngine({m:FakeSignal(m) for m in METHODS})


@pytest.fixture(scope='module')
def actual(): return FusionEngine()


def test_hand_calculated_weighted_fusion(synthetic):
    result = synthetic.recommend('Be',k=10)
    assert result['common_pool_size'] == 3
    assert [r['candidate_element'] for r in result['rankings']] == ['Li','B']
    assert result['rankings'][0]['fusion_score'] == pytest.approx(.5)
    assert result['rankings'][1]['fusion_score'] == pytest.approx(1.25/3)
    for row in result['rankings']:
        assert math.fsum(row['contributions'].values()) == row['fusion_score']
    assert result['score_is_probability'] is False


def test_hand_calculated_rank_fusion(synthetic):
    result = synthetic.recommend('Be',fusion_method='rrf')
    assert result['rankings'][0]['fusion_score'] == pytest.approx((1+1+61/62)/3)
    assert result['rankings'][0]['method_ranks'] == {'PN':1,'Atom2Vec':1,'Property':2}


def test_single_signal_and_zero_weight_still_use_same_pool(synthetic):
    result = synthetic.recommend('Be',weights={'PN':0,'Atom2Vec':0,'Property':5})
    assert result['rankings'][0]['candidate_element'] == 'B'
    assert result['rankings'][0]['fusion_score'] == 1
    assert result['available_candidate_count'] == 2


def test_large_weights_normalize_without_overflow():
    assert normalized_weights(dict.fromkeys(METHODS,1e308)) == dict.fromkeys(METHODS,1/3)


@pytest.mark.parametrize('weights', [{}, {'PN':1}, dict.fromkeys(METHODS,0), {'PN':-1,'Atom2Vec':1,'Property':1},
    {'PN':True,'Atom2Vec':1,'Property':1}, {'PN':float('nan'),'Atom2Vec':1,'Property':1},
    {'PN':float('inf'),'Atom2Vec':1,'Property':1}, {'PN':'1','Atom2Vec':1,'Property':1}, [1,1,1]])
def test_invalid_weights(weights):
    with pytest.raises(ValueError): normalized_weights(weights)


@pytest.mark.parametrize('target', ['ga','Xx',' Ga ',None,[],31])
def test_invalid_target(actual,target):
    with pytest.raises((ValueError,TypeError)): actual.recommend(target)


@pytest.mark.parametrize('kwargs', [{'k':-1},{'k':True},{'k':1.5},{'rrf_k':-1},{'rrf_k':True},{'rrf_k':1000001},
                                    {'fusion_method':'unknown'},{'fusion_method':[]}])
def test_invalid_request_parameters(synthetic,kwargs):
    with pytest.raises((ValueError,TypeError)): synthetic.recommend('Be',**kwargs)


@pytest.mark.parametrize('formula,target', [('MoS2','Ga'),('Xx2O3','Ga'),('  ','Ga'),([], 'Ga'),('<script>','Ga'),('Ga-2O3','Ga'),('a'*121,'Ga')])
def test_invalid_or_mismatched_context(actual,formula,target):
    with pytest.raises((ValueError,TypeError)): actual.recommend(target,host_formula=formula)


def test_host_membership_does_not_condition_ranking(actual):
    first = actual.recommend('Ga',host_formula='Ga2O3')
    second = actual.recommend('Ga',host_formula='GaN')
    assert first['rankings'] == second['rankings']
    assert first['host_context']['target_present']
    assert first['host_context']['host_conditioning_used'] is False
    assert set(first['validation'].values()) == {'not_run'}


def test_recognized_unsupported_no_silent_fallback(actual):
    assert actual.get_support_status('Og')['recognized']
    with pytest.raises(UnsupportedElementError): actual.recommend('Og')


def test_all_supported_targets_have_unique_deterministic_same_pool(actual):
    assert len(actual.common_candidates) == 79
    for target in actual.common_targets:
        first = actual.recommend(target,k=1000)
        assert first == actual.recommend(target,k=1000)
        symbols = [r['candidate_element'] for r in first['rankings']]
        assert len(symbols) == len(set(symbols)) == 78
        assert target not in symbols
        for ranking in first['method_rankings'].values():
            assert {r['candidate_element'] for r in ranking} == set(symbols)
        assert all(0 <= row['fusion_score'] <= 1 for row in first['rankings'])


def test_zero_k_numpy_integer_and_mutation_isolation(synthetic):
    assert synthetic.recommend('Be',k=0)['rankings'] == []
    first = synthetic.recommend('Be',k=np.int64(1))
    first['rankings'][0]['method_scores']['PN'] = 99
    assert synthetic.recommend('Be',k=1)['rankings'][0]['method_scores']['PN'] == .5


def test_alphabetical_tie_break(synthetic,monkeypatch):
    for method, engine in synthetic.engines.items():
        monkeypatch.setattr(engine,'compute_similarity',lambda *args: .5)
    assert [r['candidate_element'] for r in synthetic.recommend('Be')['rankings']] == ['B','Li']


def test_nan_signal_rejected(synthetic,monkeypatch):
    monkeypatch.setattr(synthetic.engines['PN'],'compute_similarity',lambda *args:float('nan'))
    with pytest.raises(ValueError): synthetic.recommend('Be')


def test_retrieval_metrics_do_not_invent_negatives():
    result = retrieval_metrics(['Al','Ga','In'],['Ga'])
    assert result['hit_at_1'] == 0 and result['hit_at_3'] == 1
    assert result['reciprocal_rank'] == .5
    assert result['unknowns_treated_as_negatives'] is False
    assert 'precision' not in result and 'accuracy' not in result


@pytest.mark.parametrize('ranking,positives', [(['Al','Al'],['Ga']),(['Al'],[]),(['Xx'],['Ga']),(['Al'],['Ga','Ga'])])
def test_invalid_metric_inputs(ranking,positives):
    with pytest.raises(ValueError): retrieval_metrics(ranking,positives)


def test_rank_agreement_math():
    assert top_k_jaccard(['Al','Ga'],['Ga','In'],k=2) == pytest.approx(1/3)
    assert spearman_rank(['Al','Ga','In'],['In','Ga','Al']) == -1
    with pytest.raises(ValueError): spearman_rank(['Al'],['Ga'])
