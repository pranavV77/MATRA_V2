"""Bounded, explicit host import and periodic geometric site analysis.

Distances use angstrom. Symmetry is geometric, not evidence of phase stability.
No oxidation states are guessed and no imported structure is silently relaxed.
"""
from collections import Counter
from io import StringIO
import hashlib
import math
from numbers import Real
from pathlib import Path
import warnings

import numpy as np
from pymatgen.core import Structure
from pymatgen.io.cif import CifParser
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from src.similarity_validation import PROJECT_ROOT, validate_integer, validate_symbol

MAX_SITES = 256
MAX_CIF_BYTES = 500_000


def finite_number(value, name, low, high):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise TypeError(f'{name} must be a real number')
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'{name} must be finite in [{low}, {high}]')
    return float(value)


def geometry_check(structure):
    """Gross geometric safeguards, deliberately not chemical viability tests."""
    if not isinstance(structure, Structure):
        raise TypeError('A pymatgen Structure is required')
    if not 1 <= len(structure) <= MAX_SITES:
        raise ValueError(f'Ordered host must contain 1..{MAX_SITES} sites')
    if not structure.is_ordered:
        raise ValueError('Partial occupancies/disorder require an explicit ordered model; no occupancy was rounded')
    if tuple(structure.lattice.pbc) != (True, True, True):
        raise ValueError('This stage supports fully periodic structures only')
    lattice = np.asarray(structure.lattice.matrix)
    if not np.isfinite(lattice).all() or not np.isfinite(structure.frac_coords).all():
        raise ValueError('Lattice and coordinates must be finite')
    singular = np.linalg.svd(lattice, compute_uv=False)
    if singular.min() < 1 or singular.max() > 200:
        raise ValueError('Lattice singular lengths must be 1..200 angstrom for bounded local analysis')
    if structure.volume / len(structure) < 0.5:
        raise ValueError('Volume per atom below gross-geometry limit 0.5 angstrom^3')
    for site in structure:
        validate_symbol(site.specie.symbol, 'site element')
        if hasattr(site.specie, 'oxi_state'):
            finite_number(site.specie.oxi_state, 'formal oxidation state', -8, 8)
    distances = structure.distance_matrix.copy()
    np.fill_diagonal(distances, np.inf)
    pair_min = float(distances.min()) if len(structure) > 1 else None
    if pair_min is not None and pair_min < 0.5:
        raise ValueError('Overlapping/near-overlapping periodic sites: separation below 0.5 angstrom')
    return {'gross_geometry_passed': True, 'minimum_distinct_site_distance_angstrom': pair_min,
            'volume_angstrom3': float(structure.volume), 'site_count': len(structure),
            'limits': {'minimum_pair_distance_angstrom': 0.5, 'maximum_sites': MAX_SITES,
                       'lattice_singular_lengths_angstrom': [1, 200]},
            'chemical_validity_established': False, 'relaxed': False}


def structure_fingerprint(structure):
    """Exact ordered geometry/species identity; NOT a crystallographic duplicate matcher."""
    import json
    record = {'lattice': structure.lattice.matrix.tolist(), 'species': [str(s.specie) for s in structure],
              'fractional_coordinates': structure.frac_coords.tolist()}
    return hashlib.sha256(json.dumps(record, sort_keys=True, allow_nan=False).encode()).hexdigest()


def parse_cif(text):
    if not isinstance(text, str):
        raise TypeError('CIF content must be text')
    if not text.strip() or len(text.encode('utf-8')) > MAX_CIF_BYTES:
        raise ValueError('CIF must be nonempty and at most 500000 UTF-8 bytes')
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        try:
            parser = CifParser(StringIO(text), occupancy_tolerance=1, frac_tolerance=0,
                               site_tolerance=1e-5, check_cif=True)
            if len(parser.as_dict()) != 1:
                raise ValueError('Exactly one CIF data block is required; select the desired phase explicitly')
            structures = parser.parse_structures(primitive=False, check_occu=True, on_error='raise')
            if len(structures) != 1:
                raise ValueError('Exactly one structure is required')
            structure = structures[0]
            geometry_check(structure)
        except Exception as exc:
            raise ValueError(f'CIF rejected: {exc}') from exc
    return structure, {'input_sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
                       'input_format': 'CIF', 'parser_warnings': [str(w.message) for w in caught],
                       'ordering_policy': 'ordered only; no occupancy renormalization requested',
                       'primitive_reduction': False, 'coordinate_rationalization': False}


