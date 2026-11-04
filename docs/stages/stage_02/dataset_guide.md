# Stage 2 dataset guide — release 2.0.0-audit

This release is additive. Original data, results and engines remain unchanged. The suffix `audit` means the data lineage and review state are explicit; it does not certify all properties as measurements or the benchmark as scientific ground truth.

## What is stored and why

| File | Purpose |
|---|---|
| data/raw/stage_02_sources/source_snapshot.json | Captured pinned-library values, selected fallback sources, source property metadata, 118-element registry source and warnings; offline rebuild input |
| data/raw/stage_02_sources/doi_lookup.json and DOI files | Raw registry responses and resolution outcomes; bibliographic checks only |
| data/processed/v2_0_0/elements_native.parquet | 94-element native/explicitly derived feature table; nine source gaps retained |
| data/processed/v2_0_0/cell_provenance.jsonl | One source/origin/unit/value record for every one of the 1,316 feature cells |
| data/processed/v2_0_0/element_registry.json | Recognizes all 118 elements; reports native-feature availability and legacy engine support separately |
| data/processed/v2_0_0/feature_metadata.json | Correct units, PN convention, source annotations, scope and source hashes |
| data/processed/v2_0_0/radius_estimates.json | Optional estimated radii, fit coefficients and leave-one-out diagnostics; not merged into native table |
| data/processed/v2_0_0/release_manifest.json | Versioned artifact hashes and explicit nonactivation in old engines |
| data/benchmark/v2_0_0/benchmark_review.json | All original 16 cases retained inside a claim-level review ledger; no unsupported evaluation credit |

## Four important corrections

1. Polarizability is stored in the source's bohr^3 convention. Existing numeric values are not falsely relabelled Angstrom^3 and no unnecessary conversion is performed.
2. PN source metadata cites Pettifor1984/Villars2004 with a source extension to all elements. The new convenience field is PN/118. Its name identifies the denominator; the old PN/103 field remains only in legacy data. Source agreement is not a complete historical rederivation of every published PN convention.
3. Density follows documented source conditions, with gases and theoretical estimates. Upstream At/Fr density estimates and derived volumes are flagged. None are promoted to experimentally verified measurements.
4. The derived volume is atomic weight divided by source density, in cm^3/mol atoms. It is not uniformly a condensed-solid molar volume. Source phase/temperature context must travel with it.

## Imputation explained

Native values are not project-imputed. Three Pauling gaps, five radius gaps and one Fr conductivity gap remain. The regression line for radius uses 89 observed source pairs. Slope=0.800151612; intercept=28.586066407 pm. Training R²=0.772848; leave-one-element-out MAE=13.286621 pm, RMSE=19.993328 pm. These are executed diagnostics, not validation of missing-element estimates. The old reported R²=0.963 is not supported by this executed fit. No prediction intervals are claimed.

An upstream source estimate and a project imputation are different. Storing a library value does not imply it was measured experimentally. Cell provenance explicitly says independent measurement classification has not been completed.

## Feature dictionary

- `pauling_electronegativity`: **dimensionless**. Pauling electronegativity; unavailable values remain missing.
- `covalent_radius_cordero_pm`: **pm**. Cordero covalent radius.
- `atomic_radius_slater_pm`: **pm**. Mendeleev atomic_radius; source metadata cites Slater1964.
- `first_ionization_energy_ev`: **eV**. First atomic ionization energy.
- `melting_point_k`: **K**. Library-selected allotrope or pymatgen fallback; not a compound melting point.
- `thermal_conductivity_w_mk`: **W/(m K)**. Elemental thermal conductivity; source temperature/phase conventions apply.
- `dipole_polarizability_bohr3`: **bohr^3**. Stored polarizability-volume convention, not Angstrom^3.
- `valence_electrons`: **electron count**. Mendeleev nvalence convention, not a universal definition.
- `s_valence_electrons`: **electron count**. Existing project active-subshell rule.
- `p_valence_electrons`: **electron count**. Existing project active-subshell rule.
- `d_valence_electrons`: **electron count**. Existing project active-subshell rule.
- `f_valence_electrons`: **electron count**. Existing project active-subshell rule.
- `density_g_cm3`: **g/cm^3**. Source density near room temperature; gases and upstream estimates explicitly flagged.
- `atomic_molar_volume_cm3_mol_atoms`: **cm^3/mol atoms**. Atomic weight divided by source density; not uniformly a solid-state molar volume.

## Benchmark rules

Every case is retained for traceability. Unknown chemistry is not a negative label. A matching DOI/title is not enough to verify host, phase, site, concentration and property behavior. The current strict contextual benchmark has zero eligible claims; no revised scientific accuracy figure is produced. Legacy results remain reproducible as legacy diagnostics.

Six case entries have a definite citation/topic mismatch in resolved metadata; five have unresolved identifiers, four have partial topic support and one relies on a review. These counts are case-level; the review contains 23 candidate assertions in total. Complete experimental/DFT passage extraction remains a research task. Do not display original blanket EXPERIMENTAL_DIRECT labels as newly verified truth.
