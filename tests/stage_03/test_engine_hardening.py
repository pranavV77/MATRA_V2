"""Adversarial engine tests; synthetic fixtures are not scientific benchmarks."""
from pathlib import Path
import gzip
import json
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from src.pn_similarity.pn_engine import PNSimilarityEngine
from src.property_similarity.property_engine import PropertySimilarityEngine
from src.atom2vec.atom2vec_engine import Atom2VecEngine, ALGORITHM
from src.similarity_validation import PROJECT_ROOT, UnsupportedElementError

ROOT = PROJECT_ROOT
CLASSES = [PNSimilarityEngine, PropertySimilarityEngine, Atom2VecEngine]


@pytest.fixture(scope='module', params=CLASSES, ids=['PN', 'Property', 'Atom2Vec'])
def engine(request):
    return request.param()


@pytest.fixture
def master():
    return pd.read_parquet(ROOT / 'data/processed/elements_master.parquet')


def cache(path, **changes):
    data = {'common_symbols': np.array(['Ga', 'Al']), 'F_norm': np.eye(2), 'singular_values': np.array([2., 1.])}
    data.update(changes)
    np.savez_compressed(path, **data)
    return path


def corpus(path, formulas=None):
    formulas = ['LiF', 'LiCl', 'NaF', 'NaCl', 'KF', 'KCl', 'MgO', 'CaO'] if formulas is None else formulas
    with gzip.open(path, 'wt', encoding='utf-8') as f:
        json.dump({'columns': ['formula'], 'index': list(range(len(formulas))), 'data': [[x] for x in formulas]}, f)
    return path


@pytest.mark.parametrize('target', ['', 'Xx', 'ga', ' Ga ', 'Ga2O3', None, 31, [], {}])
def test_invalid_symbols_have_explicit_errors(engine, target):
    with pytest.raises((ValueError, TypeError)):
        engine.get_top_k(target)
    with pytest.raises((ValueError, TypeError)):
        engine.compute_similarity('Ga', target)


@pytest.mark.parametrize('k', [-1, True, False, np.bool_(True), 1.5, '10', None])
def test_invalid_k_rejected(engine, k):
    with pytest.raises((ValueError, TypeError)):
        engine.get_top_k('Ga', k)


def test_k_boundaries_and_numpy_integer(engine):
    assert engine.get_top_k('Ga', 0) == []
    assert len(engine.get_top_k('Ga', np.int64(1))) == 1
    all_rows = engine.get_top_k('Ga', 10**100)
    assert len(all_rows) == len({r['candidate_element'] for r in all_rows})
    assert 'Ga' not in {r['candidate_element'] for r in all_rows}
    assert [r['rank'] for r in all_rows] == list(range(1, len(all_rows)+1))


def test_recognized_but_unsupported_is_distinct(engine):
    status = engine.get_support_status('Og')
    assert status['recognized'] and not status['target_supported']
    assert not status['scientific_substitution_validated']
    with pytest.raises(UnsupportedElementError): engine.get_top_k('Og')


@pytest.mark.parametrize('cls', [PNSimilarityEngine, PropertySimilarityEngine])
@pytest.mark.parametrize('defect', ['duplicate', 'empty', 'missing_symbol', 'missing_group', 'wrong_identity', 'false_noble_group', 'bad_symbol'])
def test_invalid_master_rejected(master, tmp_path, cls, defect):
    if defect == 'duplicate': master = pd.concat([master, master.iloc[[0]]], ignore_index=True)
    elif defect == 'empty': master = master.iloc[:0]
    elif defect == 'missing_symbol': master = master.drop(columns='symbol')
    elif defect == 'missing_group': master = master.drop(columns='group_id')
    elif defect == 'wrong_identity': master.loc[master.symbol == 'Ga', 'atomic_number'] = 30
    elif defect == 'false_noble_group': master.loc[master.symbol == 'Ga', 'group_id'] = 18
    elif defect == 'bad_symbol': master.loc[master.symbol == 'Ga', 'symbol'] = 'Ga2O3'
    path = tmp_path / 'master.parquet'
    master.to_parquet(path, index=False)
    with pytest.raises((ValueError, TypeError)): cls(path)


