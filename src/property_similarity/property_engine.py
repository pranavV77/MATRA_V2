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
   - Legacy ranking policy: exclude noble gases; this is not a universal chemistry rule.
   - Standard Z-score normalization: z = (x - mu) / sigma across the candidate universe.
3. Similarity Metric:
   - Cosine similarity between normalized 14-dimensional feature vectors:
         S_prop(e_t, e_c) = (v_t . v_c) / (||v_t|| * ||v_c||)
   - Excludes target element itself (e_c != e_t).
   - Deterministic tie breaking by candidate symbol.
   - Output schema matching PN and Atom2Vec engines.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd
from src.similarity_validation import DEFAULT_MASTER, cosine, read_master, require_supported, support_status, validate_integer


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

    def __init__(self, master_parquet_path=DEFAULT_MASTER):
        self.df = read_master(master_parquet_path, ('symbol', 'group_id', *self.FEATURE_NAMES))
        
        # Exclude noble gases (group_id == 18)
        self.candidate_df = self.df[self.df["group_id"] != 18].copy().reset_index(drop=True)
        self.symbols = self.candidate_df["symbol"].tolist()
        self.sym2idx = {s: i for i, s in enumerate(self.symbols)}
        
        # Extract feature matrix (88 x 14)
        if len(self.candidate_df) < 2:
            raise ValueError('At least two non-noble feature rows are required for standardization')
        shell_bounds = {'s_valence_electrons': 2, 'p_valence_electrons': 6, 'd_valence_electrons': 10, 'f_valence_electrons': 14}
        for name in self.FEATURE_NAMES:
            series = self.candidate_df[name]
            if not pd.api.types.is_numeric_dtype(series) or pd.api.types.is_bool_dtype(series) or pd.api.types.is_complex_dtype(series):
                raise ValueError(f'{name}: real numeric feature dtype required')
            values = series.to_numpy(dtype=np.float64)
            if not np.isfinite(values).all() or (values < 0).any() or (name not in shell_bounds and (values == 0).any()):
                raise ValueError(f'{name}: nonfinite, negative or invalid zero feature')
            if name in shell_bounds or name == 'valence_electrons':
                bound = shell_bounds.get(name, 18)
                if (values > bound).any() or not np.equal(values, np.floor(values)).all():
                    raise ValueError(f'{name}: electron count outside integer bounds')
        raw_features = self.candidate_df[self.FEATURE_NAMES].values.astype(np.float64)
        
        # Standardize (Z-score)
        try:
            with np.errstate(over='raise', invalid='raise', divide='raise'):
                self.means = np.mean(raw_features, axis=0)
                self.stds = np.std(raw_features, axis=0)
                self.stds[self.stds == 0] = 1.0  # Constant columns contribute zero, not invented variation.
                standardized = (raw_features - self.means) / self.stds
                norms = np.linalg.norm(standardized, axis=1, keepdims=True)
                if not np.isfinite(norms).all() or (norms <= 0).any():
                    raise ValueError('Zero or invalid standardized vector: cosine direction is undefined')
                self.normed_features = standardized / norms
        except FloatingPointError as exc:
            raise ValueError('Property standardization is numerically unstable') from exc

    def compute_similarity(self, target_element: str, candidate_element: str) -> float:
        """Compute cosine similarity between 14-property vectors."""
        require_supported(target_element, self.sym2idx, 'Property')
        require_supported(candidate_element, self.sym2idx, 'Property', 'candidate')
            
        i = self.sym2idx[target_element]
        j = self.sym2idx[candidate_element]
        return cosine(np.dot(self.normed_features[i], self.normed_features[j]))

    def get_support_status(self, element):
        return support_status(element, self.sym2idx, self.symbols, 'Property')

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
        k = validate_integer(k, 'k')
        require_supported(target_element, self.sym2idx, 'Property')
            
        i = self.sym2idx[target_element]
        sims = self.normed_features.dot(self.normed_features[i])
        if not np.isfinite(sims).all():
            raise ValueError('Nonfinite property similarity scores')
        sims = np.clip(sims, -1.0, 1.0)
        
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
