"""Reference retrieval and ranking agreement, with no unknown-as-negative labels."""
import math
from src.similarity_validation import validate_integer, validate_symbol


def retrieval_metrics(ranked_candidates, known_positives, cutoffs=(1, 3, 5, 10)):
    if not isinstance(ranked_candidates, list) or not isinstance(known_positives, (list, set, tuple)) or not known_positives:
        raise ValueError('A ranked candidate list and nonempty known-positive collection are required')
    for symbol in [*ranked_candidates, *known_positives]: validate_symbol(symbol)
    if len(set(ranked_candidates)) != len(ranked_candidates) or len(set(known_positives)) != len(known_positives):
        raise ValueError('Duplicate ranked elements or positives')
    positions = {s: i for i, s in enumerate(ranked_candidates, 1)}
    known_ranks = [positions[s] for s in known_positives if s in positions]
    best = min(known_ranks) if known_ranks else None
    result = {'best_known_rank': best, 'reciprocal_rank': 0.0 if best is None else 1.0/best,
              'known_positive_count': len(known_positives), 'unknowns_treated_as_negatives': False}
    for k in cutoffs:
        k = validate_integer(k, 'cutoff', minimum=1)
        recovered = sum(rank <= k for rank in known_ranks)
        result[f'hit_at_{k}'] = int(recovered > 0)
        result[f'known_recall_at_{k}'] = recovered/len(known_positives)
    return result


def top_k_jaccard(first, second, k=10):
    k = validate_integer(k, 'k', minimum=1)
    a, b = set(first[:k]), set(second[:k])
    return len(a & b)/len(a | b) if a | b else 1.0


def spearman_rank(first, second):
    if len(first) != len(set(first)) or len(second) != len(set(second)) or set(first) != set(second):
        raise ValueError('Spearman comparison requires identical unique candidate universes')
    n = len(first)
    if n < 2: return None
    positions = {s: i for i, s in enumerate(second, 1)}
    squared = math.fsum((i-positions[s])**2 for i, s in enumerate(first, 1))
    return 1 - 6*squared/(n*(n*n-1))
