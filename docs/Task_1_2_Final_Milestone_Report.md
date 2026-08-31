# Final Milestone Report: Tasks 1 & 2 Audit, Verification, and Freeze

**Project Title:** Explainable AI-Based Element Recommendation Framework for Functional Materials Using Unsupervised Representation Learning  
**Course Code:** 23CSE498 – Project Phase II, Amrita Vishwa Vidyapeetham  
**Academic Year:** 2026–2027  
**Authors:** V G Pranav Suraj (AM.SC.U4CSE23366), T Ruthvik Rao (AM.SC.U4CSE23364)  
**Project Guide:** Ms. Remya V S  
**Milestone Date:** August 31, 2026  
**Milestone Status:** Tasks 1 & 2 Completed, Audited, and Frozen  

---

## 1. Purpose of the Current Milestone

The complete 22-stage architecture of this project spans multi-signal similarity fusion, GNN-based formation energy estimation (MACE, M3GNet), structural database matching (Materials Project, OQMD), deep learning baseline comparisons (DeepOFM), and explainable narrative generation (SHAP + Gemini API). 

To ensure rigorous scientific validity before multi-signal integration, the current intermediate academic submission milestone freezes and validates the foundational representation and benchmarking layer (**Task 1 and Task 2**):
- **Task 1:** Construction of an audited 94-element master physical descriptor dataset and curation of an independently verified crystallographic substitution benchmark.
- **Task 2:** Implementation, validation, and benchmarking of three independent, uncoupled similarity engines (PN, Atom2Vec, and Physicochemical Property Similarity), demonstrated on real functional materials with a headline case study on $\beta\text{-Ga}_2\text{O}_3 \to \text{Ga}$.

---

## 2. Milestone Requirements Specification

### 2.1 Task 1 Requirements
1. **Master Elemental Table:** Extract and curate elemental properties for $Z=1\text{--}94$ from `mendeleev 1.2.0` and `pymatgen 2025.10.7`. Maintain transparent imputation logging for unavoidable missing values in unstable elements. Noble-gas electronegativities must remain strictly `NaN` without artificial zero-imputation.
2. **Benchmark Construction:** Curate 10–20 scientifically verified substitution cases from literature and crystallography databases. Distinguish isostructural bulk substitutions (`EXPERIMENTAL_DIRECT`) from dilute dopant cases (`DOPING_CONTEXT`). Prevent evaluation leakage.

### 2.2 Task 2 Requirements
1. **Three Independent Engines:** Implement Signal 1 (PN Similarity), Signal 2 (Atom2Vec SVD), and Signal 3 (Property Similarity). The three engines must remain strictly independent (zero premature score fusion).
2. **Common Output Format:** Standardize candidate ranking records across all engines (`method`, `target_element`, `rank`, `candidate_element`, `similarity_score`).
3. **Headline Demonstration:** Demonstrate all three engines on $\beta\text{-Ga}_2\text{O}_3 \to \text{Ga}$, comparing Top-10 candidates against primary substitutions ($\text{Al}, \text{In}$) and secondary dopants ($\text{Si}, \text{Sn}$).
4. **Quantitative Evaluation:** Compute multi-target Hit@1, Hit@3, Hit@5, Hit@10, Mean Reciprocal Rank (MRR), Mean Best Rank, Mean Recall@10, and pairwise Top-10 Jaccard overlap across all primary benchmark cases.

---

## 3. Completed Implementation Architecture

The codebase has been organized into a modular, production-ready structure:
- `src/features/villars_pn.py`: Hardcoded lookup table for Pierre Villars Mendeleev Periodic Numbers ($Z=1\text{--}94$).
- `src/features/build_elements_master.py`: Dataset generation pipeline extracting physical features, applying documented imputation, and computing cryptographic checksums.
- `src/pn_similarity/pn_engine.py`: Independent Pierre Villars PN similarity engine.
- `src/atom2vec/atom2vec_engine.py`: Independent Atom2Vec SVD co-occurrence engine with automated model caching.
- `src/property_similarity/property_engine.py`: Independent 14-feature continuous property cosine similarity engine.
- `src/benchmark/evaluate_benchmark.py`: Comprehensive benchmark runner computing quantitative metrics.
- `tests/test_elements_master.py`, `tests/test_benchmark.py`, `tests/test_similarity_engines.py`: Automated pytest test suite containing 26 unit tests.

---

## 4. Master Elemental Feature Table (`data/processed/elements_master.parquet`)

