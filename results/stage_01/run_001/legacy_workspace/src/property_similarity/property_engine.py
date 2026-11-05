"""
Physicochemical Property-Based Similarity Engine.

Implementation of Signal 3 from the project architecture:
Uses continuous physical features from the audited master elemental table
`elements_master.parquet`.

Methodology:
1. Feature Selection:
   - Exactly 14 audited physical properties:
     1. pauling_electronegativity
     2. covalent_radius_cordero
     3. atomic_radius_slater
     4. first_ionization_energy
     5. melting_point
     6. thermal_conductivity
     7. dipole_polarizability
     8. valence_electrons
     9. s_valence_electrons
     10. p_valence_electrons
     11. d_valence_electrons
     12. f_valence_electrons
     13. density
     14. molar_volume
2. Preprocessing & Scaling:
   - Candidate universe: All 88 non-noble elements (noble gases excluded as unreactive).
   - Standard Z-score normalization: z = (x - mu) / sigma across the candidate universe.
3. Similarity Metric:
   - Cosine similarity between normalized 14-dimensional feature vectors:
         S_prop(e_t, e_c) = (v_t . v_c) / (||v_t|| * ||v_c||)
   - Excludes target element itself (e_c != e_t).
   - Deterministic tie breaking by candidate symbol.
   - Output schema matching PN and Atom2Vec engines.
"""

import os
from typing import List, Dict, Any
import numpy as np
import pandas as pd


class PropertySimilarityEngine:
    FEATURE_NAMES = [
        "pauling_electronegativity",
        "covalent_radius_cordero",
        "atomic_radius_slater",
        "first_ionization_energy",
        "melting_point",
        "thermal_conductivity",
        "dipole_polarizability",
        "valence_electrons",
        "s_valence_electrons",
        "p_valence_electrons",
        "d_valence_electrons",
        "f_valence_electrons",
        "density",
        "molar_volume"
    ]

    def __init__(self, master_parquet_path: str = os.path.join("data", "processed", "elements_master.parquet")):
        if not os.path.exists(master_parquet_path):
            raise FileNotFoundError(f"Master elements table not found at: {master_parquet_path}")
            
        self.df = pd.read_parquet(master_parquet_path)
        
        # Exclude noble gases (group_id == 18)
        self.candidate_df = self.df[self.df["group_id"] != 18].copy().reset_index(drop=True)
        self.symbols = self.candidate_df["symbol"].tolist()
        self.sym2idx = {s: i for i, s in enumerate(self.symbols)}
        
        # Extract feature matrix (88 x 14)
        raw_features = self.candidate_df[self.FEATURE_NAMES].values.astype(np.float64)
        assert not np.isnan(raw_features).any(), "NaN values found in property candidate features!"
        
        # Standardize (Z-score)
        self.means = np.mean(raw_features, axis=0)
        self.stds = np.std(raw_features, axis=0)
        self.stds[self.stds == 0] = 1.0
        standardized = (raw_features - self.means) / self.stds
        
        # L2 normalize rows for cosine similarity
        norms = np.linalg.norm(standardized, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.normed_features = standardized / norms

    def compute_similarity(self, target_element: str, candidate_element: str) -> float:
        """Compute cosine similarity between 14-property vectors."""
        if target_element not in self.sym2idx:
            raise ValueError(f"Target element '{target_element}' not in property candidate set.")
        if candidate_element not in self.sym2idx:
            raise ValueError(f"Candidate element '{candidate_element}' not in property candidate set.")
            
        i = self.sym2idx[target_element]
        j = self.sym2idx[candidate_element]
        return float(np.dot(self.normed_features[i], self.normed_features[j]))

    def get_top_k(self, target_element: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Generate Top-K candidate elements based on physicochemical property cosine similarity.
        
        Output schema per record:
        - method: 'Property'
        - target_element: str
        - rank: int (1..k)
        - candidate_element: str
        - similarity_score: float
        """
        if target_element not in self.sym2idx:
            raise ValueError(f"Target element '{target_element}' not in property candidate universe.")
            
        i = self.sym2idx[target_element]
        sims = self.normed_features.dot(self.normed_features[i])
        
        scored_candidates = []
        for idx, cand in enumerate(self.symbols):
            if cand == target_element:
                continue  # Target element strictly excluded
            scored_candidates.append((cand, float(sims[idx])))
            
        # Sort by similarity descending; tie-break deterministically by symbol
        scored_candidates.sort(key=lambda x: (-x[1], x[0]))
        
        results = []
        for rank, (cand, sim) in enumerate(scored_candidates[:k], start=1):
            results.append({
                "method": "Property",
                "target_element": target_element,
                "rank": rank,
                "candidate_element": cand,
                "similarity_score": round(float(sim), 6)
            })
            
        return results
