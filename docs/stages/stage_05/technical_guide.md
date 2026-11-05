# Stage 5 — understanding and running the implementation

## What changed from Stage 4

Previously MATRA answered “which elements look similar to Ti?” Now it can also build “Zr at Ti index 8 in this explicit SrTiO3 supercell.” It still cannot conclude that this trial is stable or preserves a band gap.

```
Ordered CIF / declared prototype
  -> validate lattice, occupancy and periodic geometry
  -> expand requested supercell
  -> identify symmetry orbits and geometric neighbor shells
  -> select a target site in this expanded cell
  -> take the Stage 4 elemental shortlist
  -> replace one site / one orbit in separate copies
  -> record exact fractions, formal-state assumptions and geometry
  -> export unrelaxed CIF + reproducible JSON
```

## The concepts

A crystal combines a **lattice** (three repeat vectors) with a **basis** (the atoms inside the repeating cell). Fractional coordinates `(0.5,0.5,0.5)` mean halfway along each lattice vector; they are not distances in angstrom. Cartesian position is `fractional row vector × lattice matrix`.

Periodic neighbors include images across a cell boundary. A single atom in a cubic cell has six nearest periodic images, so counting only distinct input indices would be wrong. That case is actually tested.

A **symmetry orbit** groups positions connected by the host's rotations/translations. One atom substituted on any member of that orbit gives symmetry-related one-site configurations under the original host symmetry. This does not mean every two-atom arrangement on that orbit is equivalent.

`symprec=0.01 Å` is the positional tolerance used for symmetry matching, not a measured uncertainty. Ideal SrTiO3 was tested at 0.001, 0.01 and 0.05 Å; its recovered group stays #221. Distorted real materials may behave differently.

A **supercell** repeats the input cell. `[2,2,2]` multiplies volume and atom counts by eight. It also changes site indices. Analyze the expanded cell first and choose from that exact site table; the code never interprets an index silently as a primitive-cell index.

Replacement fractions are `m/N_target` and `m/N_all`, where `m` is the changed-site count. Eight Ti sites and 40 total atoms with one replacement mean 1/8=12.5% on the Ti sublattice and 1/40=2.5% overall. This is exact bookkeeping for the periodic model, not a solubility or defect-isolation conclusion.

A **formal oxidation state** is a bookkeeping convention. Charge delta is `sum(q_candidate - q_original)` over replaced sites. Zr4+ for Ti4+ gives 4−4=0. Nb5+ gives 5−4=+1. Without supplied candidate states the answer is “unknown”; the system does not guess the easiest state and declare compatibility.

## Code responsibilities and verification

| File | Inputs and important functions | Outputs, dependencies and verification |
|---|---|---|
| `src/structures/hosts.py` | `parse_cif(text)`, `load_cif(path)`, `geometry_check(structure)`, `analyze_sites(structure,...)`, `diagonal_supercell(structure,scaling)` | Pymatgen structures plus provenance; site/orbit table and geometry flags. Uses numpy, CIF parser and spglib through pymatgen. Test with Stage 5 geometry/import cases. |
| `src/structures/prototypes.py` | `prototype(name)` | Fresh explicitly parameterized ideal SrTiO3/GaN structures. Never claims measured lattice values. Analytical symmetry/shell expectations are tested. |
| `src/structures/candidates.py` | `CandidateGenerator.generate(host,target,index,...)`, `formal_charge_screen`, `export_configurations` | Fresh structures, changed indices, fractions, original elemental scores, charge assumptions, unique bundle paths. Uses Stage 4 FusionEngine; no benchmark labels. Verify that original host hash stays fixed, exact intended indices change, CIF round-trips and export labels remain unique. |
| `src/structures/service.py` | A JSON object with exactly one `host_id` or `cif_text` | `analyze`, `generate`, `export`; provenance follows every output. AFLOW bytes are checked against the frozen hash. Uses the above modules; no remote runtime lookup. |
| `src/structures/cli.py` | Command arguments | JSON analysis/results or export paths. Invalid arguments produce exit code 2. Runs the same service as HTTP. |
| `src/review_demo/server.py` | Existing loopback HTTP requests plus new structural routes | JSON responses and whitelisted static assets. Structure body cap 600 KB permits CIF text up to 500 KB; elemental cap stays 16 KB. Real HTTP tests execute these paths. |
| `src/review_demo/static/structures.js` | Host/CIF, repeats, expanded index, mode and candidate count | Live tables and project-local export requests. Host edits invalidate old generation state. It does not calculate material properties in JavaScript. |
| `experiments/stage_05/evaluate_structures.py` | Frozen three-host/three-cell setup, `--run-name` | New-run JSON, representative CIF bundles, timing and concentration/symmetry graph. Existing evaluation JSON is not overwritten. |
| `experiments/stage_05/plot_geometry.py` | The recorded run_002 JSON | Actual host/trial coordinate plot; refuses to overwrite its existing image. No new inference. |

## Run locally

Open a terminal in `C:\Final Project`:

```powershell
.\.venv\Scripts\python.exe -m src.review_demo.server --port 8765
```

Open http://127.0.0.1:8765 and select **Structure lab**. For a review: select ideal SrTiO3, set repeats to 2/2/2, analyze, retain Ti site 8, generate three candidates, and save. Show the original host's six-neighbor Ti shell and the two concentration bases. Candidate charge reads unknown because the UI has not supplied candidate oxidation states. “Unknown” is deliberate abstention.

CLI analysis and generation:

```powershell
.\.venv\Scripts\python.exe -m src.structures.cli --host perovskite --supercell 2 2 2
.\.venv\Scripts\python.exe -m src.structures.cli --host perovskite --supercell 2 2 2 --target Ti --site 8 --k 3 --export
.\.venv\Scripts\python.exe -m src.structures.cli --host aflow_zns
```

For an imported file, replace `--host ...` with `--cif data\my_host.cif`; that file must already be inside the project. Multiple phases, partial occupancies, absent target sites or unsupported representations produce explicit errors instead of fabricated outputs. Preserve any source citation alongside your imported CIF.

Run tests with a **fresh** basetemp and log path inside `C:\Final Project`. The final recorded command uses `pytest tests --basetemp=C:\Final Project\work\stage_05\pytest_005 --junitxml=C:\Final Project\logs\stage_05\run_002\pytest_005.xml -q`. Do not reuse that test directory because pytest cleans its basetemp. For an evaluation rerun, use a fresh run name (for example `--run-name run_003`) and a new log; do not overwrite run_002.

## Interpreting the metrics

Changed-site correctness compares actual before/after element identities with requested indices. Site-count, lattice and coordinate checks verify the construction contract. Fraction checks recompute denominators independently from the host. A good result is agreement, but these checks cannot establish chemical feasibility.

Symmetry reduction is `1 - N_target_orbits / N_target_sites`. It estimates redundant single-site choices avoided under this host symmetry. High reduction can lower repeated calculations, but does not estimate correct-replacement precision or wall-clock speedup.

Warm median is the middle measured query duration; p95 is the 95th percentile. Lower is faster for that exact workload. Ten samples on one laptop are not a deployment benchmark or an extrapolation to DFT.

There are no appropriate accuracy/precision/recall labels for these generated structures. The Stage 4 two-reference retrieval results remain unchanged. Stage 5 introduces no new chemical positives or negatives.