- **Dimensions:** Exactly 94 rows $\times$ 25 columns ($Z=1\text{--}94$, $\text{H}$ to $\text{Pu}$).
- **Format:** Apache Parquet (binary columnar, snappy compression).
- **Cryptographic SHA256 Checksum:** `0d9c1790b211e5e47651ec6930bcb259db36b82acc8efabb720fa26fd6fc651a`.
- **14 Audited Physical Properties:**
  1. `pauling_electronegativity`: Dimensionless; noble gases ($\text{He}, \text{Ne}, \text{Ar}$) are preserved strictly as `NaN` (0 NaNs for all other 91 elements).
  2. `covalent_radius_cordero`: Covalent radius in pm (Cordero et al., 2008). 0 NaNs.
  3. `atomic_radius_slater`: Slater empirical radius in pm. Imputed for $\text{Kr}, \text{Xe}, \text{At}, \text{Rn}, \text{Fr}$ via linear regression on Cordero radius ($R^2 = 0.963$). Flagged in `imputed_atomic_radius`.
  4. `first_ionization_energy`: Atomic first ionization energy in eV. 0 NaNs.
  5. `melting_point`: Melting point in K (`mendeleev` / `pymatgen` Element database). 0 NaNs.
  6. `thermal_conductivity`: In $\text{W}/(\text{m}\cdot\text{K})$ (`pymatgen` Element database; harmonic extrapolation for $\text{Fr}$). Flagged in `imputed_thermal_conductivity`.
  7. `dipole_polarizability`: Static dipole polarizability in $\text{\AA}^3$. 0 NaNs.
  8. `valence_electrons`: Formal valence from `mendeleev.Element.nvalence()`.
  9. `s_valence_electrons`: Active $s$-subshell count ($0\text{--}2$).
  10. `p_valence_electrons`: Active $p$-subshell count ($0\text{--}6$).
  11. `d_valence_electrons`: Active $d$-subshell count ($0\text{--}10$).
  12. `f_valence_electrons`: Active $f$-subshell count ($0\text{--}14$).
  13. `density`: STP mass density in $\text{g}/\text{cm}^3$. 0 NaNs.
  14. `molar_volume`: Condensed molar volume in $\text{cm}^3/\text{mol}$. 0 NaNs.
- **Valence/Core Convention:** Closed $4f^{14}$ shells in post-lanthanide elements ($\text{Hf}\text{--}\text{Bi}$) and closed $d^{10}$ shells in main-group elements are treated as non-valence core electrons, matching library-specific conventions rather than a blanket subshell conservation identity.
- **Imputation Transparency:** Recorded in `data/processed/feature_metadata.json` with boolean indicators. Only 5 elements have imputed physical properties ($\text{Kr}, \text{Xe}, \text{At}, \text{Rn}, \text{Fr}$).

---

## 5. Substitution Benchmark Description (`data/benchmark/benchmark_cases.json`)

- **Total Primary Cases:** Exactly **11 cases** ($N=11$).
- **Total Verified Ground-Truth Substituent Targets:** Exactly **18 targets**.
- **Evidence Label:** All primary cases are classified as `EXPERIMENTAL_DIRECT` (experimentally synthesized isostructural solid solutions with confirmed single-phase retention).
- **Secondary Dilute Doping Cases:** Exactly **5 cases** classified as `DOPING_CONTEXT` (contextual/qualitative only; strictly excluded from quantitative metrics).
- **Cryptographic SHA256 Checksum:** `446072ab803fb9a68203bbffbce0aef7349d30b76dac5e9c9ff59f1471063081`.

