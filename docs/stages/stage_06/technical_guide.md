# Stage 6 — understand the model, code and demonstration

## What problem we are solving

Stage 5 created a replacement at fixed positions. An unfamiliar replacement can push or pull its neighbors. Stage 6 asks the pretrained potential to predict the arrangement's energy and the forces on atoms, and optionally lets atoms move. It does not measure a band gap or prove that the material can be synthesized.

Think of a ball on a bumpy landscape. Energy describes height; force points downhill. Relaxation searches for a nearby valley. A nearby valley need not be the deepest valley, and a learned landscape need not match nature perfectly.

MACE was pretrained externally from materials calculations. We downloaded weights and run inference; we did not train a new force field or download the full MPTrj training corpus. Model coverage is 89 elements; our combined similarity pool remains 79. Overlap with the model's training data and generalization on these examples are not established.

## Units and calculations

Electronvolt (eV) is an energy unit used at atomic scale. Angstrom (Å) is 10⁻¹⁰ metre. Energy per atom divides the total cell energy by atom count. A 40-atom cell dropping by 0.85658 eV has a change of −0.85658/40 ≈ −0.02141 eV/atom. This describes the same composition before and after motion.

Force is the negative position derivative of energy: `F_x = -dE/dx`. We numerically check one component using `-[E(x+h)-E(x-h)]/(2h)` with h=0.0001 Å. Agreement shows the potential's energy/force calculations are consistent; both values come from the same model, so it does not establish DFT accuracy.

Maximum force is the largest atomic force-vector magnitude. Our default stopping condition is max force <=0.05 eV/Å, with at most 100 steps. “Converged” means this model's forces met that numerical condition. “Not converged” is a legitimate recorded outcome, not a result to hide or rename stable.

FIRE is an optimization method that adjusts atomic motion using forces. We cap each displacement step at 0.1 Å and keep the lattice fixed. The force can fluctuate during optimization; we record the trajectory rather than promising monotonic force decrease.

The neural potential uses atomic identities/positions, not our partial formal oxidation annotations as electronic charge-state inputs. Stage 5's original metadata remains in the archive; the energy input is explicitly a neutral atomic geometry. This is not a charged-defect calculation.

## What may be compared

The substituted trial before and after relaxation has the same atoms: its energy change is meaningful under the same model. The original host and Zr/V/Hf trials have different compositions: raw energy differences do not say which candidate is most stable. Dividing by atom count does not remove element-specific energy offsets.

Formation energy requires `E_total - sum(n_i*mu_i)` and a compatible set of elemental reference energies. Energy above the hull requires competing phases across the chemical system. We do not have an admitted compatible reference set yet. The system therefore returns null/unassessed instead of a fabricated stability value. Total energy is also a different quantity from the band gap; this model's energy cannot substitute for Stage 7's property assessment.

## Files, code responsibilities and verification

| File | What enters / important functions | What comes out / how to verify |
|---|---|---|
| `src/energy/contracts.py` | Request options; `relaxation_settings`, `neutral_geometry_from_stage5`, `comparable_energy_difference`, `regression_metrics` | Validated bounds, explicit neutral geometry, same-composition/model restriction and arithmetic metrics. Synthetic unit tests verify math; no synthetic numbers become research results. |
| `src/energy/backend.py` | Pymatgen structure; `EnergyBackend`, `predict`, `assess` | Hash-verified local model, finite energies/forces, force threshold status, trajectory and final geometry. Uses Torch/MACE/ASE only in `.venv_energy`. Actual model tests exercise invariances, force derivative, convergence, errors and cache reset. |
| `src/energy/worker.py` | Project-local request JSON and response path | One loaded model for up to four tasks, exclusive response JSON and unique last-geometry CIF files. Captures explicit failures. A nonconverged CIF is the last attempted geometry, not a confirmed minimum. |
| `src/energy/bridge.py` | Tasks from the original demo process; `run_worker` | An isolated child process, request/response/log directory, 300-second timeout and a one-job lock. Keeps Torch out of `.venv`; tests cover busy, failed, timed-out and unique runs. |
| `src/energy/service.py` | Host/CIF, repeats, target/site, candidate, mode and optional relaxation | Reconstructs the exact Stage 5 trial; preflights loaded element support; keeps source metadata and neutral model inputs separate; archives complete record. Mode is preserved, including explicit whole-orbit requests. |
| `src/review_demo/server.py` | Loopback GET status / POST energy assessment | Validated JSON API. Existing input limits/routes remain; actual HTTP assessments were executed. |
| `src/review_demo/static/energy.js` | Generated trials and user-selected candidate | Prediction table and convergence status. It makes no energy calculation in JavaScript. Changes to geometry invalidate old selection; late results identify their original selection. |
| `experiments/stage_06/setup_environment.py` | Existing Python 3.10 | Fresh isolated environment, local caches/install reports and captured package lock; refuses to replace an existing environment. |
| `experiments/stage_06/download_model.py` | Frozen official URL/revision/hash | A verified checkpoint and acquisition manifest; refuses overwrites and mismatched bytes. |
| `experiments/stage_06/evaluate_energy.py` | Frozen Stage 5 snapshot; `--run-name` | Predictions, consistency measurements, relaxation records, CIFs and timings. Refuses existing result JSON. |
| `experiments/stage_06/plot_saved_results.py` | Authoritative run_002 JSON | Presentation PNG/SVG from recorded data, without new inference. Refuses overwrite. |

