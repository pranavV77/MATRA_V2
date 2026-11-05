"""Fixed-parameter development retrieval, ablations, coverage and local timings."""
from pathlib import Path
import hashlib
import json
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.fusion.fusion_engine import FusionEngine, METHODS
from src.fusion.evaluation import retrieval_metrics, spearman_rank, top_k_jaccard
from src.data_audit.evidence_extension import validate_extended_review

OUT = ROOT / 'results/stage_04/run_001'
STRATEGIES = [*METHODS, 'weighted_score', 'rrf']


def rankings(engine, target):
    weighted = engine.recommend(target, k=1000)
    result = {m: [r['candidate_element'] for r in weighted['method_rankings'][m]] for m in METHODS}
    result['weighted_score'] = [r['candidate_element'] for r in weighted['rankings']]
    result['rrf'] = [r['candidate_element'] for r in engine.recommend(target, k=1000, fusion_method='rrf')['rankings']]
    return result


def main():
    output = OUT / 'evaluation.json'
    if output.exists(): raise FileExistsError('Evaluation run already exists')
    engine = FusionEngine()
    reference_path = ROOT / 'data/benchmark/v2_2_0/extended_evidence.json'
    reference = json.loads(reference_path.read_text(encoding='utf-8'))
    validate_extended_review(reference, ROOT)
    cases, skipped = [], []
    for claim in reference['reviewed_claims']:
        if not claim['eligible'] or claim['track'] != 'substitution': continue
        if claim['target'] not in engine.common_targets or claim['candidate'] not in engine.common_candidates:
            skipped.append(claim['claim_id'])
            continue
        orders = rankings(engine, claim['target'])
        cases.append({'claim_id': claim['claim_id'], 'target': claim['target'], 'known_candidate': claim['candidate'],
                      'evidence_class': claim['evidence_class'], 'independence_group': claim['independence_group'],
                      'scope': claim['scope'], 'source_id': claim['source_id'], 'held_out': False,
                      'metrics': {strategy: retrieval_metrics(orders[strategy], [claim['candidate']]) for strategy in STRATEGIES},
                      'top10': {strategy: orders[strategy][:10] for strategy in STRATEGIES}})
    summaries = {}
    for strategy in STRATEGIES:
        summaries[strategy] = {'cases': len(cases), 'mrr': float(np.mean([c['metrics'][strategy]['reciprocal_rank'] for c in cases])),
                              **{f'hits_at_{k}': sum(c['metrics'][strategy][f'hit_at_{k}'] for c in cases) for k in (1,3,5,10)}}
    all_rankings = {target: rankings(engine, target) for target in engine.common_targets}
    agreement = {a: {b: {'mean_top10_jaccard': float(np.mean([top_k_jaccard(r[a], r[b]) for r in all_rankings.values()])),
                        'mean_full_rank_spearman': float(np.mean([spearman_rank(r[a], r[b]) for r in all_rankings.values()]))}
                     for b in STRATEGIES} for a in STRATEGIES}
    ablations = {}
    for removed in METHODS:
        weights = {m: int(m != removed) for m in METHODS}
        orders = {target: [r['candidate_element'] for r in engine.recommend(target, k=1000, weights=weights)['rankings']]
                  for target in engine.common_targets}
        ablations['without_'+removed] = {'normalized_weights': engine.recommend('Ga', weights=weights)['weights'],
            'candidate_pool_changed': False,
            'mean_top10_jaccard_with_full': float(np.mean([top_k_jaccard(orders[t], all_rankings[t]['weighted_score']) for t in orders])),
            'development_mrr': float(np.mean([retrieval_metrics(orders[c['target']], [c['known_candidate']])['reciprocal_rank'] for c in cases])),
            'development_hits_at_1': sum(retrieval_metrics(orders[c['target']], [c['known_candidate']])['hit_at_1'] for c in cases)}
    timings = {}
    for strategy in STRATEGIES:
        fn = (lambda s=strategy: engine.engines[s].get_top_k('Ga')) if strategy in METHODS else (lambda s=strategy: engine.recommend('Ga', fusion_method=s))
        for _ in range(20): fn()
        values = []
        for _ in range(200):
            start = time.perf_counter_ns(); fn(); values.append((time.perf_counter_ns()-start)/1e6)
        timings[strategy] = {'target': 'Ga', 'warmups': 20, 'calls': 200, 'median_ms': float(np.median(values)),
                             'p95_ms': float(np.percentile(values,95)), 'raw_ms': values,
                             'note': 'Individual engine timing uses its native pool; fusion includes contributions and uses the common pool. Not a speedup comparison.'}
    result = {'scope': 'development_reference_retrieval_and_software_evaluation', 'candidate_pool_size': len(engine.common_candidates),
              'query_count_for_agreement': len(engine.common_targets), 'cutoffs': [1,3,5,10], 'held_out_cases': 0,
              'reference_source': {'path': reference_path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(reference_path.read_bytes()).hexdigest()},
              'parameters': {'default_method': 'weighted_score', 'weights': dict.fromkeys(METHODS, 1/3),
                             'cosine_mapping': '(score+1)/2', 'rrf_k': 60, 'weights_tuned_on_references': False},
              'reference_cases': cases, 'skipped_eligible_cases': skipped, 'summary': summaries,
              'agreement': agreement, 'ablations': ablations, 'timings': timings,
              'all_target_top10': {t: {m: order[:10] for m,order in r.items()} for t,r in all_rankings.items()},
              'limitations': ['Only two known development references, one computational and one experimental; no generalization estimate.',
                              'Reference recovery is not successful-substitution accuracy or property preservation.',
                              'Unknown candidates are not negative labels; no precision, specificity or confusion matrix computed.',
                              'Host composition/site/concentration do not condition element-level similarity scores.',
                              'Legacy eleven-case assertions remain withheld and are not used as new accuracy ground truth.']}
    with output.open('x', encoding='utf-8') as stream: json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
    print(json.dumps({'summary': summaries, 'ablations': ablations, 'median_ms': {m: t['median_ms'] for m,t in timings.items()}}, indent=2))


if __name__ == '__main__': main()
