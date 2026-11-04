# Stage 2 code and reproduction guide

## File responsibilities

- `src/data_audit/schema.py`: authoritative unit-explicit feature names, legacy-name mapping, expected native gaps for the pinned release, and upstream-density estimate flags. This is a new data contract, not a recommendation model.
- `src/data_audit/validation.py`: checks identities, dimensions, units, finiteness, bounds, provenance equality, missingness, registry truthfulness and benchmark admission. It raises DataValidationError. A data-validation pass establishes contract consistency, not chemical truth.
- `src/data_audit/release.py`: reads frozen local source snapshots, prepares native data/provenance, fits separately stored radius estimates, creates the coverage registry and evidence-review ledger, validates in memory, and writes only into empty versioned output directories. No existing engines are modified or redirected.
- `experiments/stage_02/collect_sources.py`: captures actual pinned-library values and DOI metadata. It reads existing feature conventions and records warnings. HTTPS requests fetch bibliographic data; all execution and storage are local. It is not a literature-truth oracle. The source snapshot and network records are intentionally frozen after capture.
- `tests/stage_02/test_data_release.py`: actual new tests for scientific units, native missingness, provenance, estimates, registry scope, admission controls, corrupt inputs, reproducibility and overwrite/path safeguards.
- `experiments/stage_02/build_reports.py`: reads completed artifacts and tests, builds plots, full native/registry/provenance viewer, stage reports and final review summary. It refuses replacing an existing completion report.
- `experiments/stage_02/verify_release.py`: final data checks, hashes, report links, code compilation and Git status capture. It runs after report generation.

The preexisting source builder/tests are preserved as a reproducible legacy baseline; their known wrong comments are superseded by the versioned release documentation, not silently rewritten.

## How to run

In PowerShell at `C:Final Project`, rebuild to NEW empty locations:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
..venvScriptspython.exe -B -X utf8 -m src.data_audit.release `
  --data-output results/stage_02/rebuild_002/native `
  --benchmark-output results/stage_02/rebuild_002/benchmark
```

The offline release rebuild uses source_snapshot.json and cached DOI metadata. It does not need network. All paths are resolved and must stay inside the project root. The existing versioned release is intentionally not replaceable. To rerun tests, choose a NEW basetemp and log/output location so evidence is preserved. The exact executed final command is in logs/stage_02/run_001/final_tests.txt and the experiment manifest.

Dependencies reuse the existing Python 3.10.11 environment; no packages were installed or upgraded. environment_freeze.txt records observations, not a verified clean-machine installation recipe. pip check passed.

## Why the engines still use legacy data

The native table has explicit units in its field names and genuine missing values. Automatically switching the old 14-feature engine would either fail or hide a new imputation policy. Stage 3 must explicitly decide support and missing-data behavior and compare any resulting ranking changes. No silent change to inference is made here.

## Reproducibility and rollback

The source snapshot and emitted tables, registry, provenance, estimates and benchmark ledger reproduce exactly in the persisted-artifact tests. Release timestamps are administrative metadata and may change for a newly created release. No live API response is assumed permanent.

Original tracked files are protected by starting hashes and a saved diff. The Stage 2 baseline tag is matra-stage-02-baseline-20261105. The previous progress document is backed up in results/stage_02/run_001/progress_before.md. Restoring the legacy workflow requires no data migration because its paths and engines were not changed. Do not use git clean/reset to remove reports: it could destroy user-owned untracked presentations.
