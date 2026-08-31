# Task 1 & Task 2 Reproducibility Guide

This guide provides the exact commands required to reproduce the environment, dataset validation, similarity rankings, benchmark evaluations, and automated tests for the completed Task 1 and Task 2 academic milestone.

---

## 1. Environment Activation & Prerequisites

The project operates under a verified Python 3.10.11 virtual environment located at `.venv/`.

### PowerShell (Windows):
```powershell
# Verify Python interpreter and installed core libraries
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\pip.exe list
```

**Required Core Dependencies:**
- `mendeleev == 1.2.0`
- `pymatgen == 2025.10.7`
- `pandas == 2.3.3`
- `pyarrow == 25.0.1`
- `scipy == 1.15.3`
- `scikit-learn == 1.7.2`
- `pytest == 9.1.1`

*(Note: PyTorch / CUDA are not required for Tasks 1 & 2 and are intentionally omitted at this stage).*

---

## 2. Task 1: Dataset & Benchmark Verification

### A. Verify Master Elemental Feature Dataset
To verify the integrity and provenance of `data/processed/elements_master.parquet`:
```powershell
.\.venv\Scripts\python.exe -c "
import pandas as pd, json
df = pd.read_parquet('data/processed/elements_master.parquet')
with open('data/processed/feature_metadata.json') as f:
    meta = json.load(f)
print('Elements:', len(df), 'Columns:', len(df.columns))
print('SHA256:', meta['sha256_checksum'])
"
```
**Expected Output:**
- `Elements: 94 Columns: 25`
- `SHA256: 0d9c1790b211e5e47651ec6930bcb259db36b82acc8efabb720fa26fd6fc651a`

### B. Verify Substitution Benchmark Dataset
To inspect the 11 primary substitution tasks and 5 secondary doping cases:
```powershell
.\.venv\Scripts\python.exe -c "
import json
with open('data/benchmark/benchmark_cases.json', 'r', encoding='utf-8') as f:
    bench = json.load(f)
print('Primary Cases:', len(bench['primary_cases']))
print('Primary Substituent Targets:', bench['metadata']['primary_targets_count'])
print('Secondary Doping Cases:', len(bench['secondary_doping_cases']))
"
```
**Expected Output:**
- `Primary Cases: 11`
- `Primary Substituent Targets: 18`
- `Secondary Doping Cases: 5`

---

## 3. Task 2: Headline Demonstration (beta-Ga2O3 -> Ga)

To generate the three independent Top-10 candidate lists for gallium oxide:
```powershell
.\.venv\Scripts\python.exe -c "
from src.pn_similarity.pn_engine import PNSimilarityEngine
from src.atom2vec.atom2vec_engine import Atom2VecEngine
from src.property_similarity.property_engine import PropertySimilarityEngine

pn = PNSimilarityEngine()
a2v = Atom2VecEngine()
prop = PropertySimilarityEngine()

print('=== beta-Ga2O3 -> Ga Independent Top-10 ===')
for name, eng in [('PN', pn), ('Atom2Vec', a2v), ('Property', prop)]:
    top10 = eng.get_top_k('Ga', k=10)
    cands = [f\"{it['candidate_element']} ({it['similarity_score']:.4f})\" for it in top10]
    print(f'{name:10s}:', ', '.join(cands))
"
```
**Expected Output:**
- **PN:** `Al (0.5000), In (0.5000), B (0.3333), Tl (0.3333), C (0.2000), Hg (0.2000), Cd (0.1667), Si (0.1667), Ge (0.1429), Zn (0.1429)`
- **Atom2Vec:** `Al (0.8462), In (0.7601), Y (0.7573), Bi (0.6505), La (0.6175), Sn (0.6046), Sb (0.5698), Ti (0.5373), Sc (0.4963), Zn (0.4661)`
- **Property:** `In (0.8771), Sn (0.8389), Ge (0.7352), P (0.6226), Tl (0.6177), Bi (0.6172), Pb (0.5930), Sb (0.5788), S (0.5427), Se (0.5259)`

