# Implementation, reasoning and actual validation

Files created and their responsibilities:

- collect_doping_sources.py: retrieves three DOI metadata records and public paper URLs;
  stores raw responses, failures and starting hashes. No previous run is overwritten.
- collect_doping_alternative.py: attempts the discovered publisher full-text URL. The attempt
  returned HTTP 401; no PDF was saved. publisher_alternative_failure.json records that outcome.
- build_doping_review.py: reads the preserved v2.2 benchmark and source extraction, then creates
  a separate, unscored doping supplement. Its seven quantities have explicit kinds, units,
  relations, specimen relationships and source line anchors. Repeat execution refuses overwrite.
- src/data_audit/doping_review.py: validate_quantity checks units/ranges/bounds and finite values;
  validate_doping_review also checks hashes, traceable passages, specimen relationships and
  prohibition of unvalidated benchmark or activation claims. It does not predict dopant behavior.
- tests/stage_02/test_doping_review.py: 29 new executed tests using actual source passages and
  damaged records. Reported raw fit values and missing activation data are preserved.
- report_doping_review.py: reads actual JUnit/review files and writes reports, a quantity table,
  preservation checks and artifact hashes. No model training, prediction or DFT calculation.

## Scientific concepts

Number density is atoms or carriers per volume: N/V, with units cm^-3. Fluence is implanted
ions per area: N/A, with units cm^-2. Converting between these requires a depth profile; no
uniform-depth conversion was used for the radioactive implantation experiment.

Stable Mg already present in an epilayer, short-lived implanted 27Mg, and mobile holes are
different populations. Equal units do not make their quantities interchangeable. A bound
such as probe density <3e14 is not an exact measurement of 3e14. A reported range is not
silently replaced by its midpoint. No radioactive-decay or implantation-profile simulation ran.

Electrical activation means incorporated dopants produce electrically active states/carriers.
Site occupation is evidence about location, not sufficient proof of carrier production.
An apparent ratio of holes to Mg would require matching specimens, populations, measurement
conditions and a justified compensation model. The current supplement supplies no such ratio.

The validator checks provenance and declared policy, not the truth of a scientific interpretation.
Numerical extraction and single-reviewer judgments still need independent scientific review.

## Executed tests and edge cases

The full suite passed 172 tests (143 previous + 29 new), zero failures/errors/skips.
Actual JUnit and runtime are in logs/stage_02/run_004/pytest.xml. New cases: identical rebuild,
saved-ledger equality, distinct densities/fluence, retained raw fitted fractions, wrong units,
NaN/infinity/boolean/negative quantities, reversed ranges, missing specimen basis, fraction
over 100%, invalid relation, wrong value count, invented activation/efficiency, normalized fit
overclaim, false held-out designation, undeserved benchmark credit, unknown-to-negative
labeling, bad checksum, escaped path, missing passage, invalid line range, specimen mix-up,
false PDF archive designation, missing quantity, duplicate lead and zero-fit boundary.

A second builder invocation actually raised FileExistsError. Source-request failures are
archived and are not passed off as retrieved papers. pip check reported no broken requirements.
No scientific performance test or cross-machine reproduction was run. Pytest runtime is not
prediction latency. Browser/network failures are observations, not chemistry failures.

## Verification categories

Functionality and local cached-data rebuild: verified for the executed scope.
Source interpretation: partially verified, independent adjudication pending.
Full dilute-doping benchmark, activation accuracy and property preservation: not verified.
All-element generalization, held-out evaluation and clean-machine reproduction: not verified.
Earlier engine audit failures remain assigned to Stage 3; passing tests do not erase them.

From C:Final Project, run a fresh test base directory:

    .venvScriptspython.exe -m pytest tests --basetemp="C:Final Projectworkstage_02doping_reviewpytest_NEW" -q

pytest clears the selected base directory; use a new name. Read-only review verification:

    .venvScriptspython.exe -c "from pathlib import Path;import json;from src.data_audit.doping_review import validate_doping_review;p=Path.cwd();print(validate_doping_review(json.loads((p/'data/benchmark/doping_review_v1_0_0/doping_evidence.json').read_text(encoding='utf-8')),p))"

No production module was changed. The new supplement is not automatically activated in an
engine. To roll back, use the earlier benchmark; no deletion or migration is needed.
