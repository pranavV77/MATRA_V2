# Stage 5 validation status

| Category | Status | Evidence and limit |
|---|---|---|
| Functionality | Verified within executed scope | Final 478 passing tests; 92 new; real HTTP, CLI and selected live browser flows |
| Geometric agreement | Verified on analytical/source examples | SrTiO3 #221, GaN/ZnS #186; nearest-shell expectations and periodic-image test |
| Construction invariants | Verified on recorded evaluation | 27/27 trial constructions across nine requests; not chemical reference labels |
| Reproducibility | Verified locally within recorded scope | Deterministic equality tests; frozen source hash; saved requests, trial geometries, raw timings and Git baseline |
| Cross-platform / clean install | Not verified | Only current Windows environment executed |
| Chemical substitution validity / site preference | Not verified | No relaxation, site-energy comparison, phase diagram, compatibility or independent success labels |
| Band-gap preservation | Not verified | No gap model/calculation invoked |
| Dilute-doping activation | Not verified | Concentration arithmetic does not establish defect physics |
| Independent statistical generalization | Not verified | No new held-out chemical cases |

Authoritative run: `results/stage_05/run_002/evaluation.json` and `logs/stage_05/run_002/pytest_005.xml`. `edge_case_report.md` enumerates actual executed tests. Scientific references, units, source distinctions and assumptions are explained in the completion report and technical guide.

Initial failures remain archived: enormous automatically generated pytest parameter IDs exceeded Windows' environment-variable length limit; explicit short IDs corrected that test setup. URL-shaped paths initially produced a missing-local-file error; URLs now reject explicitly. The first geometric evaluation discovered nonunique labels inherited from the source CIF symmetry expansion. Trial labels are now unique, source labels remain in host analysis, and a UserWarning-as-error export test verifies the fix. No original CIF or previous results were overwritten.

The final 52 nonfatal warnings are from the installed spglib deprecation/error-handling API, documented rather than hidden or fixed by an unsolicited upgrade. They do not themselves validate or invalidate chemistry. Browser screenshot saving returned EPERM; browser observation/export flows succeeded, but no persisted browser screenshot is claimed.
