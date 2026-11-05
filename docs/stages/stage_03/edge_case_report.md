# Executed robustness checks

Final suite: 320 passed, 0 failures/errors/skips in 8.564 seconds.
148 new cases plus 172 earlier tests. JUnit: logs/stage_03/run_001/pytest_final.xml.

| Historical diagnostic | Original observed result | New targeted regression |
|---|---|---|
| Atom2Vec:cache_dimension | failed | passed |
| Atom2Vec:invalid_k:-1 | failed | passed |
| Atom2Vec:invalid_k:True | failed | passed |
| Atom2Vec:nan_cache | failed | passed |
| Atom2Vec:zero_vectors | failed | passed |
| PN:duplicate | failed | passed |
| PN:duplicate_candidate | failed | passed |
| PN:invalid_k:-1 | failed | passed |
| PN:invalid_k:True | failed | passed |
| Property:duplicate | failed | passed |
| Property:duplicate_candidate | failed | passed |
| Property:infinite_feature | failed | passed |
| Property:invalid_k:-1 | failed | passed |
| Property:invalid_k:True | failed | passed |
| Property:negative_density | failed | passed |

The dimension regression now requires rejecting an incompatible cache, rather than silently
using 20 dimensions when 10 were requested. Original historical logs are unchanged; this
does not claim the old diagnostic runner itself was rewritten or all 78 old probes re-executed.

Other executed checks include invalid/nonhashable symbols, malformed types, negative/boolean/
noninteger k, numpy-integer k, zero k, huge k, explicit unsupported elements, missing/corrupt
tables, duplicate records, bad atomic identities/groups, PN range/type/uniqueness/missingness,
NaN/infinite/negative/zero-invalid features, numeric strings, booleans, complex features,
fractional/out-of-range electron counts, missing columns, overflow, zero standardized vectors,
constant-column handling, hand-calculated PN ties and cosine directions, NaN/infinite/zero/
nonunit/complex/cache vectors, shape/duplicate/invalid/object vocabularies, singular-value
shape/sign/order, metadata schema/type/seed/dimension/hash/JSON failures, strict legacy-cache
rejection, absent source corpus, changed corpus, empty/malformed/too-small corpora, skipped-row
accounting, repeated seeded training and cache reload, missing/corrupt cache, simulated solver
and write-permission failures, competing-writer preservation and temporary-file cleanup,
cwd-independent defaults, and explicit validation under python -O.

Initial hardening run: 115 passed, 2 failed, 1 skipped. Actual Windows hard-link publication
was denied; Windows publication was changed to no-overwrite rename and verified. A redundant
complex-Parquet parameter was removed; complex data is separately tested at the DataFrame
boundary. Follow-up hardening run passed 133 cases, then 15 mapped regressions were added.
The final entire suite passed 320 cases without skips. Initial logs remain available.

Limits: exhaustive malformed nested archives, every SciPy failure, power-loss durability,
arbitrary concurrent processes, POSIX/Mac behaviour, clean-machine setup and chemical validity
were not verified. Simulated errors test the specified paths, not every filesystem failure.
