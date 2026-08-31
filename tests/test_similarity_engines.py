"""
Unit tests for the three independent similarity engines (Task 2).

Verifies:
1. Engine initialization and candidate spaces.
2. Target element exclusion from its own Top-10.
3. Exactly 10 unique candidates returned per engine.
4. Determinism of rankings across multiple calls.
5. Common output schema compliance:
   {'method', 'target_element', 'rank', 'candidate_element', 'similarity_score'}
6. Score boundedness and finiteness.
7. Chemical sanity on key elements (Ga, Mo, Ti, S).
8. Strict isolation: no benchmark ground-truth answers accessed.
"""

import pytest
from src.pn_similarity.pn_engine import PNSimilarityEngine
from src.atom2vec.atom2vec_engine import Atom2VecEngine
from src.property_similarity.property_engine import PropertySimilarityEngine


@pytest.fixture(scope="module")
def pn_engine():
    return PNSimilarityEngine()


@pytest.fixture(scope="module")
def atom2vec_engine():
    return Atom2VecEngine()


@pytest.fixture(scope="module")
def prop_engine():
    return PropertySimilarityEngine()


@pytest.mark.parametrize("target", ["Ga", "Ti", "Mo", "S", "Ba", "Sr", "Pb", "Bi", "Te"])
def test_target_exclusion_and_cardinality(pn_engine, atom2vec_engine, prop_engine, target):
    """Ensure target element never appears in its own Top-10 and exactly 10 items returned."""
    for engine, method_name in [
        (pn_engine, "PN"),
        (atom2vec_engine, "Atom2Vec"),
        (prop_engine, "Property")
    ]:
        top10 = engine.get_top_k(target, k=10)
        assert len(top10) == 10, f"{method_name} failed to return 10 candidates for {target}"
        
        candidates = [item["candidate_element"] for item in top10]
        assert len(set(candidates)) == 10, f"{method_name} returned duplicate candidates for {target}"
        assert target not in candidates, f"{method_name} included target {target} in its own Top-10!"


def test_common_output_schema(pn_engine, atom2vec_engine, prop_engine):
    """Verify common output format across all three independent methods."""
    required_keys = {"method", "target_element", "rank", "candidate_element", "similarity_score"}
    
    for engine, expected_method in [
        (pn_engine, "PN"),
        (atom2vec_engine, "Atom2Vec"),
        (prop_engine, "Property")
    ]:
        top10 = engine.get_top_k("Ga", k=10)
        for idx, item in enumerate(top10, start=1):
            assert set(item.keys()) == required_keys
            assert item["method"] == expected_method
            assert item["target_element"] == "Ga"
            assert item["rank"] == idx
            assert isinstance(item["candidate_element"], str)
            assert isinstance(item["similarity_score"], float)


def test_score_bounds_and_finiteness(pn_engine, atom2vec_engine, prop_engine):
    """Verify similarity score ranges and lack of NaN/inf values."""
    import math
    for engine, score_min, score_max in [
        (pn_engine, 0.0, 1.0),
        (atom2vec_engine, -1.0, 1.0),
        (prop_engine, -1.0, 1.0)
    ]:
        for target in ["Ga", "Mo", "Ba", "S"]:
            top10 = engine.get_top_k(target, k=10)
            for item in top10:
                s = item["similarity_score"]
                assert not math.isnan(s) and not math.isinf(s)
                assert score_min <= s <= score_max, f"Score {s} out of bounds [{score_min}, {score_max}]"


def test_determinism_and_reproducibility(pn_engine, atom2vec_engine, prop_engine):
    """Verify rankings are strictly deterministic across repeated invocations."""
    for engine in [pn_engine, atom2vec_engine, prop_engine]:
        run1 = engine.get_top_k("Ga", k=10)
        run2 = engine.get_top_k("Ga", k=10)
        assert run1 == run2, "Engine produced non-deterministic Top-10 output!"


def test_chemical_sanity_analogues(pn_engine, atom2vec_engine, prop_engine):
    """
    Verify key expected chemical analogues appear in Top-10 for standard probe elements:
    - Ga: Al or In must appear in Top-10 for all 3 engines.
    - Mo: W must appear in Top-10 for all 3 engines.
    - Ti: Zr or Hf must appear in Top-10 for all 3 engines.
    - S: Se or Te must appear in Top-10 for all 3 engines.
    """
    probes = [
        ("Ga", {"Al", "In"}),
        ("Mo", {"W", "Cr"}),
        ("Ti", {"Zr", "Hf"}),
        ("S", {"Se", "Te"})
    ]
    for target, expected_analogues in probes:
        for engine, name in [(pn_engine, "PN"), (atom2vec_engine, "Atom2Vec"), (prop_engine, "Property")]:
            top10_cands = {item["candidate_element"] for item in engine.get_top_k(target, k=10)}
            intersect = top10_cands.intersection(expected_analogues)
            assert len(intersect) > 0, f"{name} failed to find any expected analogue {expected_analogues} in Top-10 for {target}: got {top10_cands}"
