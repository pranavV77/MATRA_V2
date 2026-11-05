"""
Atom2Vec Unsupervised Representation Learning and Similarity Engine.

Faithful implementation of the model-free Atom2Vec methodology from:
    Zhou et al., "Atom2Vec: Learning Atoms for Materials Discovery",
    Proc. Natl. Acad. Sci. USA, 115, 6411-6417 (2018).

Methodology Details:
1. Input Corpus:
   - All binary, ternary, and quaternary inorganic compounds from the Materials Project
     database snapshot (mp_nostruct_20181018.json.gz, 83,989 entries).
   - Higher-order formulas (> 4 elements) are filtered out as in Zhou et al.
2. Atom-Environment Extraction:
   - For each valid stoichiometric compound formula (e.g. Bi2Se3), atom-environment pairs
     are generated for every constituent element.
   - For target atom A with count c and remaining composition R, the environment is formatted
     as (c)R (e.g. Target Bi -> (2)Se3; Target Se -> (3)Bi2).
3. Vocabulary & Filtering:
   - Symbol frequency is counted across all pairs.
   - Common symbols are selected with count >= 1% of the maximum count (yields 79 elements, Z=1..92).
   - This exact threshold matches Zhou et al. Section 'Data preprocessing'.
4. Co-occurrence Matrix & Normalization:
   - Atom-environment matrix X is built of size N x M (N=79, M=83,664 environments).
   - Row-wise L2 normalization (p=2) is applied:
         X_{i,j} = X_{i,j} / sqrt(sum_j X_{i,j}^2)
     as specified in Zhou et al. 'Model-free methods'.
5. Truncated Singular Value Decomposition (SVD):
   - X = U D V^T with d=20 leading singular dimensions.
   - Fixed random_state=42 for exact determinism.
   - Atom feature representations F = U D (size N x 20).
6. Similarity Metric:
   - Cosine similarity between row vectors of F:
         S_comp(e_t, e_c) = (f_t . f_c) / (||f_t|| * ||f_c||)
   - Excludes target element itself (e_c != e_t).
   - Returns Top-K ranked candidates with similarity scores.
"""

import os
import gzip
import json
import time
from collections import Counter
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import svds
import pymatgen.core as mg


