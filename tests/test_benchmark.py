"""
Unit tests for the substitution benchmark dataset (data/benchmark/benchmark_cases.json).

Verifies:
1. JSON schema validity and top-level fields.
2. Unique case IDs across primary and secondary cases.
3. Element symbols validity against IUPAC periodic table (Z=1..94).
4. Strict separation between primary substitution and secondary doping cases.
5. Primary cases have non-empty known_substituents and valid site evidence types.
6. Target elements and substituents are chemically valid and mutually exclusive per case.
7. Secondary cases have valid dopant roles and DO NOT contaminate primary ground truths.
8. Deterministic loading and parsing integrity.
"""

import os
import json
import pandas as pd
import pytest


@pytest.fixture(scope="module")
def benchmark_data():
    path = os.path.join("data", "benchmark", "benchmark_cases.json")
    assert os.path.exists(path), f"Benchmark file does not exist at {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def valid_elements():
    path = os.path.join("data", "processed", "elements_master.parquet")
    assert os.path.exists(path), f"Master element table does not exist at {path}"
    df = pd.read_parquet(path)
    return set(df["symbol"].tolist())


def test_top_level_structure_and_counts(benchmark_data):
    """Verify top-level keys, metadata, and case counts."""
    assert "metadata" in benchmark_data
    assert "primary_cases" in benchmark_data
    assert "secondary_doping_cases" in benchmark_data
    
    primary = benchmark_data["primary_cases"]
    secondary = benchmark_data["secondary_doping_cases"]
    
    # Assert exact counts
    assert len(primary) == 11, f"Expected 11 primary cases, got {len(primary)}"
    assert len(secondary) == 5, f"Expected 5 secondary cases, got {len(secondary)}"
    
    # Total targets count in primary
    total_targets = sum(len(c["known_substituents"]) for c in primary)
    assert total_targets == 18, f"Expected 20 primary targets, got {total_targets}"


def test_unique_case_ids(benchmark_data):
    """Verify all case IDs are unique and strictly formatted."""
    all_ids = []
    for c in benchmark_data["primary_cases"]:
        assert c["case_id"].startswith("BM-P"), f"Invalid primary case ID: {c['case_id']}"
        all_ids.append(c["case_id"])
        
    for c in benchmark_data["secondary_doping_cases"]:
        assert c["case_id"].startswith("BM-S"), f"Invalid secondary case ID: {c['case_id']}"
        all_ids.append(c["case_id"])
        
    assert len(all_ids) == len(set(all_ids)), "Duplicate case IDs detected!"


def test_element_symbols_validity(benchmark_data, valid_elements):
    """Verify target elements and known substituents exist in valid elements table."""
    for c in benchmark_data["primary_cases"]:
        target = c["target_element"]
        assert target in valid_elements, f"Target element {target} not in valid elements table"
        
        subs = c["known_substituents"]
        assert len(subs) > 0, f"Case {c['case_id']} has empty known_substituents"
        assert len(subs) == len(set(subs)), f"Case {c['case_id']} has duplicate substituents"
        
        for sub in subs:
            assert sub in valid_elements, f"Substituent {sub} not in valid elements table"
            assert sub != target, f"Target element {target} cannot be its own substituent"
            
    for c in benchmark_data["secondary_doping_cases"]:
        target = c["target_element"]
        dopant = c["known_dopant"]
        assert target in valid_elements
        assert dopant in valid_elements
        assert dopant != target


def test_evidence_types_and_status(benchmark_data):
    """Verify explicit evidence classification and provenance fields."""
    valid_evidence_types = {
        "EXPERIMENTAL_DIRECT",
        "COMPUTATIONAL",
        "DATABASE_STRUCTURAL",
        "DOPING_CONTEXT",
        "UNVERIFIED"
    }
    
    for c in benchmark_data["primary_cases"]:
        ev = c["evidence_type"]
        assert ev in valid_evidence_types, f"Invalid evidence type: {ev}"
        assert ev == "EXPERIMENTAL_DIRECT", f"Primary case {c['case_id']} must be EXPERIMENTAL_DIRECT"
        
        # Provenance completeness
        assert "source_reference" in c and len(c["source_reference"]) > 0
        assert "resulting_compositions" in c and len(c["resulting_compositions"]) > 0
        assert "materials_project_identifiers" in c and len(c["materials_project_identifiers"]) > 0
        assert "wyckoff_position" in c and len(c["wyckoff_position"]) > 0
        assert "coordination" in c and len(c["coordination"]) > 0
        
    for c in benchmark_data["secondary_doping_cases"]:
        ev = c["evidence_type"]
        assert ev == "DOPING_CONTEXT", f"Secondary case {c['case_id']} must have DOPING_CONTEXT evidence type"
        assert "dopant_role" in c and len(c["dopant_role"]) > 0
        assert "context_usage_note" in c and len(c["context_usage_note"]) > 0


def test_rejected_cases_absence(benchmark_data):
    """Ensure that known rejected/invalid cases are NOT present in the primary benchmark."""
    for c in benchmark_data["primary_cases"]:
        # CsPbI3 -> Bi was rejected due to double perovskite phase separation
        if c["formula"] == "CsPbI3" and c["target_element"] == "Pb":
            assert "Bi" not in c["known_substituents"], "Bi must not be a primary substituent for CsPbI3"
            assert "Ge" not in c["known_substituents"], "Ge must not be in primary ground truth (negligible solubility)"
            assert c["known_substituents"] == ["Sn"], "CsPbI3 primary ground truth must be strictly ['Sn']"
            
        # BaTiO3 -> Si was rejected due to ionic radius collapse
        if c["formula"] == "BaTiO3" and c["target_element"] == "Ti":
            assert "Si" not in c["known_substituents"], "Si must not be a primary substituent for BaTiO3"
            
        # Ga2O3 -> Cr was rejected from primary (optical luminescence center only)
        if c["formula"] == "Ga2O3" and c["target_element"] == "Ga":
            assert "Cr" not in c["known_substituents"], "Cr must not be in primary Ga2O3 substituents"
            assert set(c["known_substituents"]) == {"Al", "In"}, "Ga2O3 primary substituents must be Al and In"


def test_secondary_not_in_primary_targets(benchmark_data):
    """Verify that dilute dopants are not spuriously included as primary bulk substituents in the same material."""
    for s_case in benchmark_data["secondary_doping_cases"]:
        mat = s_case["formula"]
        target = s_case["target_element"]
        dopant = s_case["known_dopant"]
        
        # Find corresponding primary case if any
        matching_primary = [
            p for p in benchmark_data["primary_cases"]
            if p["formula"] == mat and p["target_element"] == target
        ]
        for p in matching_primary:
            assert dopant not in p["known_substituents"], (
                f"Dilute dopant {dopant} from {s_case['case_id']} should NOT be in primary ground truth of {p['case_id']}"
            )