@pytest.mark.parametrize('defect', ['float_pn', 'negative_pn', 'zero_pn', 'large_pn', 'duplicate_pn', 'missing_pn', 'nullable_pn'])
def test_pn_data_contract(master, tmp_path, defect):
    if defect == 'float_pn': master['mendeleev_number'] = master.mendeleev_number.astype(float)
    elif defect == 'negative_pn': master.loc[0, 'mendeleev_number'] = -1
    elif defect == 'zero_pn': master.loc[0, 'mendeleev_number'] = 0
    elif defect == 'large_pn': master.loc[0, 'mendeleev_number'] = 119
    elif defect == 'duplicate_pn': master.loc[0, 'mendeleev_number'] = master.loc[1, 'mendeleev_number']
    elif defect == 'missing_pn': master = master.drop(columns='mendeleev_number')
    elif defect == 'nullable_pn':
        master['mendeleev_number'] = master.mendeleev_number.astype('Int64')
        master.loc[0, 'mendeleev_number'] = pd.NA
    path = tmp_path / 'pn.parquet'
    master.to_parquet(path, index=False)
    with pytest.raises(ValueError): PNSimilarityEngine(path)


def test_pn_formula_and_tie_break_are_hand_calculable(tmp_path):
    path = tmp_path / 'synthetic.parquet'
    pd.DataFrame({'symbol': ['Li', 'Be', 'B'], 'group_id': [1, 2, 13], 'mendeleev_number': [1, 2, 3]}).to_parquet(path, index=False)
    engine = PNSimilarityEngine(path)
    assert engine.compute_similarity('Li', 'B') == pytest.approx(1/3)
    assert [r['candidate_element'] for r in engine.get_top_k('Be')] == ['B', 'Li']


@pytest.mark.parametrize('defect', ['nan', 'infinity', 'negative_density', 'zero_density', 'strings', 'bool', 'missing_feature', 'fractional_electrons', 'excess_subshell', 'overflow'])
def test_property_feature_contract(master, tmp_path, defect):
    idx = master.index[master.symbol == 'Ga'][0]
    if defect == 'nan': master.loc[idx, 'density'] = np.nan
    elif defect == 'infinity': master.loc[idx, 'density'] = np.inf
    elif defect == 'negative_density': master.loc[idx, 'density'] = -1
    elif defect == 'zero_density': master.loc[idx, 'density'] = 0
    elif defect == 'strings': master['density'] = master.density.astype(str)
    elif defect == 'bool': master['density'] = True
    elif defect == 'missing_feature': master = master.drop(columns='density')
    elif defect == 'fractional_electrons':
        master['s_valence_electrons'] = master.s_valence_electrons.astype(float)
        master.loc[idx, 's_valence_electrons'] = 1.5
    elif defect == 'excess_subshell': master.loc[idx, 's_valence_electrons'] = 3
    elif defect == 'overflow': master.loc[idx, 'density'] = 1e308
    path = tmp_path / 'properties.parquet'
    master.to_parquet(path, index=False)
    with pytest.raises(ValueError): PropertySimilarityEngine(path)


def test_complex_property_rejected_at_reader_boundary(master, monkeypatch):
    import src.property_similarity.property_engine as module
    master['density'] = master.density.astype(complex)
    monkeypatch.setattr(module, 'read_master', lambda *args: master)
    with pytest.raises(ValueError, match='real numeric'): PropertySimilarityEngine()


def test_property_zero_vectors_and_constant_columns(master, tmp_path):
    path = tmp_path / 'constant.parquet'
    subset = master[master.symbol.isin(['Li', 'Be'])].copy()
    for feature in PropertySimilarityEngine.FEATURE_NAMES:
        subset[feature] = subset[feature].iloc[0]
    subset.to_parquet(path, index=False)
    with pytest.raises(ValueError, match='Zero'): PropertySimilarityEngine(path)
    subset.loc[subset.symbol == 'Li', 'density'] = .5
    subset.loc[subset.symbol == 'Be', 'density'] = 1.5
    subset.to_parquet(tmp_path / 'one_direction.parquet', index=False)
    engine = PropertySimilarityEngine(tmp_path / 'one_direction.parquet')
    assert engine.compute_similarity('Li', 'Be') == pytest.approx(-1)
    assert engine.compute_similarity('Li', 'Li') == 1


