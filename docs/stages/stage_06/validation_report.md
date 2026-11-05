# Stage 6 validation matrix and open scientific gate

| Category | Status | Actual evidence / limit |
|---|---|---|
| Isolated Windows installation | Verified | Python 3.10.11 + pinned MACE 0.3.14/Torch CPU stack installed; pip check passed; lock/install manifests saved |
| Original environment preservation | Verified within recorded checks | Original `.venv` still has no Torch/ASE; source/data preservation hashes recorded separately |
| Checkpoint identity | Verified | Official frozen HF revision; published LFS SHA/size matched; actual loader rechecks hash; missing/tampered/outside-path guards tested |
| Element support | Verified as representation coverage | 89 checkpoint elements; all 79 fusion elements included; not per-element accuracy proof |
| Request/shape/unit safeguards | Verified within executed tests | 510 regular tests, including 32 new; 24 isolated-energy tests, including actual inference and guards |
| Energy/force numerical consistency | Verified on executed inputs | Repeat, permutation/translation/rotation, supercell scaling and finite-difference checks |
| Relaxation | Verified on selected demonstrations | 3/3 below declared force threshold; separate one-step HTTP case correctly nonconverged |
| CIF output | Verified | Actual nonconverged HTTP output checksum and import round-trip checked; evaluation writes final geometry CIFs |
| Selected UI integration | Verified | Browser selected/generated 40-atom Ti→Zr and displayed actual 17-step convergence/result path |
| Local reproducibility | Verified within recorded scope | Same frozen input/model, deterministic checks, exact parameters and raw trajectories retained |
| Independent DFT energy/force accuracy | Not verified | Zero admitted compatible external numerical references; MAE/RMSE withheld |
| Formation energy / convex hull | Not assessed | Missing compatible elemental/competing-phase reference set |
| Chemical suitability / synthesis | Not verified | Convergence and element coverage are insufficient |
| Band gap / dilute-doping activation | Not assessed | Later modules; neutral potential is not a charged-defect model |
| GPU / Mac / clean-machine deployment | Not verified | CPU on current Windows laptop only |

Authoritative tests: logs/stage_06/run_002/regular_004.xml and real_003.xml. Authoritative model evaluation: results/stage_06/run_002/evaluation.json. edge_case_report.md enumerates executed Stage 6 tests. Live HTTP/browser records supplement, rather than replace, those tests.

Earlier acquisition failures and the partial-formal-charge integration failure remain archived. First evaluation run_001 allowed ASE cached static results; its timing is superseded by run_002, which resets the calculator before each public static prediction. Neither failed attempts nor cached timings are erased or used to claim speedup.

Full-object loading warnings originate in the pinned trusted MACE/e3nn stack; the model's identity is frozen and no arbitrary checkpoint input is exposed. Pymatgen warns in the deliberate charged-cell rejection test. Existing spglib deprecation warnings remain documented. No package upgrade or suppression was used to hide these warnings.

Browser screenshot persistence returned EPERM; no saved screenshot is claimed. Scientific PNG/SVG figures are saved and visually inspected. This milestone does not satisfy the full Stage 6 scientific gate until compatible independent references and thermodynamic assessment are addressed or the owner explicitly approves a documented scope exception.