## Local environment and reproducibility

The working application remains on `.venv`; heavyweight dependencies live in `.venv_energy`. Temporary files, package/model caches and results stay inside C:\Final Project. The CPU backend uses float64 and two Torch threads. No CUDA acceleration was installed or tested. `configs/stage_06/environment_lock.txt` captures exact versions; installation reports retain package URLs/hashes, including the CPU Torch index. `assessment_policy.json` records the implemented policy; editing that JSON alone does not hot-reconfigure the code.

MACE 0.3.14 loads its trusted checkpoint and library constants using PyTorch full-object loading and emits associated warnings. Only the frozen official model is supported. Do not add an arbitrary downloaded checkpoint or expose checkpoint upload as a UI feature.

Run the original launcher `C:\Final Project\run_review_demo.cmd`, or from that directory:

```powershell
.\.venv\Scripts\python.exe -m src.review_demo.server --port 8765
```

Open http://127.0.0.1:8765. The energy worker starts automatically for an assessment and closes afterward. Model import/startup means the first end-to-end request is much slower than a warm five-atom prediction.

To run numerical tests, use `.venv_energy\Scripts\python.exe -m pytest tests/energy_integration` with fresh project-local basetemp/JUnit paths and the cache environment defined by `src.energy.bridge.worker_environment`. For normal tests use `.venv\Scripts\python.exe -m pytest tests --ignore=tests/energy_integration`, again with fresh project-local basetemp/log paths. Do not reuse recorded pytest basetemp folders because pytest cleans them. Exact successful commands/paths are in the completion report's execution records.

The evaluation command runs under `.venv_energy` with the same process-local cache variables, using `experiments\stage_06\evaluate_energy.py --run-name run_003` for a genuinely new run. Preserve run_002. The source Stage 5 snapshot/hash and all parameters are embedded in each evaluation record. Reproducing the environment requires the captured CPU Torch source as well as the lock; do not blindly upgrade the working environment.

## Demo walkthrough

1. Open Structure lab and choose ideal cubic SrTiO3.
2. Set repeats to 2/2/2 and analyze. Confirm 40 atoms and select Ti site 8.
3. Keep one-site replacement and generate the three trial structures.
4. Scroll to “4. Assess one trial structure.” Choose Zr.
5. Enable positional relaxation and click “Predict energy and forces.” Allow time for the isolated worker; avoid starting multiple jobs.
6. Show the predicted host and unrelaxed-trial values. State that different compositions prevent raw-energy suitability ranking.
7. Show the relaxed trial's maximum force (~0.03268 eV/Å) and 17-step model convergence. The same-composition cell energy decreased by ~0.85658 eV in the recorded run.
8. Open the displayed project-local record folder. It retains input, response, log, provenance and an optional last-geometry CIF for new relaxation requests. Figures for the frozen evaluation are under results/stage_06/run_002.
9. Explain the boundary: “Our pipeline runs a pretrained potential and records numerical convergence. We still need independent energy references and competing phases before claiming stable substitutions.”

If a query reaches its step/time limit, show its recorded status. Never extend budgets silently to remove a difficult case from the report. The one-step GaN→Al HTTP example is deliberately nonconverged and validates that failure reporting works.

## Reading the results

Energy-trajectory curves use a separate starting zero for each composition; they show relaxation behavior, not a ranking of candidates. The force plot's dashed line is the declared 0.05 threshold. All three selected 100-step-budget trials finish below it. The sample is too small/selected for a general convergence guarantee.

Translation/permutation/rotation tests examine expected physical symmetries of the potential. Supercell extensivity checks that repeating a structure repeats total energy appropriately. Numerical agreement does not prove accurate chemistry.

The ~61 ms median and ~66 ms p95 are fresh five-atom CPU static calls with cache reset; the ~17-second live assessment also includes model loading, host/trial inference and 17 relaxation steps on 40 atoms. They measure different workloads. ~695 MiB measured peak applies to the isolated evaluation process, not the whole computer.

There is no independent energy MAE, hull distance, stability precision/recall or band-gap result yet. The next scientific task remains qualified reference acquisition and compatible thermodynamic assessment within Stage 6.
