# Stage 6 — feasibility review and proposed implementation

Status: preparation authorized by owner after Stage 5. No energy implementation, package installation, checkpoint download or energy inference performed. This document is the concrete proposal for the substantial-change approval gate.

## Progress and local findings

The bounded engineering workflow through Stage 5 is implemented: audited data, three independent similarity methods, fusion, local demo, host/site analysis and explicit trial structures. Latest executed full suite: 478 tests passed. Stage 5: nine host/supercell requests, 27 geometrically consistent constructions. Chemical validation remains limited: two Stage 4 development references, zero held-out chemical cases. These counts are not project completion or chemical accuracy percentages.

Planning estimate: approximately 40–45% of the intended full research scope implemented. This is judgment based on remaining work, not measured completion. Five of ten roadmap headings have engineering implementations, but unequal complexity and unfinished scientific validation prevent calling the project 50% complete by counting headings. Full property preservation, dilute doping, evidence-aware ranking and independent final evaluation remain ahead.

Windows workspace: C:\Final Project. Python 3.10.11. GPU query: RTX 3050 Laptop GPU, 4096 MiB, driver 552.27. About 156.5 GiB disk free at inspection. Twelve logical CPU threads reported. Torch, ASE, MACE, MatGL and CHGNet absent from the project environment. Pymatgen is available. Python launcher inventory failed through WindowsApps; another user-managed Python version has not been confirmed.

## Why this stage exists

Stage 5 changed an atom's identity while preserving all positions. Stage 6 must evaluate the model-predicted energy and forces of that starting configuration, then optionally move atoms toward a local minimum through relaxation. Forces are model-derived directions/strengths for atomic motion. Small residual forces indicate convergence under that model, not proof of experimental or thermodynamic stability.

## Model comparison

| Option | Verified public capability | Decision for proposal |
|---|---|---|
| MACE materials potential | Energies/forces through ASE; MACE-MP materials family documents 89-element parameterization; small checkpoint available | Proposed first baseline because it appears in the approved project architecture and offers a small-model path |
| MatGL / M3GNet | Materials potentials and property models; current distribution/model-loading infrastructure differs from older releases | Retain as later comparison candidate; do not install a second stack before the first backend is validated |
| CHGNet | Official interface supports structure energy, force, stress and relaxation | Technically relevant alternative; adopting it as the primary would be a methodology change to discuss, not silently substitute |

