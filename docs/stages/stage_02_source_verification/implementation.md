# Implementation and execution

- experiments/stage_02/collect_primary_sources.py downloads public paper/metadata snapshots
  once and records failed requests. Candidate identifiers are search leads, not verified facts.
  No API credentials, remote execution or challenge bypass is used.
- experiments/stage_02/build_primary_review.py reads those snapshots and constructs the new
  scoped evidence ledger. It finds source-line locators and hashes both extraction and paper.
  A second execution refuses to overwrite existing outputs.
- src/data_audit/primary_evidence.py validates identities, units/bases, passage anchors,
  checksums and admission conditions. It returns readiness counts, never model accuracy.
  It rejects incomplete contextual claims from scoring but cannot prove a scientific reading
  is correct; independent review remains necessary.
- tests/stage_02/test_primary_evidence.py exercises cached real passages and deliberately
  damaged records, including inaccessible sources and misleading challenge pages.
- experiments/stage_02/report_primary_review.py reads actual JUnit results, verifies earlier
  tracked-file hashes, and produces reports and a readiness-count figure. No predictions run.

Run from C:Final Project:

    .venv\Scripts\python.exe -m pytest tests --basetemp="C:Final Projectworkstage_02primary_reviewpytest_NEW" -q

Use a fresh basetemp name: pytest clears its chosen base directory. The archived executed
command and JUnit are in logs/stage_02/run_002. To verify the saved release without modifying it:

    .venv\Scripts\python.exe -c "from pathlib import Path; import json; from src.data_audit.primary_evidence import validate_primary_evidence; p=Path.cwd(); print(validate_primary_evidence(json.loads((p/'data/benchmark/v2_1_0/primary_evidence_reviewed.json').read_text(encoding='utf-8')),p))"

Production similarity engines, feature releases and earlier benchmark records are unchanged.
The new native data is still not automatically activated in legacy engines. Rollback consists
of excluding this additive evidence release; no legacy migration is required.
