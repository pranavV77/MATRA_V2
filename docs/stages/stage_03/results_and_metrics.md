# Actual Stage 3 evaluation

The goal is robust, reproducible independent similarity signals. These experiments do not
measure elemental-substitution accuracy. No chemical ground-truth labels were consumed by
the production engines and no withheld assertion was promoted to a validated benchmark.

| Engine | Supported queries | Candidate pool | Ordered pair scores checked | Max absolute score change | Changed Top-10s | Warm median ms |
|---|---:|---:|---:|---:|---:|---:|
| PN | 94 | 88 | 8836 | 0 | 0 | 0.0367 |
| Property | 88 | 88 | 7744 | 4.44e-16 | 0 | 0.0385 |
| Atom2Vec | 79 | 79 | 6241 | 6.66e-16 | 0 | 0.0390 |

All 261 supported engine-target Top-10 outputs are identical to the preserved baseline.
22,821 ordered pair evaluations include both directions and self pairs; they are not 22,821
independent materials examples. All 118 elements were queried against each support interface:
354 statuses and requests. Unsupported requests raise a specific UnsupportedElementError.
Full candidate lists contain no duplicate or self element and respect each method's policy.

## Metrics and their interpretation

- Regression-check pass count: 15/15 previously failing behaviours
  now have executed passing tests. This measures software correction, not chemistry correctness.
- Ranking regression count: number of supported queries whose complete Top-10 records changed;
  good result here is zero because the stage preserves valid existing behaviour. Limitation:
  matching an old ranking does not prove that ranking scientifically appropriate.
- Maximum absolute score difference: max |new score - original score| across each ordered
  pair matrix. Differences below 1e-12 are numerical precision here, not prediction error.
  The scatter's diagonal means score agreement, not agreement with experimental properties.
- Symmetry error: max |S(a,b)-S(b,a)|. Self error: max |S(a,a)-1|. Both were checked at
  tolerance 1e-12; these are mathematical invariants for these signals, not substitution tests.
- Coverage: number of elements with a representation and/or candidate eligibility. Higher
  coverage is not higher accuracy. Recognition of all 118 does not provide features for all.
- Query latency: wall-clock milliseconds for warm Ga Top-10 calls, 20 warmups then 200
  measured calls. Median is typical measured time, p95 the 95th percentile; neither is a
  confidence interval. One process/run and fixed target do not justify a general speedup claim.

Fresh Atom2Vec training used the entire unchanged 83,989-row composition snapshot with
dimension 20 and seed 42. 75,841
rows passed the existing composition filter; 8,148
were skipped (includes unary/higher-order or otherwise ineligible rows, not all corrupt data).
Training took 5.753 seconds in this run. Maximum pair-score
change from original cache was 6.66e-16;
all 79 fresh-model Top-10 outputs matched, and reload reproduced them. New cache metadata
records algorithm, dimension, seed and exact corpus-byte checksum. No GPU or cloud execution.

The parser issued a pymatgen warning about missing He electronegativity during composition
formatting. This was retained in the raw log. No He feature was fabricated, and the validated
embeddings are finite. Core corpus weighting/filter definitions were preserved.

Precision/recall, MRR, band-gap error, stability success and doping activation are not evaluated
here. The Stage 2 scientific benchmark remains incomplete, with zero held-out cases.
