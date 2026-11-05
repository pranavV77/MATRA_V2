# Stage 1 validation

| Category | Status | Executed evidence / boundary |
|---|---|---|
| Existing functionality | Verified within legacy suite | 26 original pytest cases passed; this suite is limited |
| Additional robustness | Failed requirements identified | 15 failed diagnostic records; production is not declared robust |
| Cached ranking reproducibility | Verified locally | All ranking and metric fields matched recorded results |
| Fresh master generation | Verified locally | Values equal and SHA256 equals original master table |
| Fresh Atom2Vec generation | Verified locally | Same 79 symbols; pairwise similarity max difference 0; all supported Top-10 lists equal |
| Metric arithmetic | Verified on legacy outputs | Independent Hit@K, MRR@10 and Recall@10 arithmetic matched all methods |
| Data integrity | Verified for observed baseline | 4/4 principal data artifacts match manifest; summary table also matches |
| Results checksum discrepancy | Explained, not repaired | Preexisting JSON diff changes timestamp only; saved patch preserves it |
| Scientific conventions | Partially verified; corrections needed | Polarizability labels and PN metadata inconsistent; imputation derivation incomplete |
| Benchmark scientific truth | Not certified | Definite BM-S04 DOI mismatch; BM-P01 evidence class needs review; other sources not fully checked |
| All-element input handling | Measured | PN 94/118, Atom2Vec 79/118, Property 88/118; acceptance is not applicability |
| Generalization / functional preservation | Not verified | No independent held-out benchmark, site validation, energy or band-gap implementation |
| Original file preservation | Verified at audit completion | 47 existing files unchanged; rechecked again in final verification |

This is an audit completion with findings, not a clean research-product validation pass. The next stage must resolve dataset/provenance issues; engine-hardening defects remain explicitly queued for the already planned similarity-engine stage. They are not silently waived.