Sources: [MACE model documentation](https://mace-docs.readthedocs.io/en/latest/guide/foundation_models.html), [official MACE foundations](https://github.com/ACEsuit/mace-foundations), [MatGL](https://matgl.ai/), [CHGNet](https://github.com/CederGroupHub/chgnet).

Current MACE PyPI documentation requires Python >=3.11 and Torch >=2.5. In contrast, release metadata for 0.3.13 and 0.3.14 declares Python >=3.7 and Torch >=1.12. This makes a pinned 0.3.14 environment a candidate for the existing Python 3.10, **not a verified working installation**. Dependencies such as matscipy/e3nn and their Windows wheels still need resolution and runtime tests. Metadata snapshots are in results/stage_06/preparation_001/feasibility_audit.json. See [current requirements](https://pypi.org/project/mace-torch/) and [0.3.14 metadata](https://pypi.org/pypi/mace-torch/0.3.14/json).

## Proposed bounded implementation

1. Resolve a pinned CPU-only MACE/ASE/Torch stack in a new **project-local environment**, provisionally `.venv_energy`. Do not upgrade the working `.venv`. Store package cache, temporary files, model files and logs inside the project. Capture resolved versions and artifact hashes. If this release cannot work locally, report the actual failure before choosing another runtime/backend.
2. Download one explicitly identified official **MACE-MP-0 small** checkpoint, retain its exact URL, license, checksum and element list, and load it by local path. Do not rely on a mutable default model alias. Verify actual supported elements against every host/trial, not merely the advertised element count.
3. Build a bounded energy adapter with explicit units, model identity, input hash, CPU/device selection, finite-value checks, shape checks, runtime and error status. Return total energy in eV, energy per atom in eV/atom, forces in eV/angstrom, maximum force and declared stress units when used. No missing signal becomes zero.
4. Add deterministic checks for repeated inference, atom permutations, rigid translations/rotations and integer supercell extensivity, with numerical tolerances declared after inspecting numerical precision. These are model/software consistency checks, not DFT accuracy tests.
5. Test static inference on the three packaged hosts and a small frozen selection of Stage 5 trials, initially capped at 40 atoms. Measure real runtime and memory before expanding workload. No inference-time promise is established yet.
6. Add optional **fixed-cell positional relaxation** first, with provisional force threshold 0.05 eV/angstrom and maximum 100 steps. Record optimizer, full trajectory, initial/final energies, maximum forces, step count and convergence. A step-budget exhaustion is reported as nonconverged. Cell relaxation/stress checks are a separately declared option, not silently enabled.
7. Curate compatible numerical reference cases and record source, geometry, method, corrections and training overlap. Fixed-geometry and relaxed tasks stay separate. If no valid external references are accessible, regression accuracy stays unavailable; do not manufacture an MAE or call consistency tests accuracy.
8. Integrate a limited energy assessment into the existing local UI, preserving Stage 4/5 outputs. Report energy-model predictions and relaxation outcomes with their validation status. Do not sort Zr/V/Hf substitutions by raw total energy or call the lowest one the most stable.

## Inputs, outputs and proposed files

Inputs: archived Stage 5 JSON/CIF geometry, selected official checkpoint, explicit CPU/precision policy, frozen relaxation settings and independently qualified reference records when available.

Proposed additions: src/energy backend/validation/relaxation modules; configs/stage_06; environment lock/requirements files; a project-local model directory; tests/stage_06; experiments/stage_06; results/stage_06; logs/stage_06; docs/stages/stage_06; a small existing-demo extension. All remain under C:\Final Project. Exact files will be introduced incrementally after approval.

Outputs: predicted energies and forces, relaxation logs and converged/nonconverged status, unchanged original structures, relaxed output structures where generated, execution timings, unit-labelled figures, reference-comparison metrics only where valid, limitations and Telugu narration. Energy-model predictions never become experimental reference labels.

## Scientific comparison rules

Different elements have different energy reference offsets. Raw total energy or even raw energy per atom cannot rank different-composition substitutions as stable/unstable. Same-composition configurations can be compared under a common model and cell/relaxation policy. Relaxation energy decrease for one composition tests the optimization, not stability against decomposition.

Formation energy per atom is `(E_total - sum(n_i*mu_i))/N`, requiring compatible elemental reference energies. Energy above the convex hull requires compatible competing-phase energies spanning the relevant chemical system. Never mix raw neural-potential energies with database-corrected DFT energies without a justified, validated reference scheme. Source: [Materials Project phase-diagram methodology](https://docs.materialsproject.org/methodology/materials-methodology/thermodynamic-stability/phase-diagrams-pds).

If these references are unavailable, formation energy/hull fields remain null with a reason. Stage 6 must not be described as fully validated thermodynamic screening merely because the predictor runs. No charged-defect formation energies, donor/acceptor activation, band-gap prediction, phonon stability or finite-temperature synthesis claim is included.

## Evaluation and figures

| Evaluation | Planned evidence | Limit |
|---|---|---|
| Input/model coverage | Supported attempted structures / all attempted, with unsupported elements and failures | Element support is not reliable accuracy on every chemistry |
| Numerical consistency | Repeat, permutation/translation/rotation and supercell differences; finite outputs and correct units | Self-consistency is not external scientific validation |
| Relaxation | Converged / attempted, max force, steps, energy trajectory and geometry checks | Local model minimum can be physically wrong or metastable |
| Performance | Cold and warm timing, model load time and peak memory where measurable | Actual CPU measurements required; no GPU extrapolation |
| Reference error | MAE, RMSE and bias in eV/atom; force errors only with compatible references | Unavailable until references are admitted; training overlap reported |
| Relative order | Reference-supported same-composition pair ordering with near-ties excluded under a declared tolerance | No cross-composition raw-energy ranking |
| Thermodynamic screening | Formation/hull errors and classification only after valid references and a declared threshold | Deferred/unavailable without complete compatible phase data |

Figures: force/energy versus relaxation step; convergence/failure table; runtime versus atom count; initial/final geometry comparison; reference/prediction parity and residual plots only if scientifically eligible numerical references exist. No generic accuracy plot on unlabelled generated candidates.

## Dependencies, risks and hardware expectations

Expect downloads and extra disk consumption for Torch, ASE, the potential and its dependencies. Exact download/storage totals await a resolved package manifest. CPU inference on small cells is the first feasibility target; runtime and peak RAM are unmeasured. A 4 GB GPU may constrain larger structures, and its driver must match any future CUDA wheel. No driver/CUDA changes or GPU acceleration are part of the initial proposal. No training from scratch or remote computation is required by the proposed first pass.

Further risks: native Windows wheel availability, pickle/checkpoint compatibility, unsupported chemistry despite element coverage, out-of-domain forces, relaxation failure and reference-energy mismatch. Errors remain visible. The working demo remains on its current environment. An isolated worker may need a process boundary for UI integration; this will be documented and tested, not hidden.

## Approval requested

Approve this bounded Stage 6 implementation, including creation of `.venv_energy` **inside** the existing project, dependency resolution/installation and download of one official small MACE checkpoint. Existing no-install decision applied to previous stages; this is the first concrete request to change it for an energy backend. If an additional Python installation or backend change proves necessary, explain the actual incompatibility and obtain approval before that change. Stage 6 preparation is complete; Stage 6 scientific implementation and evaluation are not yet performed.
