"""Deterministic similarity fusion; no host-property or success predictions.

Score fusion follows the project architecture. Weighted reciprocal-rank fusion
is a comparison method, adapted from Cormack et al., SIGIR 2009,
https://doi.org/10.1145/1571941.1572114 . No information-retrieval performance
claim is transferred to materials substitution.
"""
from collections.abc import Mapping
from functools import lru_cache
import math
from numbers import Real
from types import MappingProxyType

from pymatgen.core import Composition, Element

from src.pn_similarity.pn_engine import PNSimilarityEngine
from src.atom2vec.atom2vec_engine import Atom2VecEngine
from src.property_similarity.property_engine import PropertySimilarityEngine
from src.similarity_validation import PROJECT_ROOT, UnsupportedElementError, validate_integer, validate_symbol

METHODS = ('PN', 'Atom2Vec', 'Property')
FUSION_METHODS = ('weighted_score', 'rrf')


def normalized_weights(weights=None):
    weights = dict.fromkeys(METHODS, 1.0) if weights is None else weights
    if not isinstance(weights, Mapping) or set(weights) != set(METHODS):
        raise ValueError('Weights must specify PN, Atom2Vec and Property exactly')
    if any(isinstance(v, bool) or not isinstance(v, Real) or not math.isfinite(v) or v < 0 for v in weights.values()):
        raise ValueError('Weights must be finite nonnegative numbers, not booleans')
    largest = max(weights.values())
    if largest == 0:
        raise ValueError('At least one weight must be positive')
    scaled = {m: float(weights[m]/largest) for m in METHODS}
    total = math.fsum(scaled.values())
    return {m: scaled[m]/total for m in METHODS}


def material_context(formula, target):
    """Validate composition membership only. No structural conditioning implied."""
    if formula is None or formula == '':
        return {'provided': False, 'host_conditioning_used': False, 'site_validated': False}
    if not isinstance(formula, str):
        raise TypeError('Material formula must be a string or omitted')
    if len(formula) > 120 or not formula.strip():
        raise ValueError('Material formula is empty or too long')
    try:
        composition = Composition(formula)
        for element, amount in composition.items():
            validate_symbol(str(element), 'composition element')
            if not math.isfinite(amount) or amount <= 0:
                raise ValueError('Composition amounts must be positive and finite')
    except (ValueError, TypeError) as exc:
        raise ValueError(f'Invalid material composition: {formula!r}') from exc
    if target not in {str(element) for element in composition.elements}:
        raise ValueError(f'Target {target} is not present in material {formula}')
    return {'provided': True, 'input_formula': formula, 'reduced_formula': composition.reduced_formula,
            'target_amount': float(composition[target]), 'target_present': True,
            'host_conditioning_used': False, 'site_validated': False,
            'note': 'Composition membership checked. Rankings remain element-level; crystal site, energy and band gap are not evaluated.'}


