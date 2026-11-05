# Stage 6 energy/relaxation milestone — completion review

## 1. Objective

Run a traceable pretrained materials potential locally on Stage 5 trial geometries, report energies/forces, and perform bounded fixed-cell positional relaxation. Owner approved the concrete isolated-environment/dependency/model-download plan with “Yeah, start doing.” The working scope is implemented. **Independent energy accuracy and thermodynamic stability remain open scientific gates; the full scientific Stage 6 is not declared complete.** No Stage 7 work started.

## 2. What we implemented

An isolated CPU energy environment, one frozen official MACE-MP-0b2-small checkpoint, strict model/input/output validation, energy and force inference, optional FIRE relaxation, explicit convergence reporting, JSON/CIF archives, a subprocess interface to the existing demo and an energy section in Structure lab. No training from scratch, remote inference, CUDA install, driver change or existing-environment upgrade.

## 3. Files created

All paths below are relative to `C:\Final Project`.

| Path | Responsibility |
|---|---|
| `.venv_energy/` | Isolated runtime; large local artifact excluded from Git |
| `models/stage_06/` | Actual checkpoint, verified source/checksum manifest and inspected 89-element capabilities; weight file excluded from Git |
| `configs/stage_06/environment_lock.txt` | Captured exact installed packages |
| `configs/stage_06/assessment_policy.json` | Recorded implemented CPU/precision/relaxation policy |
| `src/energy/contracts.py` | Input bounds, explicit neutral interpretation, metrics and comparison restrictions |
| `src/energy/backend.py` | MACE inference, output validation and fixed-cell relaxation |
| `src/energy/worker.py` | Isolated command process and unique relaxed-CIF export |
| `src/energy/bridge.py` | Serial job control, timeouts, project-local process environment and archives |
| `src/energy/service.py` | Stage 5/energy integration, provenance and actual element preflight |
| `src/review_demo/static/energy.js` | Live candidate energy/force/relaxation controls and explanations |
| `experiments/stage_06/` | Setup, official acquisition, evaluation and saved-result plotting scripts |
| `tests/stage_06/` | 32 regular-environment tests |
| `tests/energy_integration/` | 24 isolated-energy tests, including actual checkpoint inference and rejection guards |
| `data/benchmark/energy_v0_1_0/reference_registry.json` | Honest external-reference admission hold: zero admitted cases |
| `results/stage_06/run_002/` | Authoritative corrected predictions, trajectories, CIFs, coverage and live HTTP records |
| `logs/stage_06/` | Preserved acquisition/install/evaluation/test logs, including initial failures |
| `results/energy_assessments/` | Unique request/response/provenance, log and optional CIF bundles from live use |
| `docs/stages/stage_06/` | Plan, completion report, walkthrough, validation, executed tests and Telugu script |

## 4. Files modified

`src/review_demo/server.py`: adds `/api/energy/status`, `/api/energy/assess` and whitelisted JS. `static/index.html`: loads energy controls. `static/structures.js`: dispatches generated trial information to the new section. `.gitignore`: excludes isolated runtime, large weights/cache and generated runtime archives. `.gitattributes`: keeps source/result hashes reproducible. `docs/progress.md`: records approval, actual results and the open scientific gate. Existing similarity methods, ranking equations, source CIFs and previous results are preserved.

## 5. Algorithms, model and conventions

Runtime verified locally: Python 3.10.11, mace-torch 0.3.14, Torch 2.6.0+cpu, ASE 3.29.0, numpy 2.2.6, pymatgen 2025.10.7. Full transitive versions are captured in the lock file and installation reports. MACE predicts energy from atomic geometry; forces follow the energy gradient. This is a pretrained potential integrated by MATRA, not a newly trained MATRA energy model.

