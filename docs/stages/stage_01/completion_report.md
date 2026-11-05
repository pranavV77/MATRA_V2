# STAGE COMPLETION REPORT — Stage 1

Date: 5 November 2026. Stage: baseline audit and reproducibility. Status: **audit executed with findings; no clean robustness or scientific-validation pass**. Next stage has not started.

## 1. Objective

Verify the existing MATRA implementation locally, preserve prior work, reproduce its documented outputs and expose failures before making scientific or production changes.

## 2. What was implemented

Three audit/report scripts, isolated execution and fixture directories, reproducibility records, figures and stage documentation. Existing Python environment reused. Original algorithms, source tests, data, results and presentations unchanged.

## 3. Files created

Scripts: `experiments/stage_01/audit_baseline.py`, `supplemental_checks.py`, `generate_report.py`. Stage reports and Telugu script under `docs/stages/stage_01`. Progress under `docs/progress.md`. Prior protocol/template/review copied under `docs/evaluation`. Raw evidence, preserved results, isolated regenerated artifacts and figures under `results/stage_01/run_001`. Console logs under `logs/stage_01/run_001`. Full inventory is generated during final verification.

## 4. Existing files modified

None. 47 preexisting files were byte-for-byte unchanged at audit completion; final verification checks again. A lightweight Git tag records baseline HEAD. The preexisting JSON change was timestamp-only and remains intact. No user-owned work was committed or reset.

## 5. Algorithms and methods

SHA256 integrity checks; original pytest suite; isolated subprocess execution; complete 118-element input probing; numerical symmetry/self-similarity checks; malformed-data fixtures; direct independent metric arithmetic; full master regeneration and Atom2Vec SVD retraining; descriptive matplotlib plots. No recommendation algorithm changed.

## 6. Actual outputs and results

Original tests: **26 passed**, pytest reported 1.68 seconds in this execution. Benchmark subprocess wall time: 2.016 seconds. Reproduced ranking, score, overlap and summary fields exactly match the preexisting local results; run metadata naturally differs.

| Method | Hit@1 | Hit@3 | Hit@10 | MRR@10 | Mean Recall@10 |
|---|---:|---:|---:|---:|---:|
| PN | 63.64% | 100.00% | 100.00% | 0.8182 | 96.97% |
| Atom2Vec | 63.64% | 81.82% | 100.00% | 0.7516 | 100.00% |
| Property | 36.36% | 72.73% | 100.00% | 0.5394 | 78.79% |


The 11 legacy cases contain 18 positive entries and only 9 unique target elements. All methods' 100% Hit@10 means at least one listed positive per case, not 100% candidate correctness. No confidence intervals/generalization claim are attached to these small, previously seen reproduction results.

Fresh master generation: 39.967 seconds; all values and original Parquet SHA256 reproduced. Fresh Atom2Vec training: 8.137 seconds; same 79 symbols and 20 dimensions, max pairwise similarity difference 0, all supported Top-10 lists identical. This establishes local reproducibility, not cross-platform guarantees or paper-level exact methodological certification.

Coverage from actual requests: PN 94/118 target elements; Atom2Vec 79/118; Property 88/118. PN's candidate universe is 88 non-noble elements; accepting noble-gas targets is not proof that such substitutions are scientifically applicable.

## 7. Edge cases tested

78 diagnostic records: 63 passed, 15 failed requirements. These are separate from the 26 original pytest cases. The 73 primary probes and 5 supplemental records expose invalid k handling, duplicate acceptance/recommendations, nonfinite and zero cached vectors, negative physical data and cache-dimension mismatch. Full observations and unexecuted cases are in edge_case_report.md and JSON. No executed failure is relabelled a pass.

## 8. Validation results

Functionality verified within the original suite. Cached and fresh numerical reproducibility verified locally. Metric arithmetic verified on the legacy predictions. Robustness failed the expanded requirements. Scientific validity partially assessed, not certified. Overall product readiness not established. See validation_report.md.

## 9. Known issues

- Negative and boolean k accepted by every engine.
- Duplicate master entries accepted; duplicate Al recommendations reproduced in PN and Property.
- Infinite/negative descriptor values and NaN/zero cached vectors lack adequate rejection.
- Cached embedding dimension can disagree with requested dimension.
- Polarizability labels conflict with the installed source library; PN range/normalization metadata conflicts with retained values.
- Fr imputation derivation and full phase-specific provenance are unverified.
- BM-S04 DOI definitely points to unrelated glass literature; BM-P01 direct-experimental evidence classification needs per-claim review.
- No dependency installation manifest; environment freeze records installed versions but is not a verified clean-machine installer.
- System Git status fails; bundled Git works without repository changes.

## 10. Scientific limitations

Element-only engines do not use host/site/concentration. Existing benchmark positives have not all been independently audited. Doping cases remain qualitative. Similarity is not stability or property preservation. Representation-training overlap with known compounds is not excluded. Duplicate formulas in the raw corpus affect weighting but may reflect legitimate polymorph entries; do not drop them without a justified policy.

## 11. Still incomplete

Production fixes are deliberately not folded into an audit-only stage. Stage 2 must correct dataset/provenance issues. Engine-hardening issues are queued for the previously planned engine stage. No later modules started. Complete source-case admission and new held-out benchmark remain pending.

## 12. Telugu audio and transcript

Complete narration: telugu_explanation.md. **No playable Telugu audio generated**: no supported speech tool/Telugu local voice; only English Zira voice detected. No external TTS service used. A full TTS-ready Telugu script is supplied instead, as permitted by the user's fallback requirement.

## 13. Readiness for next stage

The audit has established a reproducible baseline and documented actual failures. This is not a statement that every requirement passed. Stage 2 may begin only after the owner reviews the known defects and explicitly authorizes the dataset/provenance corrections. Engine defects remain tracked and must be fixed in the planned engine stage before reliance on robust candidate generation. No automatic progression.

## Open the results

Open `index.html` in this directory for the browser summary. Actual plots: legacy_metrics.png, element_coverage.png, case_rank_heatmap.png under `results/stage_01/run_001/figures`. Each also has SVG and source data. Technical instructions and rollback notes are in technical_guide.md.
