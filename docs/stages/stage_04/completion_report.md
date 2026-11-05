# Stage 4 review milestone

## Objective and scope
Combine the three existing similarity engines, compare methods fairly, and provide a partial local demonstration for the November 7 noon freeze / November 9 review. This brings forward only a small interface, not completion of Stage 10. March 2027 remains the full research review target.

## Implementation and files
`src/fusion/fusion_engine.py` combines independent signals and exposes every score contribution. Inputs: target, optional formula, k, weights and fusion method. Output: deterministic ranked candidates, method ranks, coverage and explicit validation status. `src/fusion/evaluation.py` implements retrieval and agreement metrics. `experiments/stage_04/evaluate_fusion.py` produces the immutable run. `src/review_demo/service.py` connects inference, source annotations and unique JSON/CSV exports. `server.py` serves the offline interface on loopback only; static HTML/CSS/JS provide the interface. Tests live under `tests/stage_04`.

No existing similarity implementation or dataset was replaced. Baseline Git tag: matra-review-prototype-baseline-86bec6a. See starting_checkpoint.json for protected file hashes.

## Methods explained
All comparisons use the same 79-element intersection; removing the query leaves 78 candidates. Missing features are not invented. 118 elements are recognized, but combined inference supports 79.

Weighted score = sum(w_i * s_i), where weights sum to one. PN is already in [0,1]; each cosine is mapped with (s+1)/2. Example: raw cosine 0.8 becomes 0.9; a one-third weight contributes 0.3. Equal weights are declared defaults, not learned optimal weights. This mapping aligns ranges, not distributions or reliability.

RRF = sum(w_i * 61/(60+rank_i)). It combines ordinal rankings rather than score magnitudes. The numerator only scales scores. Neither output is a probability. Reference: Cormack et al., SIGIR 2009, https://doi.org/10.1145/1571941.1572114. Information-retrieval performance does not establish materials validity.

Formula context checks membership only. Ga in GaN and Ga2O3 receives the same elemental ranking. Site, concentration, energy, band gap and dopant activation are not evaluated.

## Actual results

| Method | MRR | Hit@1 | Hit@3 |
|---|---:|---:|---:|
| PN | 1.000 | 2/2 | 2/2 |
| Atom2Vec | 0.750 | 1/2 | 2/2 |
| Property | 0.208 | 0/2 | 1/2 |
| weighted_score | 0.750 | 1/2 | 2/2 |
| rrf | 0.750 | 1/2 | 2/2 |

MRR averages 1/rank of the known candidate: ranks 2 and 1 give (0.5+1)/2=0.75. Higher is better. Hit@k counts cases with a known candidate in the first k. Known-recall is the fraction of documented positives retrieved, not recall of all chemically valid replacements. Unknown candidates are not false positives; accuracy, precision and confusion matrices are inappropriate here.

Fusion improves on Property-only, matches Atom2Vec MRR, and underperforms PN on these two cases. Ga→Al moves from PN/Atom2Vec rank 1 to fusion rank 2; Te→Se improves from Atom2Vec rank 2 to fusion rank 1. Dropping Property yields MRR 1.0 on these two cases, an exploratory observation that must not be used to tune and then claim independent success.

Jaccard = intersection/union of Top-10 sets; 1 means identical sets. Spearman measures full deterministic ordinal rank agreement. These measure agreement, not truth. Warm median fusion query time was 0.319 ms (200 calls after 20 warmups); HTTP/browser/startup costs are excluded. Individual timings use native pools and simpler output, so no speedup claim is justified.

## Reference and reproducibility
Versioned source: data/benchmark/v2_2_0/extended_evidence.json. Two eligible development references: one computational Ga–Al ordered model at x=0.5 and one experimental site-occupancy Bi2Te2Se case. Zero held-out cases, zero contextual doping benchmarks. See evaluation.json for source hash, exact scopes, parameters, per-case outputs, ablations, agreement and raw timing values. Original broad assertions remain withheld. These results do not prove synthesis feasibility or property preservation.

Run from C:\Final Project:
```
.\.venv\Scripts\python.exe -m src.review_demo.server --port 8765
```
Open http://127.0.0.1:8765. Stop with Ctrl+C. Alternatively run run_review_demo.cmd. To repeat evaluation, inspect evaluate_fusion.py and choose a new run directory; the existing output must not be overwritten.

## Executed testing and validation
386 tests passed in the full suite (320 previous + 66 new); logs/stage_04/run_001/pytest_003.txt and XML are the authoritative successful run. Earlier failed runs remain preserved. Socket access initially blocked HTTP; after network permission one Windows unread-request-body reset was reproduced and fixed with bounded body consumption. The final full suite passed.

Executed edge cases: invalid/noncanonical/unsupported targets; empty/invalid weights, all-zero, nonfinite, overflow-prone weights; invalid k/types, zero and excessive k; malformed and mismatched formulas; invalid model scores; duplicate ranking elements; deterministic ties; returned-object mutation; all 79 queries; request content-type, origin, oversized bodies and private paths; unique exports inside the project. See test source and JUnit for exact cases.

Browser verification: loaded live default Ga results, switched to Bi2Te3/Te and saw Se first, exported JSON/CSV into the project, opened actual evaluation and ablation tables. Full responsive/device coverage and every interactive control were not browser-tested. Screenshot persistence from the browser was blocked; no saved screenshot is claimed.

Functionality: verified by executed tests and selected browser flows. Reproducibility: deterministic ranking verified; run inputs and source recorded. Scientific validity: only scoped reference retrieval checked; general substitution effectiveness, site validity, energy, band-gap preservation and doping remain unverified.

## Readiness and pending work
This is a working partial review milestone with comparison graphs and transparent limitations. It is not defensibly 80% of the full research scope. Stages 5–9 and full interface/final integration remain pending. Expand independent, host/site/concentration-aware references before optimizing weights. Do not automatically begin the next stage.

Actual Telugu audio generation is unavailable in this environment. The accompanying Telugu transcript is a narration script, not a generated recording.