### Primary Benchmark Cases Summary:
| Case ID | Formula | Target Element | Host Wyckoff Site | Coordination | Known Substituents ($V_i$) | Experimental Phase / Solid Solution | Key Reference |
|---|---|---|---|---|---|---|---|
| **BM-P01** | $\text{Ga}_2\text{O}_3$ | $\text{Ga}$ | Octahedral $\text{Ga}_{\text{II}}$ ($4i$) | 6-fold | $\{\text{Al}, \text{In}\}$ | $(\text{Al}_x\text{Ga}_{1-x})_2\text{O}_3$ ($x \le 0.70$); $(\text{In}_x\text{Ga}_{1-x})_2\text{O}_3$ ($x \le 0.35$) | Peelaers et al., APL 2018 |
| **BM-P02** | $\text{GaN}$ | $\text{Ga}$ | Tetrahedral ($2b$) | 4-fold | $\{\text{Al}, \text{In}\}$ | $\text{Al}_x\text{Ga}_{1-x}\text{N}$ ($0 \le x \le 1$); $\text{In}_x\text{Ga}_{1-x}\text{N}$ ($x \le 0.40$) | Ambacher, J. Phys. D 1998 |
| **BM-P03** | $\text{MoS}_2$ | $\text{Mo}$ | Trigonal Prismatic ($2c$) | 6-fold | $\{\text{W}\}$ | $\text{Mo}_{1-x}\text{W}_x\text{S}_2$ ($0 \le x \le 1$) | Chen et al., ACS Nano 2013 |
| **BM-P04** | $\text{MoS}_2$ | $\text{S}$ | Trigonal ($4f$) | 3-fold | $\{\text{Se}\}$ | $\text{MoS}_{2(1-x)}\text{Se}_{2x}$ ($0 \le x \le 1$) | Gong et al., Nano Lett. 2014 |
| **BM-P05** | $\text{BaTiO}_3$ | $\text{Ti}$ | Octahedral ($1b$) | 6-fold | $\{\text{Zr}, \text{Sn}, \text{Hf}\}$ | $\text{BaTi}_{1-x}\text{M}_x\text{O}_3$ ($0 \le x \le 1$) | Ravez et al., Ferroelectrics 1990 |
| **BM-P06** | $\text{BaTiO}_3$ | $\text{Ba}$ | Cuboctahedral ($1a$) | 12-fold | $\{\text{Sr}, \text{Ca}\}$ | $\text{Ba}_{1-x}\text{Sr}_x\text{TiO}_3$ ($0 \le x \le 1$); $\text{Ba}_{1-x}\text{Ca}_x\text{TiO}_3$ ($x \le 0.30$) | Landolt-Börnstein III/36A |
| **BM-P07** | $\text{SrTiO}_3$ | $\text{Ti}$ | Octahedral ($1b$) | 6-fold | $\{\text{Zr}, \text{Hf}\}$ | $\text{SrTi}_{1-x}\text{M}_x\text{O}_3$ ($0 \le x \le 1$) | MP `mp-4648`, ICSD-89258 |
| **BM-P08** | $\text{SrTiO}_3$ | $\text{Sr}$ | Cuboctahedral ($1a$) | 12-fold | $\{\text{Ba}, \text{Ca}\}$ | $\text{Sr}_{1-x}\text{Ba}_x\text{TiO}_3$ ($0 \le x \le 1$); $\text{Sr}_{1-x}\text{Ca}_x\text{TiO}_3$ ($0 \le x \le 1$) | MP `mp-4648`, ICSD-24111 |
| **BM-P09** | $\text{CsPbI}_3$ | $\text{Pb}$ | Octahedral ($1b$) | 6-fold | $\{\text{Sn}\}$ | $\text{CsPb}_{1-x}\text{Sn}_x\text{I}_3$ ($0 \le x \le 1$) | Stoumpos et al., JACS 2013 |
| **BM-P10** | $\text{Bi}_2\text{Te}_3$ | $\text{Bi}$ | Octahedral ($6c$) | 6-fold | $\{\text{Sb}\}$ | $(\text{Bi}_{1-x}\text{Sb}_x)_2\text{Te}_3$ ($0 \le x \le 1$) | Poudel et al., Science 2008 |
| **BM-P11** | $\text{Bi}_2\text{Te}_3$ | $\text{Te}$ | Octahedral/Mixed ($3a/6c$) | 6-fold | $\{\text{Se}\}$ | $\text{Bi}_2(\text{Te}_{1-x}\text{Se}_x)_3$ ($0 \le x \le 1$) | MP `mp-1204`, ICSD-627122 |

---

## 6. Similarity Engine Methodologies & Academic Terminology

### 6.1 Signal 1: PN Similarity
- **Terminology:** **Faithful adaptation** of the Pierre Villars Mendeleev Periodic Number representation.
- **Reference:** Villars et al., *Chem. Met. Alloys* (2008); Oran et al., *Inorg. Chem.* (2024), *JCTC* (2026).
- **Formulation:** 
  $$S_{PN}(e_t, e_c) = \frac{1}{1 + |PN(e_t) - PN(e_c)|}$$
- **Methodology Note:** In Oran et al., crystal structure similarity is evaluated via integer distance differences $|PN_i - PN_j|$. Our implementation adapts this integer difference into a smooth, bounded $[0, 1]$ similarity metric with $S(e, e) = 1.0$, which preserves rank order and accommodates subsequent similarity fusion.
- **Candidate Universe:** 88 non-noble elements. Target element $e_t$ is strictly excluded ($e_c \ne e_t$).

