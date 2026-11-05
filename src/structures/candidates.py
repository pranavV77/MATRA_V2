"""Generate bounded single-site/orbit substitutions; no energetic acceptance."""
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import uuid

import numpy as np
from pymatgen.core import Species
from pymatgen.io.cif import CifWriter

from src.fusion.fusion_engine import FusionEngine
from src.similarity_validation import PROJECT_ROOT, validate_integer, validate_symbol
from src.structures.hosts import analyze_sites, diagonal_supercell, finite_number, geometry_check, structure_fingerprint


def formal_charge_screen(host, indices, candidate, candidate_oxidation=None):
    """Only use explicitly decorated host states and explicitly requested candidate state."""
    known_host = all(hasattr(s.specie, 'oxi_state') for s in host)
    source_states = [getattr(host[i].specie, 'oxi_state', None) for i in indices]
    candidate_oxidation = (finite_number(candidate_oxidation, 'candidate oxidation state', -8, 8)
                           if candidate_oxidation is not None else None)
    delta = (math.fsum(candidate_oxidation-float(q) for q in source_states)
             if candidate_oxidation is not None and all(q is not None for q in source_states) else None)
    host_charge = float(math.fsum(s.specie.oxi_state for s in host)) if known_host else None
    assumed_charge = host_charge+delta if host_charge is not None and delta is not None else None
    return {'status': 'unknown' if delta is None else 'isovalent_under_supplied_states' if abs(delta)<1e-8 else 'formal_charge_change_requires_assessment',
            'target_states': [float(q) if q is not None else None for q in source_states],
            'candidate_state': candidate_oxidation, 'formal_charge_delta_e': delta,
            'host_formal_charge_e': host_charge, 'trial_formal_charge_e': assumed_charge,
            'compensation_needed_under_assumptions': abs(assumed_charge)>1e-8 if assumed_charge is not None else None,
            'candidate_common_oxidation_states': list(Species(candidate, 0).element.common_oxidation_states),
            'note': 'Formal bookkeeping only. States are supplied assumptions; no charge-state, defect, carrier or compatibility prediction.'}