Checkpoint: **MACE-MP-0b2-small**, 67,622,684 bytes; SHA-256 `d5773bf9440e96d6eb8c598f84bd0e6369fcfa432f626a87f890e07da3c651c9`. The original 0a small GitHub download repeatedly reset connections; the official Hugging Face repository supplied 0b2 small at revision `e291ace2bfae073c3ebc7ae2f9479a525989baa7`. This version selection is disclosed, not represented as identical to 0a or inherently more accurate. Source and size/hash were frozen before loading.

Actual checkpoint coverage: 89 elements; all 79 current fusion elements are included. Recognition of 118 symbols remains distinct from supported/validated chemistry. Input maximum: 40 atoms. Device CPU, float64, two Torch threads. Public static predictions reset ASE's calculator cache before inference. ASE still reuses consistent energy/force values within a single geometry evaluation/optimizer step where appropriate.

Relaxation: FIRE, fixed lattice, max step displacement 0.1 Å, up to 100 steps, declared force threshold 0.05 eV/Å. Both successful convergence and exhausted budgets are explicit. The API permits force thresholds 0.01–0.2 eV/Å and step budgets 1–100. Stress and cell relaxation are not requested.

Stage 5's partial formal-state bookkeeping is preserved separately. The energy worker receives explicitly neutral atomic identities and positions. This does not compute charged defects, oxidation-state energetics or carrier activation. Explicit charged structures passed directly to the backend are rejected.