### 6.2 Signal 2: Atom2Vec Similarity
- **Terminology:** **Faithful reproduction of the implemented model-free formulation**.
- **Reference:** Zhou et al., "Atom2Vec: Learning Atoms for Materials Discovery", *Proc. Natl. Acad. Sci. USA*, 115, 6411–6417 (2018).
- **Corpus & Filtering:** Materials Project snapshot (`mp_nostruct_20181018.json.gz`, 83,989 formulas). Filtered to stoichiometric binary, ternary, and quaternary inorganic compounds.
- **Atom-Environment Co-Occurrence Matrix:** Constituent elements are extracted into $(A, (c)R)$ environments. Applying Zhou et al.'s $\ge 1\%$ frequency threshold yields $N = 79$ common chemical symbols and $M = 83,664$ unique environments.
- **Normalization & Decomposition:** Row-wise $L_2$ normalization ($p=2$): $X_{i,j} / \sqrt{\sum_k X_{i,k}^2}$. Truncated SVD via `scipy.sparse.linalg.svds` with $d=20$ leading singular values ($F = \tilde{U}\tilde{D}$) and fixed seed 42.
- **Similarity Metric:** Cosine similarity over normalized row vectors of $F$. Excludes target element $e_t$.

### 6.3 Signal 3: Physicochemical Property Similarity
- **Terminology:** **Designed physicochemical property cosine model**.
- **Methodology Note:** This is an independent, continuous property vector cosine similarity model designed for this framework using our 14 audited physical features. It is not an exact reproduction of PTG (Kusaba et al., *Sci. Rep.* 2021), which utilized Generative Topographic Mapping (GTM-LDLV) to reconstruct 2D periodic grids.
- **Formulation:** Features are Z-score normalized across the 88 non-noble elements ($\mu_k, \sigma_k$), projected to unit length, and evaluated via cosine similarity:
  $$S_{prop}(e_t, e_c) = \frac{\vec{v}_t \cdot \vec{v}_c}{\|\vec{v}_t\| \|\vec{v}_c\|}$$
  Target element $e_t$ is strictly excluded ($e_c \ne e_t$).

---

## 7. Headline Demonstration: $\beta\text{-Ga}_2\text{O}_3 \to \text{Ga}$

Demonstration on monoclinic $\beta\text{-Ga}_2\text{O}_3$ targeting the octahedral $\text{Ga}_{\text{II}}$ ($4i$) site:
- **Verified Primary Substituents:** $\text{Al}, \text{In}$
- **Verified Secondary Dopants:** $\text{Si}, \text{Sn}$

| Rank | PN Engine Candidate (Sim) | Atom2Vec Candidate (Sim) | Property Candidate (Sim) |
|:---:|---|---|---|
| **1** | **Al** (0.5000) $\big[\text{Primary GT}\big]$ | **Al** (0.8462) $\big[\text{Primary GT}\big]$ | **In** (0.8771) $\big[\text{Primary GT}\big]$ |
| **2** | **In** (0.5000) $\big[\text{Primary GT}\big]$ | **In** (0.7601) $\big[\text{Primary GT}\big]$ | **Sn** (0.8389) $\big[\text{Secondary Dopant}\big]$ |
| **3** | **B** (0.3333) | **Y** (0.7573) | **Ge** (0.7352) |
| **4** | **Tl** (0.3333) | **Bi** (0.6505) | **P** (0.6226) |
| **5** | **C** (0.2000) | **La** (0.6175) | **Tl** (0.6177) |
| **6** | **Hg** (0.2000) | **Sn** (0.6046) $\big[\text{Secondary Dopant}\big]$ | **Bi** (0.6172) |
| **7** | **Cd** (0.1667) | **Sb** (0.5698) | **Pb** (0.5930) |
| **8** | **Si** (0.1667) $\big[\text{Secondary Dopant}\big]$ | **Ti** (0.5373) | **Sb** (0.5788) |
| **9** | **Ge** (0.1429) | **Sc** (0.4963) | **S** (0.5427) |
| **10** | **Zn** (0.1429) | **Zn** (0.4661) | **Se** (0.5259) |