---

## 4. Run Full Benchmark Evaluation

To execute the benchmark runner and reproduce the evaluation metrics:
```powershell
.\.venv\Scripts\python.exe -m src.benchmark.evaluate_benchmark
```
**Generated Artifacts:**
- `results/runs/task2_benchmark_evaluation.json`: Full machine-readable evaluations.
- `results/tables/benchmark_metrics_summary.md`: Summary Markdown tables.

**Expected Performance Metrics:**
| Method | Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR | Mean Best Rank | Mean Recall@10 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **PN** | 63.6% | 100.0% | 100.0% | 100.0% | 0.8182 | 1.36 | 97.0% |
| **Atom2Vec** | 63.6% | 81.8% | 81.8% | 100.0% | 0.7516 | 2.36 | 100.0% |
| **Property** | 36.4% | 72.7% | 90.9% | 100.0% | 0.5394 | 3.09 | 78.8% |

---

## 5. Run Automated Unit Test Suite

To run all 26 automated unit tests across Task 1 and Task 2:
```powershell
.\.venv\Scripts\pytest.exe tests/ -v
```
**Expected Output:**
```
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Final Project
collected 26 items

tests/test_benchmark.py::test_top_level_structure_and_counts PASSED      [  3%]
tests/test_benchmark.py::test_unique_case_ids PASSED                     [  7%]
tests/test_benchmark.py::test_element_symbols_validity PASSED            [ 11%]
tests/test_benchmark.py::test_evidence_types_and_status PASSED           [ 15%]
tests/test_benchmark.py::test_rejected_cases_absence PASSED              [ 19%]
tests/test_benchmark.py::test_secondary_not_in_primary_targets PASSED    [ 23%]
tests/test_elements_master.py::test_element_count_and_keys PASSED        [ 26%]
tests/test_elements_master.py::test_villars_pn_completeness_and_anchors PASSED [ 30%]
tests/test_elements_master.py::test_noble_gas_electronegativity_is_nan PASSED [ 34%]
tests/test_elements_master.py::test_physical_value_bounds PASSED         [ 38%]
tests/test_elements_master.py::test_imputation_flags_transparency PASSED [ 42%]
tests/test_elements_master.py::test_subshell_and_valence_definitions PASSED [ 46%]
tests/test_elements_master.py::test_sha256_checksum_consistency PASSED   [ 50%]
tests/test_similarity_engines.py::test_target_exclusion_and_cardinality[Ga] PASSED [ 53%]
tests/test_similarity_engines.py::test_target_exclusion_and_cardinality[Ti] PASSED [ 57%]
tests/test_similarity_engines.py::test_target_exclusion_and_cardinality[Mo] PASSED [ 61%]
tests/test_similarity_engines.py::test_target_exclusion_and_cardinality[S] PASSED [ 65%]
tests/test_similarity_engines.py::test_target_exclusion_and_cardinality[Ba] PASSED [ 69%]
tests/test_similarity_engines.py::test_target_exclusion_and_cardinality[Sr] PASSED [ 73%]
tests/test_similarity_engines.py::test_target_exclusion_and_cardinality[Pb] PASSED [ 76%]
tests/test_similarity_engines.py::test_target_exclusion_and_cardinality[Bi] PASSED [ 80%]
tests/test_similarity_engines.py::test_target_exclusion_and_cardinality[Te] PASSED [ 84%]
tests/test_similarity_engines.py::test_common_output_schema PASSED       [ 88%]
tests/test_similarity_engines.py::test_score_bounds_and_finiteness PASSED [ 92%]
tests/test_similarity_engines.py::test_determinism_and_reproducibility PASSED [ 96%]
tests/test_similarity_engines.py::test_chemical_sanity_analogues PASSED  [100%]

============================= 26 passed in ~1.2s ==============================
```
