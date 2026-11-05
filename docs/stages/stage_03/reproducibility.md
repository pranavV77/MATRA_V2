# Reproduce and review Stage 3

All paths are under C:Final Project. Existing local .venv and dependencies were used without
installs/upgrades. Environment versions and initial commit are in results/stage_03/run_001/environment.json.
No cloud/remote execution or external dataset retrieval occurred in Stage 3.

- Original engines: results/stage_03/run_001/original_engines, plus Git tag
  matra-stage-03-baseline-02547fa. Existing user changes/presentations were preserved.
- Inputs: data/processed/elements_master.parquet, original atom2vec_embeddings_d20.npz and
  data/raw/mp_nostruct_20181018.json.gz. Raw/processed data and benchmark files were not edited.
- Baseline: baseline.json contains all supported Top-10 results and complete pair matrices.
- Parameters/results: engine_verification.json contains tolerances, full support statuses,
  raw per-call timings, seed, dimension, training counts and corpus checksum.
- New model: fresh_atom2vec_d20.npz, written once; old default cache is unchanged.
- Numerical arrays: score_comparison.npz, load with allow_pickle=False.
- Tests/failures: logs/stage_03/run_001 includes initial, corrected and final executions.
- Figures: score_agreement, regression_checks, warm_latency in both PNG and SVG.

The capture/verification/report scripts refuse reuse of their completed run output. Re-run tests
with a fresh pytest base directory. For a new training experiment, choose a new cache path;
changing embedding_dim against the old cache is an error, not an implicit model replacement.
The same corpus byte checksum and config do not guarantee bitwise portability across BLAS,
SciPy, OS or hardware. Compare similarities/rankings, since SVD vector signs can differ while
their pairwise geometry is unchanged. Current numerical reproducibility is local only.

Rollback, if requested, is limited to restoring the three original engine files from the baseline
Git tag or preserved copies. Keep data/results and unrelated user files intact. The shared new
helper becomes unused under original engines; no deletion/migration is needed. No rollback
was executed, and nothing was pushed to GitHub.