### Demonstration Insights:
1. **Primary Ground Truth:** Both PN and Atom2Vec place $\text{Al}$ and $\text{In}$ at **Rank 1 and Rank 2**. Property similarity places $\text{In}$ at **Rank 1**.
2. **Doping Context Separation:** $\text{Si}$ and $\text{Sn}$ appear in the Top-10 across the engines, reflecting their geometric compatibility as shallow donors. However, they are correctly quarantined from positive primary ground-truth credit.

---

## 8. Full Benchmark Evaluation Results

Evaluated across all 11 primary cases (18 ground-truth targets):

### 8.1 Summary Performance Metrics:
| Method | Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR | Mean Best Rank | Mean Recall@10 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **PN Similarity** | **63.6%** | **100.0%** | **100.0%** | **100.0%** | **0.8182** | **1.36** | **97.0%** |
| **Atom2Vec** | **63.6%** | **81.8%** | **81.8%** | **100.0%** | **0.7516** | **2.36** | **100.0%** |
| **Property Similarity** | **36.4%** | **72.7%** | **90.9%** | **100.0%** | **0.5394** | **3.09** | **78.8%** |

### 8.2 Pairwise Method Top-10 Jaccard Overlap:
- **PN vs. Atom2Vec:** $0.2347$ ($\approx 23.5\%$)
- **PN vs. Property:** $0.3341$ ($\approx 33.4\%$)
- **Atom2Vec vs. Property:** $0.1906$ ($\approx 19.1\%$)
- *Interpretation:* The three signals exhibit low pairwise overlap ($19\text{--}33\%$), demonstrating that each captures complementary representations: periodic table coordinates, empirical co-occurrence statistics, and continuous physical property vectors.

### 8.3 Case-by-Case Breakdown:
| Case ID | Formula | Target | Known GT | PN Top-5 (Best Rank) | Atom2Vec Top-5 (Best Rank) | Property Top-5 (Best Rank) |
|---|---|---|---|---|---|---|
| **BM-P01** | $\text{Ga}_2\text{O}_3$ | $\text{Ga}$ | $\{\text{Al}, \text{In}\}$ | Al, In, B, Tl, C (**R1**) | Al, In, Y, Bi, La (**R1**) | In, Sn, Ge, P, Tl (**R1**) |
| **BM-P02** | $\text{GaN}$ | $\text{Ga}$ | $\{\text{Al}, \text{In}\}$ | Al, In, B, Tl, C (**R1**) | Al, In, Y, Bi, La (**R1**) | In, Sn, Ge, P, Tl (**R1**) |
| **BM-P03** | $\text{MoS}_2$ | $\text{Mo}$ | $\{\text{W}\}$ | Cr, W, Mn, Ta, Nb (**R2**) | W, Cr, Sb, Re, Ti (**R1**) | Ru, Cr, Rh, Nb, Pd (**R10**) |
| **BM-P04** | $\text{MoS}_2$ | $\text{S}$ | $\{\text{Se}\}$ | O, Se, Te, Bi, Po (**R2**) | Te, Se, O, Mg, N (**R2**) | Se, P, Br, As, I (**R1**) |
| **BM-P05** | $\text{BaTiO}_3$ | $\text{Ti}$ | $\{\text{Zr}, \text{Sn}, \text{Hf}\}$ | Zr, Hf, V, Nb, Ta (**R1**) | Sn, Bi, Si, Sb, Cr (**R1**) | V, Sc, Zr, Y, Hf (**R3**) |
| **BM-P06** | $\text{BaTiO}_3$ | $\text{Ba}$ | $\{\text{Sr}, \text{Ca}\}$ | Ra, Sr, Ca, Sc, Fr (**R2**) | Sr, Ca, Eu, Y, Cd (**R1**) | Ra, La, Sr, Ce, Ac (**R3**) |
| **BM-P07** | $\text{SrTiO}_3$ | $\text{Ti}$ | $\{\text{Zr}, \text{Hf}\}$ | Zr, Hf, V, Nb, Ta (**R1**) | Sn, Bi, Si, Sb, Cr (**R7**) | V, Sc, Zr, Y, Hf (**R3**) |
| **BM-P08** | $\text{SrTiO}_3$ | $\text{Sr}$ | $\{\text{Ba}, \text{Ca}\}$ | Ba, Ca, Fr, Ra, Cs (**R1**) | Ba, Ca, Y, Zn, Eu (**R1**) | Ba, Ra, La, Ce, Y (**R1**) |
| **BM-P09** | $\text{CsPbI}_3$ | $\text{Pb}$ | $\{\text{Sn}\}$ | Sn, Ge, N, P, Si (**R1**) | Cd, Hg, Zn, Be, Tl (**R8**) | Tl, Bi, Po, Sn, Sb (**R4**) |
| **BM-P10** | $\text{Bi}_2\text{Te}_3$ | $\text{Bi}$ | $\{\text{Sb}\}$ | Sb, As, O, P, S (**R1**) | Sb, Ti, Sn, V, Cr (**R1**) | Po, Pb, Sb, Te, At (**R3**) |
| **BM-P11** | $\text{Bi}_2\text{Te}_3$ | $\text{Te}$ | $\{\text{Se}\}$ | Po, Se, S, H, O (**R2**) | S, Se, Ge, Sb, Si (**R2**) | Sb, At, I, Se, Br (**R4**) |

