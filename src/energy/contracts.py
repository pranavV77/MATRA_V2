"""Shared energy units, request bounds and fail-closed comparison rules."""
import math
from numbers import Real
from src.similarity_validation import validate_integer


def relaxation_settings(relax=False, max_steps=100, fmax=0.05):
    if not isinstance(relax,bool):raise TypeError('relax must be a boolean')
    max_steps=validate_integer(max_steps,'max_steps',minimum=1,maximum=100)
    if isinstance(fmax,bool) or not isinstance(fmax,Real) or not math.isfinite(fmax) or not .01 <= fmax <= .2:
        raise ValueError('fmax must be a finite force threshold in 0.01..0.2 eV/angstrom')
    return {'relax':relax,'max_steps':max_steps,'fmax_ev_per_angstrom':float(fmax),'cell_policy':'fixed_cell','optimizer':'FIRE'}


def reference_status():
    return {'formation_energy_ev_per_atom':None,'energy_above_hull_ev_per_atom':None,
            'thermodynamic_stability':'not_assessed',
            'reason':'Compatible elemental references and complete competing-phase energies have not been supplied.',
            'scientific_accuracy': 'not_established_by_self_consistency_tests'}


def neutral_geometry_from_stage5(structure):
    """Explicit neutral-atom interpretation of generated Stage 5 geometry.

    Stage 5 serializes partial formal oxidation bookkeeping, which pymatgen can
    turn into a nonzero `charge` field. That is not a requested charged-defect
    calculation. Preserve source metadata separately; this new object contains
    only the atomic identities, lattice and positions used by the potential.
    """
    from pymatgen.core import Structure
    return Structure(structure.lattice,[s.specie.symbol for s in structure],structure.frac_coords)


def regression_metrics(predicted,reference):
    if not isinstance(predicted,(list,tuple)) or not isinstance(reference,(list,tuple)) or not predicted or len(predicted)!=len(reference):
        raise ValueError('Matched nonempty prediction/reference sequences required')
    values=list(predicted)+list(reference)
    if any(isinstance(v,bool) or not isinstance(v,Real) or not math.isfinite(v) for v in values):
        raise ValueError('Reference and predicted values must be finite real numbers')
    errors=[float(a-b) for a,b in zip(predicted,reference)]
    return {'n':len(errors),'mae':sum(abs(e) for e in errors)/len(errors),
            'rmse':math.sqrt(sum(e*e for e in errors)/len(errors)),'bias':sum(errors)/len(errors)}


def comparable_energy_difference(first,second):
    """Allow only a common composition and model; no cross-composition energy ranking."""
    for record in (first,second):
        if not isinstance(record,dict) or not {'composition_counts','model_sha256','total_energy_ev'}<=set(record):
            raise ValueError('Complete energy records are required')
        value=record['total_energy_ev']
        if isinstance(value,bool) or not isinstance(value,Real) or not math.isfinite(value):
            raise ValueError('Comparable energies must be finite real numbers')
    if first['composition_counts']!=second['composition_counts']:
        raise ValueError('Raw energies of different compositions cannot rank substitution suitability')
    if first['model_sha256']!=second['model_sha256']:
        raise ValueError('Different model energy conventions cannot be mixed')
    return float(second['total_energy_ev']-first['total_energy_ev'])
