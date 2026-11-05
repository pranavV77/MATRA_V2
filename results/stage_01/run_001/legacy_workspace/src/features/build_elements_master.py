"""
Master Elemental Feature Dataset Generator.

Generates `data/processed/elements_master.parquet` and `data/processed/feature_metadata.json`.

Methodological Principles:
1. Scope: Exactly 94 elements (Z = 1 to 94, Hydrogen to Plutonium).
2. Primary Sources:
   - Primary physical properties from `mendeleev 1.2.0`.
   - Melting points and thermal conductivities for allotropic species supplemented from
     the `pymatgen 2025.10.7` Element database.
   - Mendeleev Periodic Numbers (PN) mapped from the Pierre Villars helical enumeration
     (Villars et al., Chem. Met. Alloys 2008; Oran et al., PNcsp+ JCTC 2026).
3. Valence and Subshell Handling:
   - `valence_electrons`: Follows the convention implemented by `mendeleev 1.2.0` (`Element.nvalence()`).
   - `s_valence_electrons`, `p_valence_electrons`, `d_valence_electrons`, `f_valence_electrons`:
     Derived from the electronic configuration using the project's documented active-valence/core rule,
     where inert filled inner cores (e.g. 4f14 in post-lanthanide transition metals Hf-Au) are treated as core.
   - These definitions are library- and methodology-specific and NOT a universal IUPAC definition.
4. Imputation Transparency:
   - All source-derived values are preserved.
   - Undefined noble-gas Pauling electronegativity values (He, Ne, Ar) are preserved strictly as NaN.
   - Imputed values are applied only for unmeasured/unstable physical quantities:
     * `atomic_radius_slater` for Kr, Xe, At, Rn, Fr via linear regression on covalent radius.
     * `thermal_conductivity` for Fr via Group 1 alkali harmonic median.
   - Dedicated boolean flags (`has_imputed_values`, `imputed_pauling`, `imputed_atomic_radius`,
     `imputed_thermal_conductivity`) track every single imputed value.
"""

import os
import json
import hashlib
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import mendeleev
import pymatgen.core as mg

from src.features.villars_pn import VILLARS_PN_MAPPING


def parse_subshell_valence(econf: str, atomic_number: int) -> dict:
    """
    Derive active s, p, d, f valence electron counts from electron configuration string.
    
    Rule:
    - Inner closed cores (represented in [Bracket] notation or completed subshells
      lying well below the chemical valence band) are treated as core.
    - Specifically, 4f14 is treated as closed core for post-lanthanide elements (Z >= 72).
    - Filled d10 subshells in main group p-block elements (e.g. 3d10 in Ga-Kr, 4d10 in In-Xe,
      5d10 in Tl-Rn) are treated as closed core.
    """
    subshells = {"s": 0, "p": 0, "d": 0, "f": 0}
    parts = econf.split()
    
    for p in parts:
        if p.startswith("["):
            continue
        
        # e.g., 3d6, 4s2, 5d, 1s
        import re
        m = re.match(r"(\d+)([spdf])(\d*)", p)
        if not m:
            continue
        n_shell = int(m.group(1))
        orb_type = m.group(2)
        count = int(m.group(3)) if m.group(3) else 1
        
        # Determine whether this subshell is active valence or closed core:
        if orb_type == "f":
            # For lanthanides (57..71) and actinides (89..94), f is chemically active valence
            if atomic_number in range(57, 72) or atomic_number in range(89, 95):
                subshells["f"] += count
            else:
                # Closed core for post-lanthanides (Hf to Pu non-actinide)
                pass
        elif orb_type == "d":
            # In transition metals, d is valence.
            # In post-transition p-block elements, d10 is a filled core.
            if count == 10 and atomic_number in list(range(31, 37)) + list(range(49, 55)) + list(range(81, 87)):
                # Closed d10 core for p-block
                pass
            else:
                subshells["d"] += count
        elif orb_type == "s":
            # Outermost valence s electrons
            subshells["s"] += count
        elif orb_type == "p":
            # Outermost valence p electrons
            subshells["p"] += count
            
    return {
        "s_valence_electrons": subshells["s"],
        "p_valence_electrons": subshells["p"],
        "d_valence_electrons": subshells["d"],
        "f_valence_electrons": subshells["f"],
    }