@pytest.mark.parametrize('defect', ['nan', 'infinite', 'zero', 'nonunit', 'shape', 'duplicate', 'invalid_symbol', 'object_symbols', 'complex', 'singular_shape', 'negative_singular', 'ascending_singular'])
def test_cache_contract(tmp_path, defect):
    changes = {}
    if defect == 'nan': changes['F_norm'] = np.array([[np.nan, 0], [0, 1]])
    elif defect == 'infinite': changes['F_norm'] = np.array([[np.inf, 0], [0, 1]])
    elif defect == 'zero': changes['F_norm'] = np.zeros((2, 2))
    elif defect == 'nonunit': changes['F_norm'] = np.eye(2)*2
    elif defect == 'shape': changes['F_norm'] = np.ones((1, 2))
    elif defect == 'duplicate': changes['common_symbols'] = np.array(['Ga', 'Ga'])
    elif defect == 'invalid_symbol': changes['common_symbols'] = np.array(['Ga', 'Xx'])
    elif defect == 'object_symbols': changes['common_symbols'] = np.array(['Ga', 'Al'], dtype=object)
    elif defect == 'complex': changes['F_norm'] = np.eye(2).astype(complex)
    elif defect == 'singular_shape': changes['singular_values'] = np.ones(3)
    elif defect == 'negative_singular': changes['singular_values'] = np.array([2., -1.])
    elif defect == 'ascending_singular': changes['singular_values'] = np.array([1., 2.])
    path = cache(tmp_path / 'bad.npz', **changes)
    with pytest.raises(ValueError): Atom2VecEngine(cache_embedding_path=path, embedding_dim=2)


def test_legacy_cache_policy_and_dimension(tmp_path):
    path = cache(tmp_path / 'legacy.npz')
    with pytest.raises(ValueError, match='dimension'): Atom2VecEngine(cache_embedding_path=path, embedding_dim=1)
    with pytest.raises(ValueError, match='strict'): Atom2VecEngine(cache_embedding_path=path, embedding_dim=2, require_cache_metadata=True)
    engine = Atom2VecEngine(cache_embedding_path=path, embedding_dim=2)
    assert engine.cache_info['metadata_present'] is False
    assert engine.cache_info['requested_seed_verified'] is False
    with pytest.raises(ValueError, match='non-default'):
        Atom2VecEngine(cache_embedding_path=path, embedding_dim=2, random_seed=7)


@pytest.mark.parametrize('parameter,value', [('embedding_dim', 0), ('embedding_dim', True), ('embedding_dim', 2.5), ('random_seed', -1), ('random_seed', True), ('random_seed', 2**32), ('require_cache_metadata', 'yes')])
def test_configuration_types_and_bounds(parameter, value):
    with pytest.raises((ValueError, TypeError)): Atom2VecEngine(**{parameter: value})


def test_small_training_cache_reload_and_seed_metadata(tmp_path):
    raw = corpus(tmp_path / 'corpus.gz')
    first = Atom2VecEngine(raw, tmp_path / 'a.npz', embedding_dim=2)
    second = Atom2VecEngine(raw, tmp_path / 'b.npz', embedding_dim=2)
    reloaded = Atom2VecEngine(raw, tmp_path / 'a.npz', embedding_dim=2, require_cache_metadata=True)
    assert first.get_top_k('Li') == second.get_top_k('Li') == reloaded.get_top_k('Li')
    assert np.max(np.abs(first.F_norm @ first.F_norm.T - second.F_norm @ second.F_norm.T)) < 1e-12
    assert first.training_stats['skipped_rows'] == 0
    assert reloaded.cache_info['corpus_verified'] is True
    with pytest.raises(ValueError, match='seed'): Atom2VecEngine(raw, tmp_path / 'a.npz', embedding_dim=2, random_seed=7)
    missing_corpus = Atom2VecEngine(tmp_path / 'absent.gz', tmp_path / 'a.npz', embedding_dim=2)
    assert missing_corpus.cache_info['corpus_verified'] is False
    with gzip.open(tmp_path / 'different.gz', 'wt') as f: f.write('{}')
    with pytest.raises(ValueError, match='checksum'): Atom2VecEngine(tmp_path / 'different.gz', tmp_path / 'a.npz', embedding_dim=2)