Primary sources: [MACE foundation documentation](https://mace-docs.readthedocs.io/en/latest/guide/foundation_models.html), [pinned MACE 0.3.14 model interface](https://github.com/ACEsuit/mace/blob/v0.3.14/mace/calculators/foundations_models.py), [official model repository](https://huggingface.co/mace-foundations/mace-mp-0), [MACE foundation paper](https://arxiv.org/abs/2401.00096), [Materials Project phase-diagram methodology](https://docs.materialsproject.org/methodology/materials-methodology/thermodynamic-stability/phase-diagrams-pds). Published model benchmark accuracy is not adopted as local MATRA accuracy.

## 6. Actual outputs and results

Authoritative record: `results/stage_06/run_002/evaluation.json`. Three selected Stage 5 demonstrations, not independent chemical reference positives:

| Trial | Atoms | Target-site replacement | Steps | Initial max force (eV/Å) | Final max force (eV/Å) | Same-composition energy change (eV/cell) |
|---|---:|---:|---:|---:|---:|---:|
| Ideal SrTiO3, Ti→Zr | 40 | 12.5% | 17 | 3.65375 | 0.03268 | −0.85658 |
| Ideal GaN, Ga→Al | 4 | 50% | 7 | 1.09451 | 0.04640 | −0.04263 |
| AFLOW ZnS, Zn→Cd | 4 | 50% | 22 | 1.82024 | 0.04387 | −0.24036 |

**3/3 converged under this model and fixed-cell policy.** This is a small selected demonstration count, not success probability or synthesis accuracy. The last two are high-fraction substitutions, not dilute-doping benchmarks.

Fresh five-atom static prediction: median **61.38 ms**, p95 **66.17 ms**, ten calls after two warmups with calculator reset per prediction. Includes outer prediction/geometry handling; excludes model startup, HTTP, disk export and relaxation. Other local work ran during evaluation, so these are descriptive laptop timings, not controlled throughput benchmarks. Peak isolated-process working set measured before final plotting: **728,371,200 bytes (~695 MiB)**. This excludes the browser, original server and rest of the machine.

Live 40-atom HTTP prediction+relaxation: **16.66 seconds**, including subprocess/model startup and host/trial inference, and 17 relaxation steps. A separate live GaN→Al request capped at one step correctly returned **not converged**; its saved CIF checksum and import round-trip were verified. Browser displayed the actual Ti→Zr result and saved-record location.

Finite-difference force comparison: model −0.1230599436 versus numerical derivative −0.1230600212 eV/Å, absolute difference **7.76×10⁻⁸ eV/Å**, below the predeclared 10⁻³ tolerance. The derivative uses this same model's energies: it is **not a DFT force error**. Translation/permutation/rotation/supercell energy-consistency checks passed the declared 10⁻⁷ eV/atom tolerance; raw differences are saved.

Plots `relaxation_for_review.png` and `.svg` show within-case energy changes and forces versus step. Each energy curve has its own zero. Comparing their drops does not rank different compounds' stability. No parity plot, energy MAE, stability confusion matrix or chemical accuracy is fabricated.

## 7. Edge cases tested

`edge_case_report.md` lists executed cases. Coverage includes incorrect types/booleans, nonfinite values, force shape/dtype failures, unsupported elements, oversized/charged structures, wrong target/site, mode preservation, checkpoint missing/tampered/outside project, repeated predictions with actual recalculation, input mutation, model/composition comparison gates, unique records, busy worker, subprocess failure, timeout, nonconvergence and exact unit consistency. Tests include real potential calculations, synthetic arithmetic cases and deliberately malformed outputs; those roles are distinct.

## 8. Validation status

Final regular suite: **510 passed** (`logs/stage_06/run_002/regular_004.xml`), comprising 478 prior and 32 Stage 6 tests. Isolated energy suite: **24 passed** (`real_003.xml`). These are separate environments. Do not call 534 tests 534 chemical validations.

Functionality: verified within the bounded scope. Numerical energy/force consistency: verified on executed cases. Local reproducibility: pinned model/hash, environment versions, parameters, source snapshot and deterministic checks recorded. Native Windows installation: actually succeeded. GPU/Mac/clean-machine reproduction: not executed.

Scientific energy accuracy against independent DFT: **not verified**. Compatible external energy references admitted: **0**. Formation energy, convex hull/decomposition stability, dynamical stability, band-gap preservation and doping activation: **not assessed**. Training overlap with the demonstration geometries is not independently audited. Refer to `validation_report.md` for the explicit status matrix.

## 9. Problems found and resolved

GitHub acquisition resets were preserved; official publisher mirror and frozen LFS hash used. Current MACE release requires a newer Python, so the approved pinned 0.3.14 stack was actually tested in its own environment. Partial formal charges serialized by Stage 5 were distinguished from a requested electronic charge. Cached static timing was identified; run_001's ~0.49 ms timing is superseded by run_002's fresh inference timing. No earlier result was overwritten. Installed packages emit full-object checkpoint loading warnings; only the frozen official model and installed library constants are loaded, with no user-uploaded checkpoint interface.

Browser screenshot persistence returned EPERM. UI operation/results were observed and backend records saved; no persisted browser screenshot is claimed. The scientific plots are saved and visually inspected.

## 10. Scientific limitations

Potential predictions can be wrong out of domain even for supported elements. Relaxation finds a model-local configuration at fixed cell, not a phase diagram minimum. Raw total energies/per-atom energies cannot rank different-composition substitutions. Formation energies need compatible elemental references; hull energies need compatible competing phases. A lower energy after relaxing one fixed composition is not experimental validation or proof that it outperforms another candidate. No band gap or charged-defect physics is inferred from these energies.

## 11. What is still incomplete

Independent numerical reference curation, error/uncertainty assessment, phase-reference compatibility and decomposition-stability evaluation remain inside Stage 6's scientific backlog. More diverse chemistry/site/concentration cases, non-fixed-cell assessment and hardware scaling are unvalidated. Production interface work and later property/doping/evidence-aware ranking stages remain pending.

## 12. Telugu explanation and teaching

Full beginner-friendly narration: `telugu_narration.md`. Code/method walkthrough and demo steps: `technical_guide.md`. Actual Telugu audio synthesis is unavailable in this session; no playable audio was generated.

## 13. Review and next-stage readiness

The **bounded energy/relaxation engineering milestone** is ready for owner review. **Full scientific Stage 6 completion is held** by missing independently qualified energy/phase references. Recommended next work is reference curation within Stage 6. Do not automatically start Stage 7 or represent this as scientifically validated stability filtering. Moving on with this limitation requires explicit informed owner approval.
