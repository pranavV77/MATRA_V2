# Stage 2 executed edge-case report

Final suite: 73 passed; 47 new tests plus 26 legacy tests. Each row below is an actually executed pytest record. Logs and JUnit XML are under results/stage_02/run_001 and logs/stage_02/run_001.

| Executed test | Result |
|---|---|
| test_native_release_valid | passed |
| test_source_values_and_missingness_preserved | passed |
| test_explicit_units_and_pn | passed |
| test_no_fr_conductivity_invention | passed |
| test_radius_estimates_separate_and_reproducible | passed |
| test_source_estimates_different_from_project_imputation | passed |
| test_registry_recognizes_not_invents | passed |
| test_corrupt_native_data_rejected[empty] | passed |
| test_corrupt_native_data_rejected[duplicate] | passed |
| test_corrupt_native_data_rejected[missing_column] | passed |
| test_corrupt_native_data_rejected[negative_density] | passed |
| test_corrupt_native_data_rejected[infinity] | passed |
| test_corrupt_native_data_rejected[new_nan] | passed |
| test_corrupt_native_data_rejected[string_type] | passed |
| test_corrupt_native_data_rejected[bad_atomic_number] | passed |
| test_corrupt_native_data_rejected[wrong_symbol] | passed |
| test_corrupt_native_data_rejected[bad_pn] | passed |
| test_corrupt_native_data_rejected[bad_normalization] | passed |
| test_corrupt_native_data_rejected[fractional_electrons] | passed |
| test_corrupt_native_data_rejected[count_mismatch] | passed |
| test_bad_provenance_rejected[duplicate] | passed |
| test_bad_provenance_rejected[missing] | passed |
| test_bad_provenance_rejected[wrong_unit] | passed |
| test_bad_provenance_rejected[wrong_value] | passed |
| test_bad_provenance_rejected[imputed] | passed |
| test_bad_provenance_rejected[missing_source] | passed |
| test_registry_errors_rejected[missing_element] | passed |
| test_registry_errors_rejected[duplicate_symbol] | passed |
| test_registry_errors_rejected[claims_validation] | passed |
| test_registry_errors_rejected[fake_features] | passed |
| test_registry_errors_rejected[boolean_z] | passed |
| test_registry_errors_rejected[boolean_feature_count] | passed |
| test_legacy_cases_preserved_but_not_certified | passed |
| test_invalid_benchmark_admission_rejected[unknown_credit] | passed |
| test_invalid_benchmark_admission_rejected[missing_locator] | passed |
| test_invalid_benchmark_admission_rejected[missing_scientific_class] | passed |
| test_invalid_benchmark_admission_rejected[missing_conditions] | passed |
| test_invalid_benchmark_admission_rejected[duplicate_case] | passed |
| test_invalid_benchmark_admission_rejected[track_mix] | passed |
| test_invalid_benchmark_admission_rejected[unknown_candidate] | passed |
| test_invalid_benchmark_admission_rejected[invalid_target] | passed |
| test_registry_metadata_not_chemical_evidence | passed |
| test_json_errors_reported | passed |
| test_release_refuses_overwrite_and_preserves_files | passed |
| test_outside_project_output_refused | passed |
| test_same_snapshot_build_identical | passed |
| test_persisted_release_matches_current_builder | passed |


## Boundaries

The initial run had 43 new tests; a later 70-test run added persisted-artifact reproduction; the final 73-test run also added boolean feature-count and invalid benchmark symbol/target checks. Earlier logs are preserved. No final failing test was hidden.

Dependency consistency was checked with pip check: no broken requirements found. Five unique DOI queries returned HTTP 404; these are recorded source-resolution failures, not positive test results or proof that the referenced chemistry is impossible. Responses and error details are cached.

Not tested: physical disk-full/access-denied interruption, concurrent release writers, every malformed nested JSON shape, live DOI-service outage recovery beyond recorded request errors, clean-machine installation, cross-platform regeneration, and chemistry correctness of every property/reference. The new validators protect the new data pipeline; the legacy engines still retain Stage 1 robustness defects for Stage 3.
