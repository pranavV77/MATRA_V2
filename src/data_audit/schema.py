"""Explicit units and source conventions for MATRA data release 2.0.0-audit."""
FEATURES = {
    'pauling_electronegativity': ('dimensionless', 'Pauling electronegativity; unavailable values remain missing'),
    'covalent_radius_cordero_pm': ('pm', 'Cordero covalent radius'),
    'atomic_radius_slater_pm': ('pm', 'Mendeleev atomic_radius; source metadata cites Slater1964'),
    'first_ionization_energy_ev': ('eV', 'First atomic ionization energy'),
    'melting_point_k': ('K', 'Library-selected allotrope or pymatgen fallback; not a compound melting point'),
    'thermal_conductivity_w_mk': ('W/(m K)', 'Elemental thermal conductivity; source temperature/phase conventions apply'),
    'dipole_polarizability_bohr3': ('bohr^3', 'Stored polarizability-volume convention, not Angstrom^3'),
    'valence_electrons': ('electron count', 'Mendeleev nvalence convention, not a universal definition'),
    's_valence_electrons': ('electron count', 'Existing project active-subshell rule'),
    'p_valence_electrons': ('electron count', 'Existing project active-subshell rule'),
    'd_valence_electrons': ('electron count', 'Existing project active-subshell rule'),
    'f_valence_electrons': ('electron count', 'Existing project active-subshell rule'),
    'density_g_cm3': ('g/cm^3', 'Source density near room temperature; gases and upstream estimates explicitly flagged'),
    'atomic_molar_volume_cm3_mol_atoms': ('cm^3/mol atoms', 'Atomic weight divided by source density; not uniformly a solid-state molar volume'),
}
LEGACY_FEATURE_MAP = {
    'pauling_electronegativity':'pauling_electronegativity',
    'covalent_radius_cordero':'covalent_radius_cordero_pm',
    'atomic_radius_slater':'atomic_radius_slater_pm',
    'first_ionization_energy':'first_ionization_energy_ev',
    'melting_point':'melting_point_k',
    'thermal_conductivity':'thermal_conductivity_w_mk',
    'dipole_polarizability':'dipole_polarizability_bohr3',
    'valence_electrons':'valence_electrons',
    's_valence_electrons':'s_valence_electrons','p_valence_electrons':'p_valence_electrons',
    'd_valence_electrons':'d_valence_electrons','f_valence_electrons':'f_valence_electrons',
    'density':'density_g_cm3','molar_volume':'atomic_molar_volume_cm3_mol_atoms',
}
SUBSHELL_BOUNDS={'s_valence_electrons':2,'p_valence_electrons':6,'d_valence_electrons':10,'f_valence_electrons':14}
EXPECTED_NATIVE_MISSING={
    ('He','pauling_electronegativity'),('Ne','pauling_electronegativity'),('Ar','pauling_electronegativity'),
    ('Kr','atomic_radius_slater_pm'),('Xe','atomic_radius_slater_pm'),('At','atomic_radius_slater_pm'),
    ('Rn','atomic_radius_slater_pm'),('Fr','atomic_radius_slater_pm'),('Fr','thermal_conductivity_w_mk'),
}
SOURCE_ESTIMATED_DENSITIES={'At','Fr','Es','Fm','Md','No','Lr','Rf','Db','Sg','Bh','Hs','Mt','Ds','Rg','Cn','Nh','Fl','Mc','Lv','Ts','Og'}
SOURCE_URLS={
    'mendeleev':'https://mendeleev.readthedocs.io/en/stable/data.html',
    'models':'https://mendeleev.readthedocs.io/en/stable/api/models.html',
    'pymatgen':'https://pymatgen.org/pymatgen.core.html',
}
