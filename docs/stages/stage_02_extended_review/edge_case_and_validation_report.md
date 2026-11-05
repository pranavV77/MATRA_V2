# Executed checks and validation status

Actual full suite: 143 passed, 0 failures, 0 errors,
0 skipped in 4.417 seconds. This includes 38 new tests and 105 prior tests.
No claim is made that unit tests establish chemistry correctness.

New executed cases include deterministic rebuild/saved equality; retained minor site disorder;
distinct dopant/carrier quantities; parent hash damage; deleted/altered inherited claims;
false held-out designation; missing/incorrect host grouping; missing/duplicated legacy records;
false negative legacy label; wrong cross-reference; scoring an unscored observation;
property-preservation overclaim; absent passage; missing observations; invalid observation kind;
wrong density unit; infinite density; missing mobility assumption; reversed detection bound;
invented activation-efficiency estimate; altered derived composition; altered occupancy values
even with a recomputed total; missing source-table row; wrong Wyckoff multiplicity; empty or
duplicate site tables; boolean/zero multiplicity; negative/infinite/boolean occupancies;
overfull/underfull sites; invalid element; fully ordered boundary with zero minor occupancy.

An actual second builder invocation refused overwrite with FileExistsError, as intended;
the log is repeat_build_refusal.txt. Two additional source requests returned non-PDF responses
and received no full-text credit. Their URLs, UTC times and failures are in acquisition_manifest.json.

| Validation category | Status | Limit |
|---|---|---|
| Software functionality | Verified for executed cases | Arbitrary malformed inputs/websites not exhaustively tested |
| Local reproducibility | Verified | Same cached files and environment; not clean-machine verification |
| Existing-work preservation | Verified | 160 previous tracked files checked; only .gitattributes and progress.md intentionally changed |
| Scientific interpretation | Partially verified | Traceable single-reviewer readings; expert adjudication pending |
| Experimental substitution evidence | One narrow development reference | No generalized substitution success claim |
| Dilute doping benchmark | Incomplete | Zero fully contextual eligible references |
| Property preservation / prediction accuracy | Not verified | No predictions, DFT or preservation experiments run |
| Independent generalization | Not verified | Zero held-out cases; related samples grouped by host family |

No performance benchmark was run: pytest runtime is not prediction latency or throughput.
No source covariance was available for uncertainty propagation. No concentration point was
invented from the Sn plot, and missing chemistry evidence was not relabeled as failure.
