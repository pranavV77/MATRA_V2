# Task 1 & Task 2 Milestone Artifact Manifest

This manifest documents all filesystem artifacts comprising the completed, audited, and frozen Tasks 1 and 2 milestone.

---

## 1. Primary Milestone Artifact Checksums (Integrity Verification)

The following cryptographic SHA256 checksums uniquely freeze the current milestone state:

| Artifact Path | Format | Role | Cryptographic SHA256 Checksum |
|---|---|---|---|
| `data/processed/elements_master.parquet` | Parquet (Binary) | Master elemental table ($Z=1\text{--}94$, 14 features) | `0d9c1790b211e5e47651ec6930bcb259db36b82acc8efabb720fa26fd6fc651a` |
| `data/processed/feature_metadata.json` | JSON | Feature provenance and imputation metadata | `479e0d5927d1435babd1a7620d13d06296d521926add2239bb3f592144537f07` |
| `data/benchmark/benchmark_cases.json` | JSON | 11 primary substitution cases & 5 secondary dopants | `446072ab803fb9a68203bbffbce0aef7349d30b76dac5e9c9ff59f1471063081` |
| `data/processed/atom2vec_embeddings_d20.npz` | NumPy NPZ (Compressed) | Trained Atom2Vec representations ($79 \times 20$) | `f198c4e0f6d74824637016f1804b601d444dfaa471d31977ab190897aa702935` |
| `results/runs/task2_benchmark_evaluation.json` | JSON | Full benchmark evaluation runs and rankings | `801a74d0db441c1f632332a55a979eb53e8b2e8c76af867686a0ff7f936b6a47` |
| `results/tables/benchmark_metrics_summary.md` | Markdown | Formatted summary tables for academic report | `ac6dd48efd6089bd01c1a0af26833ad2ad434047b0ddf0710bdb95dbbb79dcba` |

---

## 2. Directory Structure & File Inventory

### `data/` (Datasets, Provenance, and Benchmark)
- `data/raw/mp_nostruct_20181018.json.gz`: Raw Materials Project inorganic formulas snapshot (83,989 entries) used to extract atom-environment co-occurrence pairs for Atom2Vec.
- `data/processed/elements_master.parquet`: Master elemental feature table containing 94 elements and 14 continuous physical properties.
- `data/processed/feature_metadata.json`: Feature extraction metadata recording library versions (`mendeleev 1.2.0`, `pymatgen 2025.10.7`), Villars PN convention, and transparent imputation lists.
- `data/processed/atom2vec_embeddings_d20.npz`: Cached $79 \times 20$ representation matrix $F = \tilde{U}\tilde{D}$ trained on MP formulas via truncated SVD.
- `data/benchmark/benchmark_cases.json`: Curated substitution benchmark containing 11 primary substitution cases (18 ground-truth targets) and 5 secondary doping cases with complete Wyckoff site provenance.

### `src/` (Production Source Code)
- `src/__init__.py`: Package initialization.
- `src/features/__init__.py`: Features package initialization.
- `src/features/villars_pn.py`: Hardcoded dictionary mapping elements $Z=1\text{--}94$ to Pierre Villars Mendeleev Periodic Numbers.
- `src/features/build_elements_master.py`: Pipeline script to extract, clean, impute, validate, and export `elements_master.parquet`.
- `src/pn_similarity/__init__.py`: PN similarity package initialization.
- `src/pn_similarity/pn_engine.py`: Independent Pierre Villars PN similarity engine (`PNSimilarityEngine`).
- `src/atom2vec/__init__.py`: Atom2Vec package initialization.
- `src/atom2vec/atom2vec_engine.py`: Independent model-free Atom2Vec representation and similarity engine (`Atom2VecEngine`).
- `src/property_similarity/__init__.py`: Property similarity package initialization.
- `src/property_similarity/property_engine.py`: Independent continuous physicochemical property cosine similarity engine (`PropertySimilarityEngine`).
- `src/benchmark/__init__.py`: Benchmark package initialization.
- `src/benchmark/evaluate_benchmark.py`: Benchmark evaluation runner computing Hit@K, MRR, Mean Best Rank, Recall@10, and pairwise Jaccard overlap.
- `src/utils/__init__.py`: Shared utilities package initialization.

### `tests/` (Automated Test Suite)
- `tests/__init__.py`: Tests package initialization.
- `tests/test_elements_master.py`: 7 pytest unit tests verifying element counts, Villars PN anchors, noble gas NaN handling, physical bounds, imputation flags, subshell rules, and SHA256 integrity.
- `tests/test_benchmark.py`: 6 pytest unit tests verifying benchmark JSON schema, primary/secondary separation, evidence fields, target cardinality, and absence of rejected cases.
- `tests/test_similarity_engines.py`: 13 pytest unit tests verifying target element exclusion, Top-10 cardinality, schema conformity, score bounds $[-1, 1]$, determinism, and chemical analogue recovery.

### `results/` (Evaluation Runs & Markdown Tables)
- `results/runs/task2_benchmark_evaluation.json`: Complete machine-readable record of all Top-10 candidate shortlists, scores, and benchmark metrics across the 11 primary cases.
- `results/tables/benchmark_metrics_summary.md`: Summary Markdown tables detailing overall benchmark performance, pairwise Jaccard overlap, and the $\beta\text{-Ga}_2\text{O}_3 \to \text{Ga}$ headline demonstration.

### `docs/` (Academic Planning, References, and Milestone Reports)
- `docs/idea/Project phase doc.pdf`: Initial project proposal and scope submitted to Amrita School of Computing.
- `docs/idea/Project_Phase_2__Submission_2 (2) (1).pdf`: Official Project Phase II Submission 2 Design and Solution document.
- `docs/references/`: Collection of primary peer-reviewed reference papers (Zhou et al. Atom2Vec 2018, Oran et al. PNcsp 2024, PNcsp+ 2026, Kusaba et al. PTG 2021, Wang et al. CrabNet 2021).
- `docs/Task_1_2_Final_Milestone_Report.md`: Comprehensive academic report summarizing Tasks 1 & 2 methodology, findings, and results.
- `docs/Task_1_2_Reproducibility.md`: Step-by-step reproduction guide with exact commands and expected outputs.
- `docs/Task_1_2_Milestone_Manifest.md`: This artifact manifest and checksum inventory.
- `docs/Task_1_2_Submission_Checklist.md`: Detailed compliance checklist mapped to academic evaluation requirements.