class Atom2VecEngine:
    def __init__(
        self,
        raw_mp_path: str = os.path.join("data", "raw", "mp_nostruct_20181018.json.gz"),
        cache_embedding_path: str = os.path.join("data", "processed", "atom2vec_embeddings_d20.npz"),
        embedding_dim: int = 20,
        random_seed: int = 42
    ):
        self.raw_mp_path = raw_mp_path
        self.cache_embedding_path = cache_embedding_path
        self.embedding_dim = embedding_dim
        self.random_seed = random_seed
        
        self.common_symbols: List[str] = []
        self.atom2idx: Dict[str, int] = {}
        self.F_norm: Optional[np.ndarray] = None
        
        self._load_or_train()
        
    def _load_or_train(self):
        """Load cached embeddings if present, otherwise train from the MP dataset."""
        if os.path.exists(self.cache_embedding_path):
            data = np.load(self.cache_embedding_path, allow_pickle=True)
            self.common_symbols = list(data["common_symbols"])
            self.atom2idx = {s: i for i, s in enumerate(self.common_symbols)}
            self.F_norm = data["F_norm"]
        else:
            self._train_from_corpus()
            
    def _train_from_corpus(self):
        """Train Atom2Vec representation matrix via SVD on MP inorganic compounds."""
        if not os.path.exists(self.raw_mp_path):
            raise FileNotFoundError(f"Materials Project raw dataset not found at: {self.raw_mp_path}")
            
        with gzip.open(self.raw_mp_path, "rt", encoding="utf-8") as f:
            raw = json.load(f)
            
        df = pd.DataFrame(data=raw["data"], index=raw["index"], columns=raw["columns"])
        
        symbol_counter = Counter()
        compound_pairs = []
        
        for formula in df["formula"]:
            try:
                comp = mg.Composition(formula)
                elements = comp.elements
                n_el = len(elements)
                if 2 <= n_el <= 4:
                    red = comp.reduced_composition
                    items = []
                    valid = True
                    for el, amt in red.items():
                        if amt.is_integer() or abs(amt - round(amt)) < 1e-4:
                            items.append((str(el), int(round(amt))))
                        else:
                            valid = False
                            break
                    if not valid:
                        continue
                    items.sort(key=lambda x: x[0])
                    for target_el, count in items:
                        symbol_counter[target_el] += 1
                        env_parts = [f"{el}{amt}" for el, amt in items if el != target_el]
                        env_str = f"({count})" + "".join(env_parts)
                        compound_pairs.append((target_el, env_str))
            except Exception:
                continue
                
        max_count = max(symbol_counter.values())
        threshold = 0.01 * max_count
        self.common_symbols = sorted([s for s, c in symbol_counter.items() if c >= threshold])
        self.atom2idx = {s: i for i, s in enumerate(self.common_symbols)}
        
        env_counter = Counter()
        for target_el, env_str in compound_pairs:
            if target_el in self.atom2idx:
                env_counter[env_str] += 1
                
        env2idx = {env: j for j, env in enumerate(env_counter.keys())}
        N = len(self.common_symbols)
        M = len(env2idx)
        
        counts = {}
        for target_el, env_str in compound_pairs:
            if target_el in self.atom2idx and env_str in env2idx:
                pair = (self.atom2idx[target_el], env2idx[env_str])
                counts[pair] = counts.get(pair, 0) + 1
                
        row_ind = [k[0] for k in counts.keys()]
        col_ind = [k[1] for k in counts.keys()]
        data_vals = [float(v) for v in counts.values()]
        X = csr_matrix((data_vals, (row_ind, col_ind)), shape=(N, M), dtype=np.float64)
        
        # Row L2 normalization (p=2)
        row_norms = np.sqrt(np.array(X.power(2).sum(axis=1)).flatten())
        row_norms[row_norms == 0] = 1.0
        inv_diag = diags(1.0 / row_norms)
        X_norm = inv_diag.dot(X)
        
        # Truncated SVD
        U, S, Vt = svds(X_norm, k=self.embedding_dim, random_state=self.random_seed)
        idx_sort = np.argsort(S)[::-1]
        U = U[:, idx_sort]
        S = S[idx_sort]
        F = U * S
        
        # Row normalize for cosine similarity
        self.F_norm = F / np.linalg.norm(F, axis=1, keepdims=True)
        
        # Save cache
        os.makedirs(os.path.dirname(self.cache_embedding_path), exist_ok=True)
        np.savez_compressed(
            self.cache_embedding_path,
            common_symbols=np.array(self.common_symbols),
            F_norm=self.F_norm,
            singular_values=S
        )

    def compute_similarity(self, target_element: str, candidate_element: str) -> float:
        """Compute cosine similarity between Atom2Vec embeddings."""
        if target_element not in self.atom2idx:
            raise ValueError(f"Target element '{target_element}' is not in Atom2Vec vocabulary.")
        if candidate_element not in self.atom2idx:
            raise ValueError(f"Candidate element '{candidate_element}' is not in Atom2Vec vocabulary.")
            
        i = self.atom2idx[target_element]
        j = self.atom2idx[candidate_element]
        return float(np.dot(self.F_norm[i], self.F_norm[j]))

    def get_top_k(self, target_element: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Generate Top-K candidate elements based on Atom2Vec cosine similarity.
        
        Output schema per record:
        - method: 'Atom2Vec'
        - target_element: str
        - rank: int (1..k)
        - candidate_element: str
        - similarity_score: float
        """
        if target_element not in self.atom2idx:
            raise ValueError(f"Target element '{target_element}' not in Atom2Vec vocabulary.")
            
        i = self.atom2idx[target_element]
        sims = self.F_norm.dot(self.F_norm[i])
        
        scored_candidates = []
        for idx, cand in enumerate(self.common_symbols):
            if cand == target_element:
                continue  # Target element strictly excluded
            scored_candidates.append((cand, float(sims[idx])))
            
        # Sort by similarity descending; tie break deterministically by symbol
        scored_candidates.sort(key=lambda x: (-x[1], x[0]))
        
        results = []
        for rank, (cand, sim) in enumerate(scored_candidates[:k], start=1):
            results.append({
                "method": "Atom2Vec",
                "target_element": target_element,
                "rank": rank,
                "candidate_element": cand,
                "similarity_score": round(float(sim), 6)
            })
            
        return results
