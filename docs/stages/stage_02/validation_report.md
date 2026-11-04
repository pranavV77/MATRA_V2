# Stage 2 validation status

| Category | Status | Evidence / limitation |
|---|---|---|
| Data-release functionality | Verified | 47 new tests passed |
| Legacy regression | Verified | 26 existing tests passed |
| Source-value preservation | Verified | Every native cell compared with captured source snapshot |
| Units/source conventions | Verified against pinned library metadata | Source metadata and explicit names stored; individual measurements not independently certified |
| Radius-estimate reproducibility | Verified | 89 training pairs, coefficients, LOO diagnostics; not mixed with native values |
| Missingness honesty | Verified | Nine gaps preserved; no unsupported Fr conductivity |
| Full element recognition | Verified | 118 registry rows; only 94 native-feature rows, no invented extra vectors |
| Claim admission safeguards | Verified | Unknowns cannot earn credit; source/condition checks enforced |
| Benchmark chemical validity | **Not yet verified** | 0 strict contextual claims admitted; primary passage/site/concentration curation remains |
| Reproducibility | Verified locally | Frozen inputs regenerate emitted native table, provenance, estimates, registry and ledger |
| Dependencies | Consistency check passed | pip check reports no broken requirements; clean machine not tested |
| Original file preservation | Final hash check recorded separately | Original tracked files must match Stage 2 starting hashes |
| Production engine robustness | Unchanged / not fixed here | Stage 1 defects remain queued for Stage 3 |
| Band-gap, stability and doping effectiveness | Not assessed | Later modules; DOI metadata is not scientific evidence for effectiveness |

Engineering deliverables are complete within scope. The scientific benchmark remains withheld. Do not characterize this stage as a fully verified substitution benchmark or use the new release to claim improved accuracy.
