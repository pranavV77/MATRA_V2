# MATRA — materials substitution research prototype

MATRA combines periodic-number, Atom2Vec and property similarity, constructs site-specific trial crystal structures, and optionally runs a pinned pretrained MACE energy/force potential with fixed-cell relaxation.

**Current status:** Stage 6 energy/relaxation engineering is implemented. The owner has **not reviewed Stage 6**. Independent DFT accuracy and thermodynamic-stability validation remain open; this is not a finished or experimentally validated recommendation product. No Stage 7 work has started.

## Run the existing local demo

Workspace: `C:\Final Project`. Run `run_review_demo.cmd` and keep the terminal open, then visit http://127.0.0.1:8765. Workbench shows similarity; Evaluation shows the two scoped development-reference comparisons; Structure lab provides atomic-site selection, trial generation and optional energy assessment.

For a demonstration: choose ideal SrTiO3, repeat 2/2/2, analyze 40 atoms, select Ti site 8, generate candidates, select Zr in the energy section and optionally enable relaxation. A converged model calculation is not proof of stability or synthesis.

## What is included

- `src/`, `tests/`, `experiments/`: implementation, executed regression cases and reproducible experiment scripts.
- `data/`, `configs/`, `models/stage_06/*.json`: versioned data/provenance, captured dependency versions, policies and model identity.
- `docs/progress.md`, `docs/evaluation/`, `docs/stages/`: current progress, evaluation protocol, stage reports, explanations and Telugu narration scripts.
- `results/stage_*/`, `logs/stage_*/`: recorded outputs, figures and actual execution evidence, including preserved failures.
- Presentation files and their helper scripts: retained owner artifacts; historical slide claims have not been audited or updated for Stage 6. Current stage reports supersede historical benchmark descriptions.

Virtual environments, downloaded model binaries, package caches and disposable pytest directories are not uploaded. Model source/revision/SHA-256 and restoration scripts are included. Runtime demo exports remain available in the local workspace.

## Restoring on another Windows machine

The verified runtime is Python **3.10.11** on the current Windows laptop. Clean-machine reproduction has not been executed. On a fresh machine, use the intended `C:\Final Project` workspace; do not clone or install over an existing working project.

From the repository directory, keep bootstrap temporary/cache files local:

```powershell
New-Item -ItemType Directory -Force work\bootstrap | Out-Null
$env:TEMP = (Resolve-Path work\bootstrap).Path
$env:TMP = $env:TEMP
$env:PIP_CACHE_DIR = Join-Path $env:TEMP 'pip-cache'
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r configs\base_environment_lock.txt
```

If energy inference is needed and `.venv_energy` does not already exist:

```powershell
.\.venv\Scripts\python.exe experiments\stage_06\setup_environment.py
.\.venv\Scripts\python.exe experiments\stage_06\download_model.py
```

The setup uses the captured energy lock when present, writes unique installation logs/reports and refuses to replace an existing environment. The downloader restores missing weights against the committed manifest, preserves that manifest, and verifies the official published SHA-256. An existing verified model is reused; a corrupt/different file is preserved and rejected. Never run an arbitrary user-supplied checkpoint.

## Validation and limitations

At the end-of-day backup, the regular suite passed **514 tests** (including four new mocked restore-path tests). The separate isolated-energy suite previously passed **24 tests**, including real potential calculations and rejection guards; energy scientific behavior was not changed by the backup fixes. Latest backup check: `logs/handoff/2026-11-05/regular.xml`.

The Stage 6 frozen evaluation has three selected trial relaxations meeting the declared force threshold. These are numerical demonstrations, not independent positive chemical labels. The energy reference ledger currently admits **zero independent numerical reference cases**. Formation energy, convex hull, band gap and dopant activation remain unassessed. Different-composition raw energies cannot rank substitution suitability.

For the complete explanation and demo steps, read `docs/stages/stage_06/technical_guide.md`. For results and open gates, read its completion/validation reports. The model is MACE-MP-0b2-small from the official publisher; its exact revision/hash are in `models/stage_06/checkpoint.json`. Telugu scripts are supplied; no playable Telugu audio has been generated.

The next work is owner review and qualified reference validation within Stage 6, subject to the owner's stage-wise approval. Work is stopped for the day; this push is a backup, not stage approval.
