# Architecture, algorithms and file responsibilities

This stage changes three signal engines and adds one shared validation helper. It does not
fuse signals, generate structures or predict materials properties. Valid output records retain:
method, target_element, rank, candidate_element, similarity_score (six decimal display).

## Shared validation: src/similarity_validation.py

Inputs: symbols, integer parameters, Parquet tables and numerical arrays. Outputs: checked
values, a DataFrame, support-status dictionaries or explicit exceptions. Dependencies: numpy,
pandas, pymatgen. validate_symbol accepts canonical symbols only; 'ga', formulas and whitespace
are rejected. validate_integer rejects booleans, negative k and nonintegers, accepts numpy
integer scalars. UnsupportedElementError is a ValueError subclass for a recognized element
without a representation. read_master rejects empty/duplicate/ill-identified records and
incorrect noble-gas group flags. It does not certify source measurements or physical units.

All 118 canonical elements are recognized. Each engine exposes get_support_status(element):
recognized, target_supported, candidate_eligible, reason, scientific_substitution_validated=False.
Default paths resolve from the project source location, so changing working directory does
not redirect default data/cache lookups. Explicit custom relative paths remain caller-relative.
Invalid target requests are checked even when k=0; supported targets with k=0 return [].
Large k returns the available candidates without duplicates or the target itself.

## PN engine: src/pn_similarity/pn_engine.py

Input: symbol/group/PN table and target. Output: PN similarities/rankings. Initialization now
requires unique integer PN values in 1..118, matching the recorded scale, not the old 1..103
header. Core equation is unchanged: S=1/(1+|PN_a-PN_b|). For PN values 40 and 42,
distance=2 and score=1/3. An adjacent element scores 1/2. This is a dimensionless ordinal
proximity signal, not a probability of successful substitution. Raw integer distances are used;
the separately recorded PN/118 feature is not substituted into this formula.

94 query elements are available. The default pool excludes noble gases (88 candidates),
while PN descriptive queries on represented noble gases remain available. This asymmetric
query/candidate policy preserves the original engine and is explicit in support metadata.
It is a project screening policy, not a universal assertion that noble gases cannot react.

## Property engine: src/property_similarity/property_engine.py

Input: original 14-feature table; output: cosine-based rankings over 88 non-noble feature rows.
Each candidate feature must be real and finite; physical magnitudes must be positive, while
subshell counts may be zero and must obey integer occupancy bounds. Missing values are
rejected; no new imputation is introduced. Initialization, not a later query, rejects corruption.

For feature x, z=(x-mu)/sigma with population standard deviation (ddof=0). Example:
[10,20,30] has mean 20, sigma about 8.165, and z(30) about 1.225. This stops large numerical
units from dominating solely because of scale. A constant feature contributes zero; its
division scale is set to 1. Every standardized element vector is then divided by its L2 norm.
Cosine = dot(a,b)/(norm(a)*norm(b)); [1,0] and [1,1] give 1/sqrt(2), about 0.7071.
Opposite directions give -1. A negative score is not a proven chemically incompatible pair.
An all-zero standardized row has no direction, so cosine is undefined and the table is rejected.
Overflow is caught; floating roundoff is bounded to [-1,1] before returning cosine scores.

The old table remains the default for behaviour compatibility. Stage 2 native data was not
silently activated: native field names/missingness need a separately reviewed integration.
Plausible-but-wrong positive values, historical imputation and source-condition/unit problems
cannot be certified by these numeric guards. Correlated features can still double-count trends;
feature weighting/ablation belongs to the next approved evaluation work.

## Atom2Vec: src/atom2vec/atom2vec_engine.py

Inputs: compressed composition corpus or cache, dimension and seed. Output: unit embeddings,
cosine rankings, cache_info and (when trained) training_stats. A composition such as Ga2O3
produces Ga environment '(2)O3' and O environment '(3)Ga2'. Repeated environments build
a sparse atom-environment count matrix. Each row is L2-normalized; sparse SVD decomposes
X approximately as U*Sigma*V-transpose. The retained representation U*Sigma has 20 default
dimensions and is normalized again for cosine similarity. This learns co-occurrence patterns;
it does not calculate band gap, defect formation energy or dopant activation.

Only binary-to-quaternary integer compositions are retained; common elements have at least
1% of maximum frequency. Corpus rows, including repeated compositions, keep their old
weighting for comparability. Input/skipped counts are recorded. Empty/malformed/too-small
corpora fail before SVD or cache publication. One byte snapshot supplies both parsed data
and its SHA-256 hash, preventing a mismatch between trained input and recorded checksum.
Dimension must be positive and smaller than both matrix dimensions for sparse SVD; the seed
must be a nonboolean integer from 0 through 2**32-1.

Cache loading disables pickle, validates unique canonical symbols, vector shape/dimension,
finite real values, unit row norms (absolute tolerance 1e-8), and descending nonnegative
dimension-matched singular values. A corrupt cache is rejected, never silently retrained over.
New cache metadata validates algorithm, dimension, seed and corpus hash (if corpus available).
If corpus is absent, cache_info explicitly says its checksum was not independently checked.
The original metadata-free cache remains usable in compatibility mode, with provenance
unverified in cache_info; require_cache_metadata=True rejects it. Non-default seed requests
against metadata-free caches are rejected. Default compatibility does not prove the old seed.

Cache publication first completes a temporary archive in the destination directory. Windows
rename refuses an existing destination; POSIX uses an exclusive hard link. Only the temporary
file created by this operation is cleaned up. A competing destination is preserved. The Windows
path was tested; the POSIX branch and Mac execution have not been verified here.

## Experiments and tests

capture_baseline.py preserves original engines, rankings, pair matrices, environment and hashes.
verify_engines.py compares all pairs/rankings, checks 118-element support, measures warm
latency and trains/reloads one new full-corpus cache. build_reports.py reads actual JUnit and
experiment outputs, maps the 15 historical failures, verifies preservation and creates reports.
tests/stage_03/test_engine_hardening.py contains 148 new executed cases, including optimized
Python validation and simulated solver/permission/concurrent-writer failures. Synthetic
fixtures test arithmetic and error handling; they are not experimentally validated materials.

Run tests from C:Final Project, choosing a NEW base directory (pytest clears its selected base):

    .venvScriptspython.exe -m pytest tests --basetemp="C:Final Projectworkstage_03pytest_NEW" -q

Use get_support_status('Og') to inspect support, get_top_k('Ga', 10) for a ranking, and
compute_similarity('Ga','Al') for a pair score. See the method's cache_info before treating
a cache as reproducibly trained. The archived fresh strict cache is
results/stage_03/run_001/fresh_atom2vec_d20.npz; pass that explicit path with
require_cache_metadata=True to load it. The production default cache was not replaced.
