"""Analytical demonstration fixtures; parameters are declared choices, not measurements."""
import math
from pymatgen.core import Lattice, Structure

PROTOTYPES = {
    'perovskite': {'name': 'Ideal cubic SrTiO3 prototype', 'formula': 'SrTiO3',
                   'evidence_class': 'analytically_constructed_demonstration',
                   'source_url': 'https://aflow.org/p/AB3C_cP5_221_a_c_b-001/',
                   'prototype_label': 'AB3C_cP5_221_a_c_b-001',
                   'parameters': {'a_angstrom': 3.9}, 'expected_spacegroup': 221,
                   'note': 'Coordinates follow the cubic perovskite topology. a=3.9 is a chosen demonstration length, not an experimental SrTiO3 reference.'},
    'wurtzite': {'name': 'Ideal wurtzite GaN prototype', 'formula': 'GaN',
                 'evidence_class': 'analytically_constructed_demonstration',
                 'source_url': 'https://aflow.org/p/AB_hP4_186_b_b-001/',
                 'prototype_label': 'AB_hP4_186_b_b-001',
                 'parameters': {'a_angstrom': 3.2, 'c_over_a': math.sqrt(8/3), 'u': 0.375},
                 'expected_spacegroup': 186,
                 'note': 'Ideal wurtzite in a translated origin convention. a=3.2, ideal c/a and u are chosen parameters, not measured GaN coordinates.'}}


def prototype(name):
    if not isinstance(name,str) or name not in PROTOTYPES:
        raise ValueError('Unknown prototype; choose perovskite or wurtzite')
    if name == 'perovskite':
        return Structure(Lattice.cubic(3.9), ['Sr2+','Ti4+','O2-','O2-','O2-'],
                         [[0,0,0],[.5,.5,.5],[.5,.5,0],[.5,0,.5],[0,.5,.5]])
    return Structure(Lattice.hexagonal(3.2,3.2*math.sqrt(8/3)), ['Ga3+','Ga3+','N3-','N3-'],
                     [[1/3,2/3,0],[2/3,1/3,.5],[1/3,2/3,.375],[2/3,1/3,.875]])
