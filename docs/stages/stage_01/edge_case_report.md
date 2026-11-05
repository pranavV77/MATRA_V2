# Stage 1 edge-case report

Executed diagnostic records: 78; passed: 63; failed requirements: 15. These are probe outcomes, not a product accuracy measure. Existing pytest results are separately 26 passed. All 118 elements were also tested against all 3 engines (354 requests).

An exception counts as rejection in these diagnostics; it does not establish a friendly error message or a stable API contract. In particular KeyError/IndexError/AssertionError still require production-hardening review. Warnings from deliberately damaged fixtures are captured in the audit console.

| Executed probe | Status | Requirement | Observation |
|---|---|---|---|
| PN:invalid_target:0 | passed | Reject invalid target explicitly | ValueError: Target element '' not found in master database. |
| PN:invalid_target:1 | passed | Reject invalid target explicitly | ValueError: Target element 'Xx' not found in master database. |
| PN:invalid_target:2 | passed | Reject invalid target explicitly | ValueError: Target element 'ga' not found in master database. |
| PN:invalid_target:3 | passed | Reject invalid target explicitly | ValueError: Target element ' Ga ' not found in master database. |
| PN:invalid_target:4 | passed | Reject invalid target explicitly | ValueError: Target element 'Ga2O3' not found in master database. |
| PN:invalid_target:5 | passed | Reject invalid target explicitly | ValueError: Target element 'None' not found in master database. |
| PN:invalid_target:6 | passed | Reject invalid target explicitly | ValueError: Target element '31' not found in master database. |
| PN:invalid_target:7 | passed | Reject invalid target explicitly | TypeError: unhashable type: 'list' |
| PN:invalid_target:8 | passed | Reject invalid target explicitly | TypeError: unhashable type: 'dict' |
| PN:k=0 | passed | Return min(k, available candidates), no target | [] |
| PN:k=1 | passed | Return min(k, available candidates), no target | [{'method': 'PN', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'Al', 'similarity_score': 0.5}] |
| PN:k=1000 | passed | Return min(k, available candidates), no target | [{'method': 'PN', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'Al', 'similarity_score': 0.5}, {'method': 'PN', 'target_element': 'Ga', 'rank': 2, 'candidate_element': 'In', 'similarity_sco … (full record in JSON) |
| PN:invalid_k:-1 | failed | Reject negative, noninteger or boolean k | [{'method': 'PN', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'Al', 'similarity_score': 0.5}, {'method': 'PN', 'target_element': 'Ga', 'rank': 2, 'candidate_element': 'In', 'similarity_sco … (full record in JSON) |
| PN:invalid_k:1.5 | passed | Reject negative, noninteger or boolean k | TypeError: slice indices must be integers or None or have an __index__ method |
| PN:invalid_k:'10' | passed | Reject negative, noninteger or boolean k | TypeError: slice indices must be integers or None or have an __index__ method |
| PN:invalid_k:True | failed | Reject negative, noninteger or boolean k | [{'method': 'PN', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'Al', 'similarity_score': 0.5}] |
| PN:repeat | passed | Same input produces identical rankings | True |
| PN:all_pair_symmetry | passed | Symmetry within 1e-12 | 0.0 |
| PN:all_self_similarity | passed | Self similarity within 1e-12 | 0.0 |
| Atom2Vec:invalid_target:0 | passed | Reject invalid target explicitly | ValueError: Target element '' not in Atom2Vec vocabulary. |
| Atom2Vec:invalid_target:1 | passed | Reject invalid target explicitly | ValueError: Target element 'Xx' not in Atom2Vec vocabulary. |
| Atom2Vec:invalid_target:2 | passed | Reject invalid target explicitly | ValueError: Target element 'ga' not in Atom2Vec vocabulary. |
| Atom2Vec:invalid_target:3 | passed | Reject invalid target explicitly | ValueError: Target element ' Ga ' not in Atom2Vec vocabulary. |
| Atom2Vec:invalid_target:4 | passed | Reject invalid target explicitly | ValueError: Target element 'Ga2O3' not in Atom2Vec vocabulary. |
| Atom2Vec:invalid_target:5 | passed | Reject invalid target explicitly | ValueError: Target element 'None' not in Atom2Vec vocabulary. |
| Atom2Vec:invalid_target:6 | passed | Reject invalid target explicitly | ValueError: Target element '31' not in Atom2Vec vocabulary. |
| Atom2Vec:invalid_target:7 | passed | Reject invalid target explicitly | TypeError: unhashable type: 'list' |
| Atom2Vec:invalid_target:8 | passed | Reject invalid target explicitly | TypeError: unhashable type: 'dict' |
| Atom2Vec:k=0 | passed | Return min(k, available candidates), no target | [] |
| Atom2Vec:k=1 | passed | Return min(k, available candidates), no target | [{'method': 'Atom2Vec', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'Al', 'similarity_score': 0.846227}] |
| Atom2Vec:k=1000 | passed | Return min(k, available candidates), no target | [{'method': 'Atom2Vec', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'Al', 'similarity_score': 0.846227}, {'method': 'Atom2Vec', 'target_element': 'Ga', 'rank': 2, 'candidate_element': 'In' … (full record in JSON) |
| Atom2Vec:invalid_k:-1 | failed | Reject negative, noninteger or boolean k | [{'method': 'Atom2Vec', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'Al', 'similarity_score': 0.846227}, {'method': 'Atom2Vec', 'target_element': 'Ga', 'rank': 2, 'candidate_element': 'In' … (full record in JSON) |
| Atom2Vec:invalid_k:1.5 | passed | Reject negative, noninteger or boolean k | TypeError: slice indices must be integers or None or have an __index__ method |
| Atom2Vec:invalid_k:'10' | passed | Reject negative, noninteger or boolean k | TypeError: slice indices must be integers or None or have an __index__ method |
| Atom2Vec:invalid_k:True | failed | Reject negative, noninteger or boolean k | [{'method': 'Atom2Vec', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'Al', 'similarity_score': 0.846227}] |
| Atom2Vec:repeat | passed | Same input produces identical rankings | True |
| Atom2Vec:all_pair_symmetry | passed | Symmetry within 1e-12 | 0.0 |
| Atom2Vec:all_self_similarity | passed | Self similarity within 1e-12 | 6.661338147750939e-16 |
| Property:invalid_target:0 | passed | Reject invalid target explicitly | ValueError: Target element '' not in property candidate universe. |
| Property:invalid_target:1 | passed | Reject invalid target explicitly | ValueError: Target element 'Xx' not in property candidate universe. |
| Property:invalid_target:2 | passed | Reject invalid target explicitly | ValueError: Target element 'ga' not in property candidate universe. |
| Property:invalid_target:3 | passed | Reject invalid target explicitly | ValueError: Target element ' Ga ' not in property candidate universe. |
| Property:invalid_target:4 | passed | Reject invalid target explicitly | ValueError: Target element 'Ga2O3' not in property candidate universe. |
| Property:invalid_target:5 | passed | Reject invalid target explicitly | ValueError: Target element 'None' not in property candidate universe. |
| Property:invalid_target:6 | passed | Reject invalid target explicitly | ValueError: Target element '31' not in property candidate universe. |
| Property:invalid_target:7 | passed | Reject invalid target explicitly | TypeError: unhashable type: 'list' |
| Property:invalid_target:8 | passed | Reject invalid target explicitly | TypeError: unhashable type: 'dict' |
| Property:k=0 | passed | Return min(k, available candidates), no target | [] |
| Property:k=1 | passed | Return min(k, available candidates), no target | [{'method': 'Property', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'In', 'similarity_score': 0.877063}] |
| Property:k=1000 | passed | Return min(k, available candidates), no target | [{'method': 'Property', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'In', 'similarity_score': 0.877063}, {'method': 'Property', 'target_element': 'Ga', 'rank': 2, 'candidate_element': 'Sn' … (full record in JSON) |
| Property:invalid_k:-1 | failed | Reject negative, noninteger or boolean k | [{'method': 'Property', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'In', 'similarity_score': 0.877063}, {'method': 'Property', 'target_element': 'Ga', 'rank': 2, 'candidate_element': 'Sn' … (full record in JSON) |
| Property:invalid_k:1.5 | passed | Reject negative, noninteger or boolean k | TypeError: slice indices must be integers or None or have an __index__ method |
| Property:invalid_k:'10' | passed | Reject negative, noninteger or boolean k | TypeError: slice indices must be integers or None or have an __index__ method |
| Property:invalid_k:True | failed | Reject negative, noninteger or boolean k | [{'method': 'Property', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'In', 'similarity_score': 0.877063}] |
| Property:repeat | passed | Same input produces identical rankings | True |
| Property:all_pair_symmetry | passed | Symmetry within 1e-12 | 0.0 |
| Property:all_self_similarity | passed | Self similarity within 1e-12 | 4.440892098500626e-16 |
| PNSimilarityEngine:missing_file | passed | Reject missing dataset | FileNotFoundError: Master elements table not found at: C:\Final Project\results\stage_01\run_001\fixtures\missing.parquet |
| PropertySimilarityEngine:missing_file | passed | Reject missing dataset | FileNotFoundError: Master elements table not found at: C:\Final Project\results\stage_01\run_001\fixtures\missing.parquet |
| Property:duplicate | failed | Reject invalid master dataset before scoring | [{'method': 'Property', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'In', 'similarity_score': 0.873378}, {'method': 'Property', 'target_element': 'Ga', 'rank': 2, 'candidate_element': 'Sn' … (full record in JSON) |
| PN:duplicate | failed | Reject invalid master dataset | [{'method': 'PN', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'Al', 'similarity_score': 0.5}, {'method': 'PN', 'target_element': 'Ga', 'rank': 2, 'candidate_element': 'In', 'similarity_sco … (full record in JSON) |
| Property:empty | passed | Reject invalid master dataset before scoring | ValueError: Target element 'Ga' not in property candidate universe. |
| PN:empty | passed | Reject invalid master dataset | ValueError: Target element 'Ga' not found in master database. |
| Property:missing_feature | passed | Reject invalid master dataset before scoring | KeyError: "['density'] not in index" |
| Property:nan_feature | passed | Reject invalid master dataset before scoring | AssertionError: NaN values found in property candidate features! |
| Property:infinite_feature | failed | Reject invalid master dataset before scoring | [{'method': 'Property', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'H', 'similarity_score': 'NaN'}, {'method': 'Property', 'target_element': 'Ga', 'rank': 2, 'candidate_element': 'Li', 's … (full record in JSON) |
| Property:negative_density | failed | Reject invalid master dataset before scoring | [{'method': 'Property', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'In', 'similarity_score': 0.750418}, {'method': 'Property', 'target_element': 'Ga', 'rank': 2, 'candidate_element': 'Sn' … (full record in JSON) |
| Property:invalid_type | passed | Reject invalid master dataset before scoring | ValueError: could not convert string to float: 'bad' |
| Property:malformed_file | passed | Reject corrupt file | ArrowInvalid: Could not open Parquet input source '<Buffer>': Parquet magic bytes not found in footer. Either the file is corrupted or this is not a parquet file. |
| Atom2Vec:nan_cache | failed | Reject nonfinite cached vectors before scoring | [{'method': 'Atom2Vec', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'Al', 'similarity_score': 'NaN'}] |
| Atom2Vec:shape_cache | passed | Reject symbol/vector shape mismatch | IndexError: index 1 is out of bounds for axis 0 with size 1 |
| Atom2Vec:missing_corpus | passed | Reject missing corpus when cache absent | FileNotFoundError: Materials Project raw dataset not found at: C:\Final Project\results\stage_01\run_001\fixtures\none.gz |
| Atom2Vec:cache_dimension | failed | Requested embedding dimension agrees with loaded cache | 20 |
| PN:duplicate_candidate | failed | Reject duplicate or return unique candidates | {'total': 88, 'unique': 87, 'Al_count': 2} |
| Property:duplicate_candidate | failed | Reject duplicate or return unique candidates | {'total': 88, 'unique': 87, 'Al_count': 2} |
| Atom2Vec:zero_vectors | failed | Reject zero-norm cached vectors | {'observed_self_similarity': 0.0, 'observed_ranking': [{'method': 'Atom2Vec', 'target_element': 'Ga', 'rank': 1, 'candidate_element': 'Al', 'similarity_score': 0.0}]} |
| audit_runner:existing_run_id | passed | Reject repeated run rather than overwrite | {'exit_code': 1} |
| environment:simulated_missing_dependency | passed | Import failure when site-packages are deliberately hidden | {'scope': 'Simulation only; no installed dependency was removed.'} |


## Not executed / not yet verified

- Read-only directory / access-denied simulation, disk-full behavior, forced process termination and concurrent requests.
- Full corrupt/empty corpus training recovery, formula-parse failure accounting, version-migration compatibility and cross-OS reproduction.
- GPU model inference, charged defects, site-aware generation, property prediction and performance under load: not implemented and outside Stage 1.
- Complete independent literature validation: not completed. See reference_audit.md.

The deliberate `python -S` missing-dependency check is a simulation that hides installed packages; no package was removed. The repeated-run guard was executed and rejected reuse of run_001. Existing damaged fixtures were isolated copies, never original data.
