"""Shared contracts for independent similarity signals; no chemical validation."""
from numbers import Integral
from pathlib import Path
import numpy as np
import pandas as pd
from pymatgen.core import Element

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MASTER = PROJECT_ROOT / 'data/processed/elements_master.parquet'
NOBLE_GASES = frozenset(('He', 'Ne', 'Ar', 'Kr', 'Xe', 'Rn', 'Og'))


class UnsupportedElementError(ValueError):
    """Canonical element exists but this signal has insufficient data/policy support."""


def validate_symbol(value, role='element'):
    if not isinstance(value, str):
        raise TypeError(f'{role} must be a canonical element symbol string')
    if not Element.is_valid_symbol(value):
        raise ValueError(f'Invalid {role} symbol {value!r}; use a canonical symbol such as Ga')
    return value


def validate_integer(value, name, minimum=0, maximum=None):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral):
        raise TypeError(f'{name} must be an integer, not a boolean')
    value = int(value)
    if value < minimum or (maximum is not None and value > maximum):
        raise ValueError(f'{name} outside permitted range [{minimum}, {maximum}]')
    return value


def require_supported(value, available, method, role='target'):
    validate_symbol(value, role)
    if value not in available:
        raise UnsupportedElementError(f'{method}: recognized {role} {value} has no supported representation; no score was inferred')


def support_status(symbol, available, candidates, method):
    validate_symbol(symbol)
    supported = symbol in available
    eligible = symbol in candidates
    return {'method': method, 'element': symbol, 'recognized': True,
            'target_supported': supported, 'candidate_eligible': eligible,
            'reason': 'available' if eligible else 'candidate_policy_exclusion' if supported else 'representation_unavailable',
            'scientific_substitution_validated': False}


def read_master(path, columns):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f'Master elements table missing or not a file: {path}')
    try:
        frame = pd.read_parquet(path)
    except (ValueError, OSError) as exc:
        raise ValueError(f'Cannot read master table {path}: {exc}') from exc
    missing = set(columns) - set(frame.columns)
    if not frame.columns.is_unique:
        raise ValueError('Duplicate master column names are not allowed')
    if missing:
        raise ValueError(f'Missing master columns: {sorted(missing)}')
    if frame.empty:
        raise ValueError('Master table is empty')
    symbols = frame['symbol'].tolist()
    for symbol in symbols:
        validate_symbol(symbol, 'master element')
    if len(set(symbols)) != len(symbols):
        raise ValueError('Duplicate master element symbols are not allowed')
    group = frame['group_id']
    if not pd.api.types.is_integer_dtype(group) or pd.api.types.is_bool_dtype(group) or group.isna().any() or not group.between(0, 18).all():
        raise ValueError('group_id must contain integer groups 0..18 (0 denotes unassigned f-block group)')
    if any((symbol in NOBLE_GASES) != (grp == 18) for symbol, grp in zip(symbols, group)):
        raise ValueError('Noble-gas identity/group mismatch')
    if 'atomic_number' in frame:
        if not pd.api.types.is_integer_dtype(frame.atomic_number) or pd.api.types.is_bool_dtype(frame.atomic_number):
            raise ValueError('Atomic numbers must be integers')
        if any(z != Element(symbol).Z for symbol, z in zip(symbols, frame.atomic_number)):
            raise ValueError('Atomic number/symbol mismatch')
    return frame


def real_matrix(array, name):
    array = np.asarray(array)
    if array.dtype.kind not in 'iuf' or not np.isfinite(array).all():
        raise ValueError(f'{name} must contain finite real numbers, not booleans, objects or complex values')
    return array.astype(np.float64, copy=False)


def cosine(dot):
    if not np.isfinite(dot):
        raise ValueError('Nonfinite cosine similarity')
    return float(np.clip(dot, -1.0, 1.0))
