# Executed Stage 6 edge-case and regression report

Final regular suite: 510 passed (478 prior + 32 Stage 6). Final isolated-energy suite: 24 passed. Evidence: regular_004.xml and real_003.xml under logs/stage_06/run_002. The isolated suite includes actual potential inference, deliberately malformed outputs and checkpoint rejection guards. These are not 56 independent chemical validations.

| Suite | Executed case | Result | Seconds |
|---|---|---|---:|
| regular | test_invalid_relaxation_settings[kwargs0] | PASS | 0.001 |
| regular | test_invalid_relaxation_settings[kwargs1] | PASS | 0.001 |
| regular | test_invalid_relaxation_settings[kwargs2] | PASS | 0.001 |
| regular | test_invalid_relaxation_settings[kwargs3] | PASS | 0.001 |
| regular | test_invalid_relaxation_settings[kwargs4] | PASS | 0.001 |
| regular | test_invalid_relaxation_settings[kwargs5] | PASS | 0.001 |
| regular | test_invalid_relaxation_settings[kwargs6] | PASS | 0.001 |
| regular | test_invalid_relaxation_settings[kwargs7] | PASS | 0.001 |
| regular | test_invalid_relaxation_settings[kwargs8] | PASS | 0.001 |
| regular | test_invalid_relaxation_settings[kwargs9] | PASS | 0.001 |
| regular | test_metric_math_and_no_fake_stability | PASS | 0.000 |
| regular | test_invalid_regression_inputs[a0-b0] | PASS | 0.001 |
| regular | test_invalid_regression_inputs[a1-b1] | PASS | 0.001 |
| regular | test_invalid_regression_inputs[a2-b2] | PASS | 0.001 |
| regular | test_invalid_regression_inputs[a3-b3] | PASS | 0.001 |
| regular | test_invalid_regression_inputs[x-b4] | PASS | 0.001 |
| regular | test_composition_and_checkpoint_comparison_gate | PASS | 0.000 |
| regular | test_bridge_unique_outputs_and_environment | PASS | 0.017 |
| regular | test_bridge_failures_preserve_records | PASS | 0.009 |
| regular | test_bridge_timeout_and_busy | PASS | 0.008 |
| regular | test_geometry_and_energy_bridge_inputs | PASS | 0.052 |
| regular | test_whole_orbit_not_silently_changed_to_one_site | PASS | 0.010 |
| regular | test_service_rejects_bad_inputs_before_worker[updates0] | PASS | 0.011 |
| regular | test_service_rejects_bad_inputs_before_worker[updates1] | PASS | 0.003 |
| regular | test_service_rejects_bad_inputs_before_worker[updates2] | PASS | 0.012 |
| regular | test_service_rejects_bad_inputs_before_worker[updates3] | PASS | 0.001 |
| regular | test_service_rejects_bad_inputs_before_worker[updates4] | PASS | 0.001 |
| regular | test_service_rejects_bad_inputs_before_worker[updates5] | PASS | 0.003 |
| regular | test_service_rejects_bad_inputs_before_worker[updates6] | PASS | 0.004 |
| regular | test_service_rejects_bad_inputs_before_worker[updates7] | PASS | 0.001 |
| regular | test_service_rejects_bad_inputs_before_worker[updates8] | PASS | 0.001 |
| regular | test_non_object | PASS | 0.001 |
| isolated_energy | test_model_identity_and_coverage | PASS | 8.454 |
| isolated_energy | test_real_prediction_repeat_units_and_no_mutation[perovskite] | PASS | 0.673 |
| isolated_energy | test_real_prediction_repeat_units_and_no_mutation[wurtzite] | PASS | 0.185 |
| isolated_energy | test_translation_invariance | PASS | 0.125 |
| isolated_energy | test_permutation_invariance | PASS | 0.121 |
| isolated_energy | test_rotation_equivariance | PASS | 0.111 |
| isolated_energy | test_supercell_extensivity | PASS | 0.155 |
| isolated_energy | test_finite_difference_force | PASS | 0.179 |
| isolated_energy | test_relaxation_trajectory_and_convergence | PASS | 0.595 |
| isolated_energy | test_nonconvergence_is_reported | PASS | 0.127 |
| isolated_energy | test_no_relaxation_is_explicit | PASS | 0.061 |
| isolated_energy | test_unsupported_and_oversized_and_charged | PASS | 0.004 |
| isolated_energy | test_invalid_calculator_outputs_are_rejected[nan-forces0] | PASS | 0.001 |
| isolated_energy | test_invalid_calculator_outputs_are_rejected[inf-forces1] | PASS | 0.001 |
| isolated_energy | test_invalid_calculator_outputs_are_rejected[True-forces2] | PASS | 0.001 |
| isolated_energy | test_invalid_calculator_outputs_are_rejected[1-forces3] | PASS | 0.001 |
| isolated_energy | test_invalid_calculator_outputs_are_rejected[1.0-forces4] | PASS | 0.001 |
| isolated_energy | test_invalid_calculator_outputs_are_rejected[1.0-forces5] | PASS | 0.001 |
| isolated_energy | test_invalid_calculator_outputs_are_rejected[1.0-forces6] | PASS | 0.001 |
| isolated_energy | test_stage5_partial_formal_charge_is_explicitly_normalized | PASS | 0.063 |
| isolated_energy | test_public_predictions_actually_rerun_calculator | PASS | 0.123 |
| isolated_energy | test_checkpoint_integrity_guards[missing] | PASS | 0.025 |
| isolated_energy | test_checkpoint_integrity_guards[tampered] | PASS | 0.027 |
| isolated_energy | test_checkpoint_integrity_guards[outside] | PASS | 0.024 |