class FusionEngine:
    def __init__(self, engines=None):
        if engines is None:
            cache = PROJECT_ROOT / 'results/stage_03/run_001/fresh_atom2vec_d20.npz'
            if not cache.is_file():
                raise FileNotFoundError('The validated Stage 3 cache is required; this demo does not train or overwrite it')
            engines = {'PN': PNSimilarityEngine(), 'Atom2Vec': Atom2VecEngine(cache_embedding_path=cache, require_cache_metadata=True),
                       'Property': PropertySimilarityEngine()}
        if not isinstance(engines, Mapping) or set(engines) != set(METHODS):
            raise ValueError('Exactly three independent engines are required')
        self.engines = MappingProxyType(dict(engines))
        symbols = [Element.from_Z(z).symbol for z in range(1, 119)]
        self.common_targets = tuple(s for s in symbols if all(e.get_support_status(s)['target_supported'] for e in self.engines.values()))
        self.common_candidates = tuple(s for s in symbols if all(e.get_support_status(s)['candidate_eligible'] for e in self.engines.values()))
        if len(self.common_candidates) < 2:
            raise ValueError('Common candidate pool must contain at least two elements')

    def get_support_status(self, symbol):
        validate_symbol(symbol)
        return {'element': symbol, 'recognized': True, 'fusion_supported': symbol in self.common_targets,
                'candidate_eligible': symbol in self.common_candidates,
                'methods': {m: self.engines[m].get_support_status(symbol) for m in METHODS},
                'scientific_substitution_validated': False}

    @lru_cache(maxsize=128)
    def _table(self, target):
        """Immutable, benchmark-independent score/rank table on a fixed common pool."""
        candidates = tuple(s for s in self.common_candidates if s != target)
        scores, ranks = {}, {}
        for method in METHODS:
            values = {}
            for symbol in candidates:
                score = float(self.engines[method].compute_similarity(target, symbol))
                low = 0 if method == 'PN' else -1
                if not math.isfinite(score) or not low <= score <= 1:
                    raise ValueError(f'{method} produced a nonfinite or out-of-range score')
                values[symbol] = score
            ordered = sorted(candidates, key=lambda s: (-values[s], s))
            scores[method] = values
            ranks[method] = {s: i for i, s in enumerate(ordered, 1)}
        return tuple((s, tuple(scores[m][s] for m in METHODS), tuple(ranks[m][s] for m in METHODS)) for s in candidates)

    def recommend(self, target_element, k=10, weights=None, fusion_method='weighted_score', rrf_k=60, host_formula=None):
        validate_symbol(target_element, 'target')
        k = validate_integer(k, 'k')
        rrf_k = validate_integer(rrf_k, 'rrf_k', maximum=1_000_000)
        if not isinstance(fusion_method, str) or fusion_method not in FUSION_METHODS:
            raise ValueError('fusion_method must be weighted_score or rrf')
        weights = normalized_weights(weights)
        if target_element not in self.common_targets:
            raise UnsupportedElementError(f'{target_element} is recognized but does not have all three representations; no signal was imputed')
        context = material_context(host_formula, target_element)
        table = self._table(target_element)
        rows = []
        for symbol, raw, ranks in table:
            scaled = tuple(s if m == 'PN' else (s+1)/2 for m, s in zip(METHODS, raw))
            if fusion_method == 'weighted_score':
                contributions = {m: weights[m]*scaled[i] for i, m in enumerate(METHODS)}
            else:
                # A common positive factor bounds display scores without changing RRF order.
                contributions = {m: weights[m]*(rrf_k+1)/(rrf_k+ranks[i]) for i, m in enumerate(METHODS)}
            total = math.fsum(contributions.values())
            rows.append({'candidate_element': symbol, 'fusion_score': total,
                         'method_scores': dict(zip(METHODS, raw)), 'scaled_scores': dict(zip(METHODS, scaled)),
                         'method_ranks': dict(zip(METHODS, ranks)), 'contributions': contributions})
        rows.sort(key=lambda row: (-row['fusion_score'], row['candidate_element']))
        for rank, row in enumerate(rows, 1): row['rank'] = rank
        selected = rows[:k]
        method_rankings = {m: [{'candidate_element': row['candidate_element'], 'rank': row['method_ranks'][m],
                                'similarity_score': row['method_scores'][m]}
                               for row in sorted(rows, key=lambda r: r['method_ranks'][m])[:k]] for m in METHODS}
        return {'target_element': target_element, 'fusion_method': fusion_method, 'weights': weights, 'rrf_k': rrf_k,
                'requested_k': k, 'returned_k': len(selected), 'common_pool_size': len(self.common_candidates),
                'available_candidate_count': len(table), 'pool_policy': 'fixed intersection of three candidate universes; same pool for baselines and ablations',
                'host_context': context, 'rankings': selected, 'method_rankings': method_rankings,
                'scope': 'element_similarity_screening', 'score_is_probability': False,
                'validation': {'structural_site': 'not_run', 'energy_stability': 'not_run', 'band_gap_preservation': 'not_run', 'doping_activation': 'not_run'}}
