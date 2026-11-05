"""Compare hardened signals to preserved behavior; no chemistry benchmark scoring."""
from pathlib import Path
import importlib.util
import json
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pymatgen.core import Element
from src.pn_similarity.pn_engine import PNSimilarityEngine
from src.property_similarity.property_engine import PropertySimilarityEngine
from src.atom2vec.atom2vec_engine import Atom2VecEngine
from src.similarity_validation import UnsupportedElementError

OUT = ROOT / 'results/stage_03/run_001'


def latency(engine, repetitions=200):
    for _ in range(20): engine.get_top_k('Ga')
    durations = []
    for _ in range(repetitions):
        start = time.perf_counter_ns()
        engine.get_top_k('Ga')
        durations.append((time.perf_counter_ns()-start)/1e6)
    return {'warmup_calls': 20, 'repetitions': repetitions, 'median_ms': float(np.median(durations)),
            'p95_ms': float(np.percentile(durations, 95)), 'raw_ms': durations}


def main():
    if (OUT / 'engine_verification.json').exists(): raise FileExistsError('Verification already recorded')
    baseline = json.loads((OUT / 'baseline.json').read_text(encoding='utf-8'))
    engines = {'PN': PNSimilarityEngine(), 'Property': PropertySimilarityEngine(), 'Atom2Vec': Atom2VecEngine()}
    result = {'purpose': 'Software/math/reproducibility verification, not scientific substitution accuracy', 'engines': {}}
    arrays = {}
    for method, engine in engines.items():
        previous = baseline[method]
        symbols = previous['symbols']
        matrix = np.array([[engine.compute_similarity(a, b) for b in symbols] for a in symbols])
        old = np.array(previous['similarity_matrix'])
        delta = float(np.max(np.abs(matrix-old)))
        rank_changes = sum(engine.get_top_k(s) != previous['top10'][s] for s in symbols)
        repeated = all(engine.get_top_k(s) == engine.get_top_k(s) for s in symbols)
        symmetry = float(np.max(np.abs(matrix-matrix.T)))
        self_error = float(np.max(np.abs(np.diag(matrix)-1)))
        if delta > 1e-12 or rank_changes or not repeated or symmetry > 1e-12 or self_error > 1e-12:
            raise ValueError(f'Valid-input numerical/ranking regression for {method}')
        statuses = []
        for z in range(1, 119):
            symbol = Element.from_Z(z).symbol
            status = engine.get_support_status(symbol)
            if status['target_supported']:
                rows = engine.get_top_k(symbol, 1000)
                candidates = [r['candidate_element'] for r in rows]
                if len(set(candidates)) != len(candidates) or symbol in candidates:
                    raise ValueError('Duplicate or self candidate')
                if any(not engine.get_support_status(s)['candidate_eligible'] for s in candidates):
                    raise ValueError('Ranking emitted a policy-excluded candidate')
                status['returned_candidates_for_large_k'] = len(rows)
            else:
                try: engine.get_top_k(symbol)
                except UnsupportedElementError: status['unsupported_request_rejected'] = True
                else: raise ValueError('Unsupported request silently accepted')
            statuses.append(status)
        filename, classname = {'PN': ('pn_engine.py', 'PNSimilarityEngine'), 'Property': ('property_engine.py', 'PropertySimilarityEngine'), 'Atom2Vec': ('atom2vec_engine.py', 'Atom2VecEngine')}[method]
        spec = importlib.util.spec_from_file_location('preserved_' + method, OUT / 'original_engines' / filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        legacy = getattr(module, classname)()  # Existing, trusted cache/data; no retraining.
        old_latency, new_latency = latency(legacy), latency(engine)
        result['engines'][method] = {'targets_checked': len(symbols), 'pair_scores_checked': int(matrix.size),
            'max_abs_score_change': delta, 'top10_changes': rank_changes, 'repeat_rankings_identical': repeated,
            'max_symmetry_error': symmetry, 'max_self_similarity_error': self_error,
            'target_support_count': sum(s['target_supported'] for s in statuses),
            'candidate_support_count': sum(s['candidate_eligible'] for s in statuses),
            'element_statuses': statuses, 'before_latency': old_latency, 'after_latency': new_latency}
        arrays[method + '_before'] = old
        arrays[method + '_after'] = matrix
    print('Cached-engine comparisons passed; running fresh full-corpus Atom2Vec training.', flush=True)
    start = time.perf_counter()
    fresh = Atom2VecEngine(cache_embedding_path=OUT / 'fresh_atom2vec_d20.npz', require_cache_metadata=True)
    seconds = time.perf_counter()-start
    reloaded = Atom2VecEngine(cache_embedding_path=OUT / 'fresh_atom2vec_d20.npz', require_cache_metadata=True)
    symbols = baseline['Atom2Vec']['symbols']
    fresh_matrix = np.array([[fresh.compute_similarity(a, b) for b in symbols] for a in symbols])
    difference = float(np.max(np.abs(fresh_matrix-arrays['Atom2Vec_before'])))
    changes = sum(fresh.get_top_k(s) != baseline['Atom2Vec']['top10'][s] for s in symbols)
    reload_identical = all(fresh.get_top_k(s) == reloaded.get_top_k(s) for s in symbols)
    if difference > 1e-10 or changes or not reload_identical:
        raise ValueError(f'Fresh training differs: max_delta={difference}, top10_changes={changes}, reload={reload_identical}')
    result['fresh_training'] = {'seconds': seconds, 'embedding_dim': 20, 'random_seed': 42,
                                'max_abs_similarity_change_vs_original': difference, 'top10_changes': changes,
                                'reload_rankings_identical': reload_identical, 'training_stats': fresh.training_stats,
                                'cache_info': fresh.cache_info, 'cache_path': 'results/stage_03/run_001/fresh_atom2vec_d20.npz'}
    arrays['Atom2Vec_fresh'] = fresh_matrix
    with (OUT / 'score_comparison.npz').open('xb') as stream: np.savez_compressed(stream, **arrays)
    with (OUT / 'engine_verification.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    print(json.dumps({'fresh_training': result['fresh_training'], 'checked_pairs': sum(r['pair_scores_checked'] for r in result['engines'].values()),
                      'changed_top10': sum(r['top10_changes'] for r in result['engines'].values())}, indent=2))


if __name__ == '__main__': main()
