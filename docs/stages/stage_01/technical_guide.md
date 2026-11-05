# Stage 1 implementation and mentoring guide

## Why these files exist

- `experiments/stage_01/audit_baseline.py`: reads existing source/data/tests, snapshots checksums, runs the original pytest suite, copies source/data to a protected experiment workspace, reproduces benchmark outputs, executes edge probes, rebuilds the master and retrains Atom2Vec. Inputs are existing project files; outputs are append-only run directories. Its helpers compute SHA256, write strict JSON and record subprocess output/exit codes/timing. It refuses an already-started run ID. It imports the actual existing engines; it does not replace them.
- `experiments/stage_01/supplemental_checks.py`: executes actual duplicate-candidate and zero-vector tests, independent metric arithmetic, repeated-run and dependency-missing simulations, and 30-sample warm inference timings. It uses run_001 and refuses overwriting its own result file.
- `experiments/stage_01/generate_report.py`: reads those saved observations; writes reports, figure source data, static PNG/SVG plots and the browser entry point. It makes no model predictions and refuses replacing an existing completion report. The figures are descriptive legacy results, not a fusion improvement claim.
- `docs/stages/stage_01/reference_audit.md`: records source checks, citation mismatches and claims not yet verified. It separates a bad citation from an invalid dopant claim.
- `docs/stages/stage_01/telugu_explanation.md`: complete Telugu narration script and explicit audio limitation.
- `docs/progress.md`: central stage status, approvals, known issues and next-stage gate.
- `docs/evaluation/`: copies of the previously reviewed evaluation protocol/template and historical dataset review. The prior HTML is preserved as a historical review, not silently updated scientific evidence.

The existing `.venv` supplies all dependencies needed here, including matplotlib. No production source or original tests were edited. Experiment fixtures are deliberately damaged copies, not replacement datasets.

## How the isolation works

The legacy benchmark hardcodes `results/runs/...`. Running it at the project root would replace the user's existing output. Instead we copy `src` and `data` under `results/stage_01/run_001/legacy_workspace` and run the original module with that working directory. Its relative paths resolve entirely inside the experiment sandbox. Production code is untouched. Model regeneration saves to new `rebuild` and `fresh` locations there.

## How to reproduce

From PowerShell in `C:Final Project`:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
..venvScriptspython.exe -B -X utf8 experimentsstage_01audit_baseline.py --run-id run_002
```

Use a new run ID. Do not rerun run_001 to overwrite evidence. This command writes a new run's raw audit evidence. The supplemental/report tools currently target run_001; their report-generation configuration must be deliberately adapted and inspected before generating a second report. Do not claim those tools are fully parameterized. Exit code 0 for the audit means execution completed and originals were preserved; inspect summary.json for failed requirements. It does not mean every diagnostic passed.

## Concepts connected to the implementation

**Hash:** SHA256 fingerprints bytes. Equal hashes verify file identity, not chemical truth. Metadata time changes can change a JSON hash even when rankings are identical.

**PN similarity:** `1/(1+abs(PN_target-PN_candidate))`. Ga=83 and Al=82 gives 0.5. A chemical ordering is a cheap element-level heuristic. It does not use host structure.

**Property similarity:** each descriptor is standardized as `(value-mean)/standard_deviation`, then rows are normalized and their dot product gives cosine similarity. A radius 130, mean 100, standard deviation 20 becomes 1.5. The selected descriptor set and correlated features shape the result. A pure change of units by a positive constant cancels under feature standardization but labels still must be scientifically correct.

**Atom2Vec:** formula-derived atom/environments form a sparse count matrix. Row normalization and truncated SVD retain 20 latent dimensions. Cosine similarity compares normalized vectors. We compare pairwise similarities when regenerating because vector signs/rotations can change without changing similarity; in this local reproduction, pairwise differences were exactly zero.

**Recall versus Hit:** for two documented options Al and In, returning only In in Top-10 gives Hit@10=1 but Recall@10=1/2. Thus all three methods can have 100% Hit@10 without equal recall.

**MRR@10:** a first positive at rank 1 contributes 1; at rank 2, 0.5; no positive in Top-10, 0. Legacy output calls this MRR but only searches Top-10. Full-list MRR is a separate quantity. Existing arbitrary missed-rank value 88 is a latent reporting defect; current primary cases all have a positive in Top-10 so it does not affect this reproduced mean-best-rank result.

**Fixtures:** synthetic inputs used to test a specific failure. An invalid density fixture tests software validation; it is not experimental evidence about a real material.

**Input validation:** Python accepts `True` as an integer and negative slice endpoints. Thus `candidates[:-1]` returns nearly the entire list. Validation must precede slicing; this stage demonstrates the issue without changing the engines.

## Limits of this stage

No fusion, site-aware generation, formation-energy prediction, gap preservation, electrical activation, new benchmark curation or production interface was implemented. Small legacy results do not establish generalization or universal elemental coverage. Measured runtimes are single-machine local observations; warm inference excludes engine startup, training and network operations. No unsupported DFT-speedup claim is made.

## Rollback and preservation

Original files were not modified. Baseline commit/tag, preexisting diff, original hashes and backup result copies are under run_001. Do not use `git reset --hard` or `git clean` to remove audit files: that could destroy the user's preexisting results or presentations. If removal is requested later, enumerate the newly created stage paths and remove only approved paths. The lightweight tag points to the original commit; the saved patch and hashes preserve the dirty baseline information separately.