@pytest.mark.parametrize('formulas', [[], [None, '', 'Xx2Zz3', 'H', 'LiNaKFO'], ['LiF']])
def test_empty_or_too_small_training_corpus(tmp_path, formulas):
    raw = corpus(tmp_path / 'small.gz', formulas)
    path = tmp_path / 'no_cache.npz'
    with pytest.raises(ValueError): Atom2VecEngine(raw, path, embedding_dim=2)
    assert not path.exists()


def test_invalid_formulas_are_accounted_for(tmp_path):
    raw = corpus(tmp_path / 'corpus.gz', ['LiF', 'LiCl', 'NaF', 'NaCl', None, '', 'H'])
    engine = Atom2VecEngine(raw, tmp_path / 'cache.npz', embedding_dim=1)
    assert engine.training_stats == {'input_rows': 7, 'valid_binary_to_quaternary_rows': 4, 'skipped_rows': 3}


def test_atomic_publication_never_overwrites_competing_cache(tmp_path, monkeypatch):
    import src.atom2vec.atom2vec_engine as module
    raw = corpus(tmp_path / 'corpus.gz')
    target = tmp_path / 'race.npz'
    def collision(source, destination):
        Path(destination).write_bytes(b'other writer cache')
        raise FileExistsError('simulated competing writer')
    monkeypatch.setattr(module.os, 'rename' if module.os.name == 'nt' else 'link', collision)
    with pytest.raises(FileExistsError): Atom2VecEngine(raw, target, embedding_dim=2)
    assert target.read_bytes() == b'other writer cache'
    assert not list(tmp_path.glob('.atom2vec-*'))


def test_solver_failure_does_not_publish_cache(tmp_path, monkeypatch):
    import src.atom2vec.atom2vec_engine as module
    raw = corpus(tmp_path / 'corpus.gz')
    def failure(*args, **kwargs): raise RuntimeError('simulated SVD convergence failure')
    monkeypatch.setattr(module, 'svds', failure)
    with pytest.raises(RuntimeError, match='convergence'): Atom2VecEngine(raw, tmp_path / 'absent.npz', embedding_dim=2)
    assert not (tmp_path / 'absent.npz').exists()


def test_defaults_are_independent_of_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for cls in CLASSES:
        assert len(cls().get_top_k('Ga', 1)) == 1


