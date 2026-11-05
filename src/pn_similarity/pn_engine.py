"""
Pierre Villars Mendeleev Periodic Number (PN) Similarity Engine.

Implementation of Signal 1 from the project architecture:
Uses the project's recorded Mendeleev Periodic Number scale (1 to 118)
derived from Pierre Villars et al. (Chem. Met. Alloys 2008) and validated in
PNcsp / PNcsp+ (Oran et al., Inorg. Chem. 2024, JCTC 2026).

Similarity Formula:
    S_PN(e_t, e_c) = 1.0 / (1.0 + |PN(e_t) - PN(e_c)|)
where e_t is the target element and e_c is the candidate element.

Filtering & Constraints:
- Candidate space: All 88 non-noble elements (Z=1..94 excluding group 18 noble gases).
- Excludes target element itself (e_c != e_t).
- Ties broken deterministically by alphabetical order of candidate elemental symbol.
- Returns Top-K candidates formatted with strict common output schema.
"""

from typing import List, Dict, Any
import numpy as np
from src.similarity_validation import DEFAULT_MASTER, read_master, require_supported, support_status, validate_integer


class PNSimilarityEngine:
    def __init__(self, master_parquet_path=DEFAULT_MASTER):
        self.df = read_master(master_parquet_path, ('symbol', 'group_id', 'mendeleev_number'))
        pn = self.df['mendeleev_number']
        if pn.dtype.kind not in 'iu' or pn.isna().any() or not np.isfinite(pn).all() or not pn.between(1, 118).all() or not pn.is_unique:
            raise ValueError('PN values must be unique integers in 1..118')
        self.pn_dict = dict(zip(self.df["symbol"], self.df["mendeleev_number"]))
        
        # Filter candidate universe: exclude noble gases (group_id == 18)
        self.candidate_elements = [
            sym for sym, grp in zip(self.df["symbol"], self.df["group_id"])
            if grp != 18
        ]
        
    def compute_similarity(self, target_element: str, candidate_element: str) -> float:
        """Compute S_PN between two elements."""
        require_supported(target_element, self.pn_dict, 'PN')
        require_supported(candidate_element, self.pn_dict, 'PN', 'candidate')
            
        dist = abs(self.pn_dict[target_element] - self.pn_dict[candidate_element])
        return 1.0 / (1.0 + float(dist))

    def get_support_status(self, element):
        """Distinguish recognition, query data and ranking-candidate policy."""
        return support_status(element, self.pn_dict, self.candidate_elements, 'PN')

    def get_top_k(self, target_element: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Generate Top-K ranked candidate elements for a target element based on PN similarity.
        
        Output schema per record:
        - method: 'PN'
        - target_element: str
        - rank: int (1..k)
        - candidate_element: str
        - similarity_score: float
        """
        k = validate_integer(k, 'k')
        require_supported(target_element, self.pn_dict, 'PN')
            
        t_pn = self.pn_dict[target_element]
        scored_candidates = []
        
        for cand in self.candidate_elements:
            if cand == target_element:
                continue  # Target element is strictly excluded
            
            c_pn = self.pn_dict[cand]
            dist = abs(t_pn - c_pn)
            sim = 1.0 / (1.0 + float(dist))
            scored_candidates.append((cand, sim, dist))
            
        # Sort by similarity descending; tie-break deterministically by candidate symbol
        scored_candidates.sort(key=lambda x: (-x[1], x[0]))
        
        results = []
        for rank, (cand, sim, _) in enumerate(scored_candidates[:k], start=1):
            results.append({
                "method": "PN",
                "target_element": target_element,
                "rank": rank,
                "candidate_element": cand,
                "similarity_score": round(float(sim), 6)
            })
            
        return results
