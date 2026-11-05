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
import hashlib
import logging
from pathlib import Path
import tempfile
import zipfile
from collections import Counter
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import svds
import pymatgen.core as mg
from src.similarity_validation import PROJECT_ROOT, cosine, real_matrix, require_supported, support_status, validate_integer, validate_symbol

LOGGER = logging.getLogger(__name__)
ALGORITHM = 'atom-environment-row-l2-svd-v1'


class Atom2VecEngine:
    def __init__(
        self,
        raw_mp_path=PROJECT_ROOT / 'data/raw/mp_nostruct_20181018.json.gz',
        cache_embedding_path=PROJECT_ROOT / 'data/processed/atom2vec_embeddings_d20.npz',
        embedding_dim: int = 20,
        random_seed: int = 42,
        require_cache_metadata: bool = False,
    ):
        self.raw_mp_path = Path(raw_mp_path)
        self.cache_embedding_path = Path(cache_embedding_path)
        self.embedding_dim = validate_integer(embedding_dim, 'embedding_dim', minimum=1)
        self.random_seed = validate_integer(random_seed, 'random_seed', maximum=2**32-1)
        if type(require_cache_metadata) is not bool:
            raise TypeError('require_cache_metadata must be boolean')
        self.require_cache_metadata = require_cache_metadata
        self.cache_info = {}
        self.training_stats = None
        
        self.common_symbols: List[str] = []
        self.atom2idx: Dict[str, int] = {}
        self.F_norm: Optional[np.ndarray] = None
        
        self._load_or_train()
        
    def _load_or_train(self):
        """Load cached embeddings if present, otherwise train from the MP dataset."""
        if self.cache_embedding_path.exists():
            if not self.cache_embedding_path.is_file():
                raise ValueError('Embedding cache must be a file')
            try:
                with np.load(self.cache_embedding_path, allow_pickle=False) as data:
                    symbols, features, singular = data['common_symbols'], data['F_norm'], data['singular_values']
                    self._validate_arrays(symbols, features, singular)
                    if 'metadata_json' in data:
                        encoded = data['metadata_json']
                        if encoded.shape != () or encoded.dtype.kind != 'U':
                            raise ValueError('Cache metadata must be a scalar Unicode JSON string')
                        metadata = json.loads(str(encoded.item()))
                        if not isinstance(metadata, dict) or type(metadata.get('schema_version')) is not int or metadata['schema_version'] != 1 or metadata.get('algorithm') != ALGORITHM:
                            raise ValueError('Unsupported cache metadata schema/algorithm')
                        if type(metadata.get('embedding_dim')) is not int or metadata['embedding_dim'] != self.embedding_dim:
                            raise ValueError('Cached embedding configuration mismatch')
                        if type(metadata.get('random_seed')) is not int or metadata['random_seed'] != self.random_seed:
                            raise ValueError('Cached random seed configuration mismatch')
                        checksum = metadata.get('corpus_sha256')
                        if not isinstance(checksum, str) or len(checksum) != 64 or any(c not in '0123456789abcdef' for c in checksum):
                            raise ValueError('Invalid cached corpus checksum')
                        corpus_verified = False
                        if self.raw_mp_path.is_file():
                            if hashlib.sha256(self.raw_mp_path.read_bytes()).hexdigest() != checksum:
                                raise ValueError('Cached corpus checksum does not match supplied corpus')
                            corpus_verified = True
                        self.cache_info = {**metadata, 'metadata_present': True, 'corpus_verified': corpus_verified}
                    else:
                        if self.require_cache_metadata:
                            raise ValueError('Legacy cache has no training metadata; strict cache policy rejects it')
                        if self.random_seed != 42:
                            raise ValueError('Legacy cache cannot verify a non-default random seed; use a metadata-bearing cache or a new cache path')
                        self.cache_info = {'metadata_present': False, 'corpus_verified': False,
                                           'requested_seed_verified': False, 'note': 'Legacy cache: shape/norm checked; training seed and corpus provenance unavailable'}
                        LOGGER.info(self.cache_info['note'])
                    self.common_symbols = symbols.tolist()
                    self.atom2idx = {s: i for i, s in enumerate(self.common_symbols)}
                    self.F_norm = features.astype(np.float64, copy=True)
            except (KeyError, ValueError, TypeError, OSError, EOFError, zipfile.BadZipFile) as exc:
                raise ValueError(f'Invalid embedding cache {self.cache_embedding_path}: {exc}') from exc
        else:
            self._train_from_corpus()

    def _validate_arrays(self, symbols, features, singular):
        if symbols.ndim != 1 or symbols.dtype.kind != 'U' or len(symbols) < 2:
            raise ValueError('Cache vocabulary must contain at least two Unicode element symbols')
        for symbol in symbols.tolist():
            validate_symbol(symbol, 'cache element')
        if len(set(symbols.tolist())) != len(symbols):
            raise ValueError('Duplicate cache element symbols')
        features = real_matrix(features, 'Embeddings')
        singular = real_matrix(singular, 'Singular values')
        if features.shape != (len(symbols), self.embedding_dim):
            raise ValueError('Embedding rows/dimension do not match vocabulary/requested dimension')
        if singular.shape != (self.embedding_dim,) or (singular < 0).any() or (np.diff(singular) > 0).any():
            raise ValueError('Singular values must be nonnegative, descending and dimension-matched')
        with np.errstate(over='ignore', invalid='ignore'):
            norms = np.linalg.norm(features, axis=1)
        if not np.isfinite(norms).all() or not np.allclose(norms, 1.0, rtol=0, atol=1e-8):
            raise ValueError('Cached vectors must be nonzero and L2-normalized within 1e-8')
            
    def _train_from_corpus(self):
        """Train Atom2Vec representation matrix via SVD on MP inorganic compounds."""
        if not self.raw_mp_path.is_file():
            raise FileNotFoundError(f"Materials Project raw dataset not found at: {self.raw_mp_path}")
            
        # Decode one byte snapshot so the metadata hash describes exactly the trained corpus.
        corpus_bytes = self.raw_mp_path.read_bytes()
        corpus_checksum = hashlib.sha256(corpus_bytes).hexdigest()
        try:
            raw = json.loads(gzip.decompress(corpus_bytes).decode('utf-8'))
        except (OSError, ValueError, EOFError) as exc:
            raise ValueError(f'Invalid gzip/JSON corpus: {self.raw_mp_path}') from exc
        del corpus_bytes
            
        if not isinstance(raw, dict) or not all(k in raw for k in ('data', 'index', 'columns')):
            raise ValueError('Corpus must have data, index and columns fields')
        try:
            df = pd.DataFrame(data=raw['data'], index=raw['index'], columns=raw['columns'])
        except (ValueError, TypeError) as exc:
            raise ValueError('Malformed corpus table') from exc
        if list(df.columns).count('formula') != 1:
            raise ValueError('Corpus requires exactly one formula column')
        
        symbol_counter = Counter()
        compound_pairs = []
        valid_formulas = 0
        
        for formula in df["formula"]:
            if not isinstance(formula, str) or not formula:
                continue
            try:
                comp = mg.Composition(formula)
                elements = comp.elements
                n_el = len(elements)
                if 2 <= n_el <= 4:
                    red = comp.reduced_composition
                    items = []
                    valid = True
                    for el, amt in red.items():
                        validate_symbol(str(el), 'corpus element')
                        if np.isfinite(amt) and amt > 0 and (amt.is_integer() or abs(amt - round(amt)) < 1e-4):
                            items.append((str(el), int(round(amt))))
                        else:
                            valid = False
                            break
                    if not valid:
                        continue
                    valid_formulas += 1
                    items.sort(key=lambda x: x[0])
                    for target_el, count in items:
                        symbol_counter[target_el] += 1
                        env_parts = [f"{el}{amt}" for el, amt in items if el != target_el]
                        env_str = f"({count})" + "".join(env_parts)
                        compound_pairs.append((target_el, env_str))
            except (ValueError, TypeError):
                continue
        self.training_stats = {'input_rows': len(df), 'valid_binary_to_quaternary_rows': valid_formulas,
                               'skipped_rows': len(df)-valid_formulas}
        LOGGER.info('Atom2Vec corpus preprocessing: %s', self.training_stats)
        if not symbol_counter:
            raise ValueError('Corpus has no supported binary-to-quaternary integer compositions')
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
        if self.embedding_dim >= min(N, M):
            raise ValueError(f'embedding_dim must be below min(vocabulary, environments)={min(N, M)} for sparse SVD')
        
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
        norms = np.linalg.norm(F, axis=1, keepdims=True)
        if not np.isfinite(norms).all() or (norms <= 0).any():
            raise ValueError('SVD produced zero or nonfinite embedding vectors')
        self.F_norm = F / norms
        self._validate_arrays(np.array(self.common_symbols), self.F_norm, S)
        metadata = {'schema_version': 1, 'algorithm': ALGORITHM,
                    'embedding_dim': self.embedding_dim, 'random_seed': self.random_seed,
                    'corpus_sha256': corpus_checksum}
        self.cache_embedding_path.parent.mkdir(parents=True, exist_ok=True)
        # Publish only a completed archive. Windows rename refuses an existing destination;
        # POSIX uses an exclusive hard link because POSIX rename would overwrite a file.
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(dir=self.cache_embedding_path.parent, prefix='.atom2vec-', suffix='.npz', delete=False) as stream:
                temp_path = Path(stream.name)
                np.savez_compressed(stream, common_symbols=np.array(self.common_symbols), F_norm=self.F_norm,
                                    singular_values=S, metadata_json=np.array(json.dumps(metadata, sort_keys=True)))
            if os.name == 'nt':
                os.rename(temp_path, self.cache_embedding_path)
            else:
                os.link(temp_path, self.cache_embedding_path)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
        self.cache_info = {**metadata, 'metadata_present': True, 'corpus_verified': True}

    def compute_similarity(self, target_element: str, candidate_element: str) -> float:
        """Compute cosine similarity between Atom2Vec embeddings."""
        require_supported(target_element, self.atom2idx, 'Atom2Vec')
        require_supported(candidate_element, self.atom2idx, 'Atom2Vec', 'candidate')
            
        i = self.atom2idx[target_element]
        j = self.atom2idx[candidate_element]
        return cosine(np.dot(self.F_norm[i], self.F_norm[j]))

    def get_support_status(self, element):
        return support_status(element, self.atom2idx, self.common_symbols, 'Atom2Vec')

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
        k = validate_integer(k, 'k')
        require_supported(target_element, self.atom2idx, 'Atom2Vec')
            
        i = self.atom2idx[target_element]
        sims = self.F_norm.dot(self.F_norm[i])
        if not np.isfinite(sims).all():
            raise ValueError('Nonfinite embedding similarity scores')
        sims = np.clip(sims, -1.0, 1.0)
        
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
