"""
Unit tests for elements_master dataset generation and integrity.
"""

import os
import json
import hashlib
import numpy as np
import pandas as pd
import pytest


@pytest.fixture(scope="module")
def dataset_paths():
    parquet_path = os.path.join("data", "processed", "elements_master.parquet")
    metadata_path = os.path.join("data", "processed", "feature_metadata.json")
    return parquet_path, metadata_path


@pytest.fixture(scope="module")
def df(dataset_paths):
    parquet_path, _ = dataset_paths
    assert os.path.exists(parquet_path), f"Parquet file {parquet_path} does not exist!"
    return pd.read_parquet(parquet_path)


@pytest.fixture(scope="module")
def metadata(dataset_paths):
    _, metadata_path = dataset_paths
    assert os.path.exists(metadata_path), f"Metadata file {metadata_path} does not exist!"
    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_element_count_and_keys(df):
    """Verify exactly 94 rows, primary keys, and lack of duplicates."""
    assert len(df) == 94, f"Expected exactly 94 elements, got {len(df)}"
    assert df["atomic_number"].tolist() == list(range(1, 95))
    assert df["atomic_number"].nunique() == 94
    assert df["symbol"].nunique() == 94
    assert df["name"].nunique() == 94


def test_villars_pn_completeness_and_anchors(df):
    """Verify Pierre Villars PN values against published anchors."""
    assert df["mendeleev_number"].notnull().all()
    assert (df["mendeleev_number"] >= 1).all()
    assert (df["mendeleev_number"] <= 118).all()
    
    # Specific anchors
    h_pn = df.loc[df["symbol"] == "H", "mendeleev_number"].values[0]
    ga_pn = df.loc[df["symbol"] == "Ga", "mendeleev_number"].values[0]
    al_pn = df.loc[df["symbol"] == "Al", "mendeleev_number"].values[0]
    ti_pn = df.loc[df["symbol"] == "Ti", "mendeleev_number"].values[0]
    li_pn = df.loc[df["symbol"] == "Li", "mendeleev_number"].values[0]
    
    assert h_pn == 105
    assert ga_pn == 83
    assert al_pn == 82
    assert ti_pn == 43
    assert li_pn == 1


def test_noble_gas_electronegativity_is_nan(df):
    """Verify noble gases He, Ne, Ar remain strictly NaN and are not assigned artificial zeros."""
    for sym in ["He", "Ne", "Ar"]:
        val = df.loc[df["symbol"] == sym, "pauling_electronegativity"].values[0]
        assert np.isnan(val), f"Electronegativity for {sym} must be NaN, got {val}"
        
    # Check that solid-forming elements have valid electronegativities
    for sym in ["H", "C", "O", "Ga", "Ti", "Fe", "Au"]:
        val = df.loc[df["symbol"] == sym, "pauling_electronegativity"].values[0]
        assert not np.isnan(val), f"Electronegativity for {sym} should not be NaN"
        assert val > 0.0, f"Electronegativity for {sym} must be positive"


def test_physical_value_bounds(df):
    """Sanity check physical property ranges across all elements."""
    # Covalent radius (Cordero et al., 2008 ranges up to 260 pm for Francium)
    assert (df["covalent_radius_cordero"] > 25.0).all()
    assert (df["covalent_radius_cordero"] <= 265.0).all()
    
    # First ionization energy (eV)
    assert (df["first_ionization_energy"] > 3.5).all()
    assert (df["first_ionization_energy"] < 26.0).all()
    
    # Melting point (K)
    assert (df["melting_point"] > 0.0).all()
    assert (df["melting_point"] < 4500.0).all()
    
    # Density (g/cm^3)
    assert (df["density"] > 0.0).all()
    assert (df["density"] < 30.0).all()
    
    # Thermal conductivity (W/(m*K))
    assert (df["thermal_conductivity"] > 0.0).all()
    assert (df["thermal_conductivity"] < 500.0).all()
    
    # Polarizability (Angstrom^3) - Cesium is 400.9 A^3 in mendeleev
    assert (df["dipole_polarizability"] > 0.0).all()
    assert (df["dipole_polarizability"] < 450.0).all()


def test_imputation_flags_transparency(df):
    """Verify that imputation flags are explicit and accurately identify imputed elements."""
    # Exactly 5 elements imputed for atomic radius
    imputed_rad_syms = set(df.loc[df["imputed_atomic_radius"], "symbol"])
    assert imputed_rad_syms == {"Kr", "Xe", "At", "Rn", "Fr"}
    
    # Exactly 1 element imputed for thermal conductivity
    imputed_tc_syms = set(df.loc[df["imputed_thermal_conductivity"], "symbol"])
    assert imputed_tc_syms == {"Fr"}
    
    # imputed_pauling is False for all elements (remains NaN)
    assert not df["imputed_pauling"].any()
    
    # has_imputed_values is True only for those 5 elements (Fr has both radius & tc imputed)
    assert set(df.loc[df["has_imputed_values"], "symbol"]) == {"Kr", "Xe", "At", "Rn", "Fr"}
    assert df["has_imputed_values"].sum() == 5


def test_subshell_and_valence_definitions(df):
    """Verify valence electron properties follow documented library/project conventions."""
    assert (df["valence_electrons"] >= 1).all()
    assert (df["valence_electrons"] <= 18).all()
    
    # Subshell non-negativity and upper bounds
    assert (df["s_valence_electrons"] >= 0).all() and (df["s_valence_electrons"] <= 2).all()
    assert (df["p_valence_electrons"] >= 0).all() and (df["p_valence_electrons"] <= 6).all()
    assert (df["d_valence_electrons"] >= 0).all() and (df["d_valence_electrons"] <= 10).all()
    assert (df["f_valence_electrons"] >= 0).all() and (df["f_valence_electrons"] <= 14).all()
    
    # Main group s-block elements have s == valence_electrons
    s_block = df[df["group_id"].isin([1, 2]) & (df["atomic_number"] <= 56)]
    for _, row in s_block.iterrows():
        assert row["s_valence_electrons"] == row["valence_electrons"]
        assert row["p_valence_electrons"] == 0
        assert row["d_valence_electrons"] == 0
        assert row["f_valence_electrons"] == 0


def test_sha256_checksum_consistency(dataset_paths, metadata):
    """Verify that stored metadata SHA256 matches actual file on disk."""
    parquet_path, _ = dataset_paths
    with open(parquet_path, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()
    assert actual_hash == metadata["sha256_checksum"]