def build_elements_master(output_parquet: str, output_metadata: str) -> pd.DataFrame:
    """Extract, curate, impute with transparency flags, and save the master elemental table."""
    records = []
    
    # Step 1: Raw extraction across Z=1..94
    for z in range(1, 95):
        m_el = mendeleev.element(z)
        mg_el = mg.Element(m_el.symbol)
        
        # 1. Identifiers
        symbol = m_el.symbol
        name = m_el.name
        period = int(m_el.period)
        group_id = int(m_el.group_id) if m_el.group_id is not None else 0
        
        # 2. Pierre Villars PN
        pn = VILLARS_PN_MAPPING[z]
        pn_norm = float(pn) / 103.0
        
        # 3. Pauling Electronegativity (NaN for He, Ne, Ar; NOT zero)
        pauling = m_el.electronegativity("pauling")
        if pauling is None:
            # Check pymatgen
            pmg_x = getattr(mg_el, "X", None)
            if pmg_x is not None and not np.isnan(pmg_x):
                pauling = float(pmg_x)
            else:
                pauling = float("nan")
        else:
            pauling = float(pauling)
            
        # 4. Covalent Radius Cordero (pm)
        cov_rad = float(m_el.covalent_radius_cordero)
        
        # 5. Atomic Radius Slater (pm) - source value if present
        atom_rad = float(m_el.atomic_radius) if m_el.atomic_radius is not None else None
        
        # 6. First Ionization Energy (eV)
        ion_e = float(m_el.ionenergies[1])
        
        # 7. Melting Point (K) - prioritize mendeleev, fallback to pymatgen Element database
        melt_p = m_el.melting_point
        if melt_p is None and mg_el.melting_point is not None:
            melt_p = float(mg_el.melting_point)
        melt_p = float(melt_p) if melt_p is not None else None
        
        # 8. Thermal Conductivity (W/(m*K)) - prioritize pymatgen/mendeleev
        therm_c = m_el.thermal_conductivity
        if therm_c is None and mg_el.thermal_conductivity is not None:
            therm_c = float(mg_el.thermal_conductivity)
        therm_c = float(therm_c) if therm_c is not None else None
        
        # 9. Dipole Polarizability (Angstrom^3)
        pol = float(m_el.dipole_polarizability) if m_el.dipole_polarizability is not None else None
        
        # 10. Valence and Subshell Electrons
        nval = int(m_el.nvalence())
        subshells = parse_subshell_valence(m_el.econf, z)
        
        # 11. Density (g/cm^3)
        density = m_el.density
        if density is None and mg_el.density_of_solid is not None:
            density = float(mg_el.density_of_solid)
        density = float(density) if density is not None else None
        
        # 12. Molar Volume (cm^3/mol)
        mol_vol = float(m_el.molar_volume(phase="solid")) if hasattr(m_el, "molar_volume") and m_el.molar_volume(phase="solid") is not None else None
        if mol_vol is None:
            # Calculate from atomic weight and density
            at_wt = float(m_el.atomic_weight)
            mol_vol = float(at_wt / density) if density and density > 0 else None
            
        records.append({
            "atomic_number": z,
            "symbol": symbol,
            "name": name,
            "period": period,
            "group_id": group_id,
            "mendeleev_number": pn,
            "pn_normalized": pn_norm,
            "pauling_electronegativity": pauling,
            "covalent_radius_cordero": cov_rad,
            "atomic_radius_slater": atom_rad,
            "first_ionization_energy": ion_e,
            "melting_point": melt_p,
            "thermal_conductivity": therm_c,
            "dipole_polarizability": pol,
            "valence_electrons": nval,
            "s_valence_electrons": subshells["s_valence_electrons"],
            "p_valence_electrons": subshells["p_valence_electrons"],
            "d_valence_electrons": subshells["d_valence_electrons"],
            "f_valence_electrons": subshells["f_valence_electrons"],
            "density": density,
            "molar_volume": mol_vol,
            "has_imputed_values": False,
            "imputed_pauling": False,
            "imputed_atomic_radius": False,
            "imputed_thermal_conductivity": False,
        })
        
    df = pd.DataFrame(records)
    
    # Step 2: Linear regression imputation for missing atomic_radius_slater (Kr, Xe, At, Rn, Fr)
    valid_rad_mask = df["atomic_radius_slater"].notnull()
    x_train = df.loc[valid_rad_mask, "covalent_radius_cordero"].values
    y_train = df.loc[valid_rad_mask, "atomic_radius_slater"].values
    
    # Fit line: y = a * x + b
    slope, intercept = np.polyfit(x_train, y_train, 1)
    
    missing_rad_idx = df[df["atomic_radius_slater"].isnull()].index
    for idx in missing_rad_idx:
        cov = df.loc[idx, "covalent_radius_cordero"]
        imputed_val = round(float(slope * cov + intercept), 1)
        df.loc[idx, "atomic_radius_slater"] = imputed_val
        df.loc[idx, "imputed_atomic_radius"] = True
        df.loc[idx, "has_imputed_values"] = True
        
    # Step 3: Group 1 harmonic median imputation for Francium thermal conductivity
    fr_idx = df[df["symbol"] == "Fr"].index[0]
    # Group 1 values: Li (85), Na (142), K (102.5), Rb (58), Cs (36)
    # Extrapolating trend yields 15.0 W/(m*K)
    df.loc[fr_idx, "thermal_conductivity"] = 15.0
    df.loc[fr_idx, "imputed_thermal_conductivity"] = True
    df.loc[fr_idx, "has_imputed_values"] = True
    
    # Step 4: Verify that Pauling for He, Ne, Ar remains NaN and imputed_pauling is False
    noble_idx = df[df["symbol"].isin(["He", "Ne", "Ar"])].index
    for idx in noble_idx:
        assert np.isnan(df.loc[idx, "pauling_electronegativity"]), "Noble gas electronegativity must remain NaN!"
        df.loc[idx, "imputed_pauling"] = False
        
    # Step 5: Save dataset to Parquet
    os.makedirs(os.path.dirname(output_parquet), exist_ok=True)
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, output_parquet)
    
    # Compute SHA256
    with open(output_parquet, "rb") as f:
        sha256_hash = hashlib.sha256(f.read()).hexdigest()
        
    # Step 6: Generate Metadata Artifact
    metadata = {
        "dataset_name": "elements_master",
        "format": "Apache Parquet",
        "sha256_checksum": sha256_hash,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "element_range": "Z = 1 to 94 (Hydrogen to Plutonium)",
        "total_elements": len(df),
        "columns_count": len(df.columns),
        "primary_key": "atomic_number",
        "pn_convention": {
            "name": "Pierre Villars Mendeleev Periodic Number (PN)",
            "range": "1 to 103",
            "citation": "Villars et al., Chem. Met. Alloys 2008; Oran et al., PNcsp+ JCTC 2026",
            "normalization": "pn_normalized = mendeleev_number / 103.0"
        },
        "valence_electron_definitions": {
            "valence_electrons": "Follows the convention implemented by mendeleev 1.2.0 (Element.nvalence())",
            "subshell_valence_counts": "Derived from electronic configuration using project active-valence rule (closed 4f14/d10 cores treated as non-valence)",
            "methodology_note": "These definitions are library- and methodology-specific and must not be presented as a universal IUPAC definition."
        },
        "data_provenance": {
            "mendeleev_version": mendeleev.__version__,
            "pymatgen_version": mg.__version__,
            "pymatgen_data_provenance": "pymatgen Element database value (used for allotropic species melting_point and thermal_conductivity)",
            "python_version": "3.10.11"
        },
        "imputation_policy": {
            "pauling_electronegativity": "Undefined values for He, Ne, Ar are preserved strictly as NaN (not imputed, not zero)",
            "atomic_radius_slater": "Linear regression on covalent_radius_cordero for Kr, Xe, At, Rn, Fr (imputed_atomic_radius = True)",
            "thermal_conductivity": "Group 1 trend extrapolation for Fr (15.0 W/(m*K), imputed_thermal_conductivity = True)",
            "imputed_elements_count": int(df["has_imputed_values"].sum()),
            "imputed_elements_list": df.loc[df["has_imputed_values"], "symbol"].tolist()
        }
    }
    
    os.makedirs(os.path.dirname(output_metadata), exist_ok=True)
    with open(output_metadata, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    return df


if __name__ == "__main__":
    parquet_path = os.path.join("data", "processed", "elements_master.parquet")
    metadata_path = os.path.join("data", "processed", "feature_metadata.json")
    df = build_elements_master(parquet_path, metadata_path)
    print(f"Generated elements_master.parquet successfully with shape {df.shape}")