---

## 9. Automated Testing & Verification

Running `pytest tests/ -v` executes 26 tests across three test suites:
- `tests/test_benchmark.py`: 6 tests verifying JSON schema, primary/secondary separation, evidence fields, target cardinality, and absence of rejected cases.
- `tests/test_elements_master.py`: 7 tests asserting 94-element coverage, Villars PN anchors, noble gas NaN electronegativity, physical bounds, imputation flags, subshell rules, and SHA256 consistency.
- `tests/test_similarity_engines.py`: 13 tests asserting target exclusion, Top-10 cardinality, schema compliance, score boundedness $[-1, 1]$, determinism, and chemical analogue recovery.

**Test Summary:** Exactly **26 tests passed in 1.26s**, 0 failures, 0 errors.

---

## 10. Data Leakage & Integrity Audit

- **Quarantined Ground Truth:** The benchmark answers (`known_substituents`) reside exclusively in `data/benchmark/benchmark_cases.json`. They are never passed to `PNSimilarityEngine`, `Atom2VecEngine`, or `PropertySimilarityEngine`.
- **Blind Candidate Generation:** Engines receive only `target_element` (e.g. `'Ga'`) and generate Top-K shortlists purely from unsupervised representations. Ground-truth matching is performed post-hoc solely by the evaluation script.
- **Zero Embedding Contamination:** Neither the 14 physical properties in `elements_master.parquet` nor the 20-dimensional SVD vectors in `atom2vec_embeddings_d20.npz` incorporate benchmark labels or substitution task definitions.

---

## 11. Known Scientific Limitations

1. **Atom2Vec Vocabulary Coverage:** Bounded to 79 common elements due to the $\ge 1\%$ frequency threshold in Materials Project formulas. Rare transuranics ($Z \ge 93$) and noble gases are absent from Atom2Vec representations.
2. **Transition Metal Property Clustering:** Continuous property cosine similarity clusters transition metals closely by density and valence shell configurations, which can rank 4d congeners above 5d isovalent counterparts (e.g. $\text{Ru}$ before $\text{W}$ for $\text{Mo}$).
3. **Concentration-Agnostic Representation:** At this foundational stage, similarities reflect element-level substitutability and do not yet evaluate solubility limits or formation energies of specific compositions (deferred to future GNN and convex-hull stages).

---

## 12. Division of Milestones: Current Scope vs. Future Stages

### Completed for Current Academic Milestone (Tasks 1 & 2):
- [x] Curated 94-element master physical descriptor table (`elements_master.parquet`)
- [x] Curated 11-case crystallographic substitution benchmark with site provenance (`benchmark_cases.json`)
- [x] Implemented independent Pierre Villars PN similarity engine (`src/pn_similarity/`)
- [x] Implemented independent Atom2Vec SVD co-occurrence engine (`src/atom2vec/`)
- [x] Implemented independent Physicochemical Property cosine similarity engine (`src/property_similarity/`)
- [x] Generated individual Top-10 shortlists for all benchmark materials
- [x] Performed headline demonstration on $\beta\text{-Ga}_2\text{O}_3 \to \text{Ga}$ distinguishing primary substitution from dilute doping
- [x] Evaluated multi-target Hit@K, MRR, Mean Best Rank, and Recall@10
- [x] Validated with 26 automated unit tests and frozen artifact checksums

### Preserved for Future Project Stages (Do Not Start Yet):
- Multi-signal weighted score fusion ($S = w_1 S_{PN} + w_2 S_{comp} + w_3 S_{prop}$)
- GNN-based formation energy estimation (MACE, M3GNet)
- Structural database cross-matching (Materials Project API, OQMD)
- DeepOFM orbital field matrix baseline comparison
- Explainable narrative generation (SHAP feature attribution + Gemini API)
- Interactive web application (FastAPI backend + React frontend)