def load_cif(path):
    if '://' in str(path):
        raise ValueError('Remote URLs are not local host paths')
    path = Path(path)
    path = (PROJECT_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_relative_to(PROJECT_ROOT):
        raise ValueError('Host files must be inside C:\\Final Project')
    if path.suffix.lower() != '.cif':
        raise ValueError('Host input must be a .cif file')
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size > MAX_CIF_BYTES:
        raise ValueError('CIF file exceeds 500000 bytes')
    structure, provenance = parse_cif(path.read_text(encoding='utf-8-sig'))
    provenance['path'] = path.relative_to(PROJECT_ROOT).as_posix()
    provenance['file_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    return structure, provenance


def analyze_sites(structure, symprec=0.01, shell_factor=1.15, neighbor_radius=8.0):
    checked = geometry_check(structure)
    symprec = finite_number(symprec, 'symprec (angstrom)', 1e-5, 0.1)
    shell_factor = finite_number(shell_factor, 'shell_factor', 1, 1.5)
    neighbor_radius = finite_number(neighbor_radius, 'neighbor_radius (angstrom)', 1, 8)
    # Work on a copy; never standardize/reorder caller site indices.
    host = structure.copy()
    try:
        analyzer = SpacegroupAnalyzer(host, symprec=symprec, angle_tolerance=5)
        sym = analyzer.get_symmetrized_structure()
        groups = sorted(sym.equivalent_indices, key=lambda g: min(g))
        spacegroup = {'symbol': analyzer.get_space_group_symbol(), 'number': analyzer.get_space_group_number()}
    except Exception as exc:
        raise ValueError(f'Symmetry analysis failed; no fallback site equivalence invented: {exc}') from exc
    all_neighbors = host.get_all_neighbors(neighbor_radius)
    sites = []
    for index, site in enumerate(host):
        neighbors = sorted(all_neighbors[index], key=lambda n: (n.nn_distance, n.index, tuple(n.image)))
        nearest = float(neighbors[0].nn_distance) if neighbors else None
        shell = [n for n in neighbors if n.nn_distance <= nearest*shell_factor+1e-8] if neighbors else []
        group_id = next(i for i,g in enumerate(groups) if index in g)
        sites.append({'index': index, 'element': site.specie.symbol, 'species': str(site.specie), 'input_label': site.label,
                      'fractional_coordinates': site.frac_coords.tolist(), 'orbit_id': group_id,
                      'formal_oxidation_state': float(site.specie.oxi_state) if hasattr(site.specie, 'oxi_state') else None,
                      'nearest_distance_angstrom': nearest, 'nearest_shell_count': len(shell),
                      'nearest_shell_species_counts': dict(Counter(n.specie.symbol for n in shell)),
                      'neighbor_search_complete_for_shell': nearest is not None and nearest*shell_factor <= neighbor_radius,
                      'nearest_shell_definition': 'all periodic images within shell_factor times nearest distance; geometric, not bond assignment'})
    return {'formula': host.composition.element_composition.reduced_formula, 'site_count': len(host),
            'structure_sha256': structure_fingerprint(host), 'lattice_angstrom': host.lattice.matrix.tolist(),
            'spacegroup': spacegroup, 'parameters': {'symprec_angstrom': symprec, 'angle_tolerance_degrees': 5,
                                                   'shell_factor': shell_factor, 'neighbor_radius_angstrom': neighbor_radius},
            'orbits': [{'orbit_id': i, 'representative_index': min(g), 'indices': sorted(g),
                        'multiplicity_in_input_cell': len(g), 'element': host[g[0]].specie.symbol} for i,g in enumerate(groups)],
            'sites': sites, 'geometry': checked, 'site_chemical_suitability': 'not_established'}


def diagonal_supercell(structure, scaling=(1, 1, 1)):
    geometry_check(structure)
    if not isinstance(scaling, (list, tuple)) or len(scaling) != 3:
        raise ValueError('supercell must be three positive integer scale factors')
    factors = [validate_integer(x, 'supercell factor', minimum=1, maximum=4) for x in scaling]
    if math.prod(factors)*len(structure) > MAX_SITES:
        raise ValueError(f'Supercell would exceed {MAX_SITES} sites')
    host = structure.copy()
    host.make_supercell(factors)
    geometry_check(host)
    return host