def test_nan_validation_survives_python_optimization(master, tmp_path):
    master.loc[master.symbol == 'Ga', 'density'] = np.nan
    path = tmp_path / 'nan.parquet'
    master.to_parquet(path, index=False)
    code = 'import sys;from src.property_similarity.property_engine import PropertySimilarityEngine\ntry: PropertySimilarityEngine(sys.argv[1])\nexcept ValueError: sys.exit(0)\nsys.exit(2)'
    result = subprocess.run([sys.executable, '-O', '-c', code, str(path)], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize('defect', ['schema_bool', 'schema_unknown', 'algorithm', 'seed_bool', 'seed_mismatch', 'dimension', 'checksum', 'json', 'array_shape'])
def test_cache_metadata_contract(tmp_path, defect):
    metadata = {'schema_version': 1, 'algorithm': ALGORITHM, 'embedding_dim': 2,
                'random_seed': 42, 'corpus_sha256': '0'*64}
    if defect == 'schema_bool': metadata['schema_version'] = True
    elif defect == 'schema_unknown': metadata['schema_version'] = 99
    elif defect == 'algorithm': metadata['algorithm'] = 'unknown'
    elif defect == 'seed_bool': metadata['random_seed'] = True
    elif defect == 'seed_mismatch': metadata['random_seed'] = 7
    elif defect == 'dimension': metadata['embedding_dim'] = 3
    elif defect == 'checksum': metadata['corpus_sha256'] = 'not-a-hash'
    encoded = np.array(json.dumps(metadata))
    if defect == 'json': encoded = np.array('{bad json')
    elif defect == 'array_shape': encoded = np.array([json.dumps(metadata)])
    path = cache(tmp_path / 'metadata.npz', metadata_json=encoded)
    with pytest.raises(ValueError): Atom2VecEngine(tmp_path / 'not_present.gz', path, embedding_dim=2)


@pytest.mark.parametrize('cls', [PNSimilarityEngine, PropertySimilarityEngine])
def test_missing_and_corrupt_master(tmp_path, cls):
    with pytest.raises(FileNotFoundError): cls(tmp_path / 'missing.parquet')
    damaged = tmp_path / 'corrupt.parquet'
    damaged.write_bytes(b'not a parquet file')
    with pytest.raises(ValueError): cls(damaged)


def test_missing_cache_keys_and_malformed_archive(tmp_path):
    missing = tmp_path / 'missing_keys.npz'
    np.savez_compressed(missing, F_norm=np.eye(2))
    with pytest.raises(ValueError): Atom2VecEngine(cache_embedding_path=missing, embedding_dim=2)
    damaged = tmp_path / 'corrupt.npz'
    damaged.write_bytes(b'not a zip')
    with pytest.raises(ValueError): Atom2VecEngine(cache_embedding_path=damaged, embedding_dim=2)


@pytest.mark.parametrize('payload', [{}, {'data': [], 'index': [], 'columns': ['wrong']}, 'not-table'])
def test_malformed_corpus_table(tmp_path, payload):
    path = tmp_path / 'bad.gz'
    with gzip.open(path, 'wt') as f: json.dump(payload, f)
    with pytest.raises(ValueError): Atom2VecEngine(path, tmp_path / 'cache.npz', embedding_dim=1)


def test_cache_write_permission_failure_keeps_destination_absent(tmp_path, monkeypatch):
    import src.atom2vec.atom2vec_engine as module
    raw = corpus(tmp_path / 'corpus.gz')
    def denied(*args, **kwargs): raise PermissionError('simulated cache-directory write denial')
    monkeypatch.setattr(module.tempfile, 'NamedTemporaryFile', denied)
    with pytest.raises(PermissionError): Atom2VecEngine(raw, tmp_path / 'cache.npz', embedding_dim=2)
    assert not (tmp_path / 'cache.npz').exists()


REGRESSION_IDS = [
    'PN:invalid_k:-1', 'PN:invalid_k:True', 'Atom2Vec:invalid_k:-1', 'Atom2Vec:invalid_k:True',
    'Property:invalid_k:-1', 'Property:invalid_k:True', 'PN:duplicate', 'Property:duplicate',
    'Property:infinite_feature', 'Property:negative_density', 'Atom2Vec:nan_cache',
    'Atom2Vec:cache_dimension', 'PN:duplicate_candidate', 'Property:duplicate_candidate', 'Atom2Vec:zero_vectors']


@pytest.mark.parametrize('case', REGRESSION_IDS, ids=REGRESSION_IDS)
def test_stage1_reported_failure_remediated(case, master, tmp_path):
    name = case.split(':')[0]
    cls = {'PN': PNSimilarityEngine, 'Property': PropertySimilarityEngine, 'Atom2Vec': Atom2VecEngine}[name]
    with pytest.raises((ValueError, TypeError)):
        if 'invalid_k' in case:
            cls().get_top_k('Ga', -1 if case.endswith(':-1') else True)
        elif 'duplicate' in case:
            frame = pd.concat([master, master[master.symbol == 'Al']], ignore_index=True)
            path = tmp_path / 'duplicate.parquet'
            frame.to_parquet(path, index=False)
            cls(path)
        elif case == 'Property:infinite_feature' or case == 'Property:negative_density':
            master.loc[master.symbol == 'Ga', 'density'] = np.inf if 'infinite' in case else -1
            path = tmp_path / 'invalid.parquet'
            master.to_parquet(path, index=False)
            cls(path)
        elif case == 'Atom2Vec:cache_dimension':
            cls(embedding_dim=10)
        else:
            matrix = np.zeros((2, 2)) if case.endswith('zero_vectors') else np.array([[np.nan, 0], [0, 1]])
            cls(cache_embedding_path=cache(tmp_path / 'bad.npz', F_norm=matrix), embedding_dim=2)