class CandidateGenerator:
    def __init__(self, fusion=None):
        self.fusion = fusion or FusionEngine()

    def generate(self, structure, target, site_index, k=5, supercell=(1,1,1), mode='single_site',
                 candidate_symbols=None, candidate_oxidation_states=None, symprec=0.01):
        validate_symbol(target, 'target')
        site_index = validate_integer(site_index, 'site_index')
        k = validate_integer(k, 'k', minimum=1, maximum=20)
        if mode not in ('single_site', 'symmetry_orbit'):
            raise ValueError('mode must be single_site or symmetry_orbit')
        host = diagonal_supercell(structure, supercell)
        analysis = analyze_sites(host, symprec=symprec)
        if site_index >= len(host) or host[site_index].specie.symbol != target:
            raise ValueError('Selected index must identify the target element in the expanded cell')
        orbit = analysis['orbits'][analysis['sites'][site_index]['orbit_id']]
        indices = [site_index] if mode == 'single_site' else orbit['indices']
        if candidate_symbols is not None:
            if not isinstance(candidate_symbols, (list,tuple)) or not 1 <= len(candidate_symbols) <= 20:
                raise ValueError('Explicit candidates must contain 1..20 unique element symbols')
            for s in candidate_symbols: validate_symbol(s, 'candidate')
            if len(set(candidate_symbols)) != len(candidate_symbols) or target in candidate_symbols:
                raise ValueError('Candidates must be unique and differ from the target')
            if any(s not in self.fusion.common_candidates for s in candidate_symbols):
                raise ValueError('Candidate lacks the three similarity representations')
        states = {} if candidate_oxidation_states is None else candidate_oxidation_states
        if not isinstance(states, dict):
            raise TypeError('candidate_oxidation_states must be a symbol-to-state object')
        for symbol,value in states.items():
            validate_symbol(symbol)
            finite_number(value, 'candidate oxidation state', -8, 8)
        ranking = self.fusion.recommend(target, k=len(self.fusion.common_candidates))
        chosen = [r for r in ranking['rankings'] if candidate_symbols is None or r['candidate_element'] in candidate_symbols][:k]
        if set(states)-{r['candidate_element'] for r in chosen}:
            raise ValueError('Oxidation states must refer only to returned candidates; increase k or revise candidates')
        total_target = sum(s.specie.symbol == target for s in host)
        configurations = []
        for row in chosen:
            candidate = row['candidate_element']
            charge = formal_charge_screen(host, indices, candidate, states.get(candidate))
            trial = host.copy()
            # Strip unassessed host magnetic moments/forces/labels on replaced sites.
            for i in indices:
                replacement = Species(candidate, states[candidate]) if candidate in states else candidate
                trial.replace(i, replacement, properties={}, label=candidate)
            # Symmetry-expanded CIFs can repeat asymmetric-unit labels. Trial
            # labels identify explicit ordered sites uniquely; source labels stay in host analysis.
            for j, site in enumerate(trial):
                site.label = f'{site.specie.symbol}{j}'
            checked = geometry_check(trial)
            preserved = bool(np.array_equal(host.lattice.matrix, trial.lattice.matrix) and np.array_equal(host.frac_coords, trial.frac_coords))
            if not preserved or len(trial) != len(host):
                raise RuntimeError('Substitution must preserve initial lattice, coordinates and site count')
            configurations.append({'candidate_element': candidate, 'elemental_rank': row['rank'],
                                   'fusion_score': row['fusion_score'], 'score_contributions': row['contributions'],
                                   'replaced_indices': list(indices), 'replacement_count': len(indices),
                                   'target_sublattice_fraction': len(indices)/total_target,
                                   'all_atoms_replaced_fraction': len(indices)/len(host),
                                   'selected_orbit_fraction': len(indices)/len(orbit['indices']),
                                   'target_sublattice_denominator': total_target,
                                   'trial_formula': trial.composition.element_composition.formula,
                                   'candidate_already_present_in_host': candidate in {s.specie.symbol for s in host},
                                   'formal_charge_screen': charge, 'geometry': checked,
                                   'coordinates_and_lattice_preserved': preserved, 'trial_labels': 'unique element+ordered-index labels',
                                   'structure_sha256': structure_fingerprint(trial), 'structure': trial.as_dict(),
                                   'validation': {'site_identity': 'checked_against_input_geometry', 'structural_relaxation': 'not_run',
                                                  'energy_stability': 'not_run', 'band_gap_preservation': 'not_run', 'doping_activation': 'not_run'}})
        return {'scope': 'unrelaxed_site_specific_substitution_configurations', 'target_element': target,
                'host': analysis, 'supercell': list(supercell), 'selected_site_index_in_expanded_cell': site_index,
                'selected_orbit': orbit, 'mode': mode, 'requested_k': k, 'returned_count': len(configurations),
                'parameters': {'symprec_angstrom': symprec, 'candidate_pool': 'Stage 4 common 79-element pool',
                               'rank_policy': 'unchanged elemental fusion order; no unvalidated site score added'},
                'configurations': configurations,
                'limitations': ['Site-specific configuration is not a validated chemical substitution.',
                                'One arrangement per candidate; other multi-site orderings are not enumerated.',
                                'Selected-site index applies after supercell expansion; inspect expanded site table first.',
                                'Fractions describe this periodic cell; they do not establish dilute-defect behavior.',
                                'Geometry unchanged by construction; passing collision checks is not stability evidence.']}


def export_configurations(result, output_dir=None):
    """Create a fresh bundle with no overwrites; keep JSON states, CIF geometry and hashes."""
    from pymatgen.core import Structure
    parent = Path(output_dir or PROJECT_ROOT/'results/structure_lab/exports').resolve()
    if not parent.is_relative_to(PROJECT_ROOT):
        raise ValueError('Structure exports must remain inside the project')
    parent.mkdir(parents=True, exist_ok=True)
    bundle = parent / ('trial_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ_')+uuid.uuid4().hex[:10])
    bundle.mkdir(exist_ok=False)
    files = []
    import hashlib
    for index,c in enumerate(result['configurations']):
        structure = Structure.from_dict(c['structure'])
        path = bundle / f'{index+1:02d}_{c["candidate_element"]}.cif'
        with path.open('x',encoding='utf-8') as out: out.write(str(CifWriter(structure)))
        files.append({'path': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    archive = {'exported_at_utc': datetime.now(timezone.utc).isoformat(), 'result': result, 'cif_files': files,
               'cif_note': 'Unrelaxed geometry. Use accompanying JSON for assumptions, provenance and per-site oxidation metadata.'}
    with (bundle/'record.json').open('x',encoding='utf-8') as out: json.dump(archive,out,indent=2,allow_nan=False)
    return {'saved': True, 'directory': str(bundle), 'record_path': str(bundle/'record.json'), 'configurations': len(files)}
