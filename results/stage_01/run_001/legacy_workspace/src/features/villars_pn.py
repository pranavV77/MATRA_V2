"""
Pierre Villars Mendeleev Periodic Number (PN) Scale Module.

References:
    1. Villars, P.; Daams, J.; Shikata, Y.; Rajan, K.; Iwata, S.
       A New Approach to Describe Elemental-Property Parameters.
       Chem. Met. Alloys 2008, 1, 1-23.
    2. Oran, C.; Caputo, R.; Villars, P.; Tekin, A.
       PNcsp+: A Periodic Number-Based Crystal Structure Prediction.
       J. Chem. Theory Comput. 2026, 22, 3761-3771.
    3. Oran, C.; Caputo, R.; Villars, P.; et al.
       Phase Prediction via Crystal Structure Similarity in the Periodic Number Representation.
       Inorg. Chem. 2024, 63, 20521-20532.

Methodological Definition:
    In the Villars Mendeleev Periodic Number representation, elements are ordered
    group-wise from top to bottom and sequentially across the periodic table from left to right.
    Light alkaline-earth elements Be and Mg are positioned directly above Group 12 (Zn, Cd, Hg)
    to reflect structural coordination similarity in condensed phases.
    The enumeration spans 1 to 118 for the entire periodic system.
    This module provides the verified mapping for all Z=1 to 94 elements.
"""

from typing import Dict, Optional

# Verified Mendeleev Periodic Number mapping for elements Z=1 to 94
# Sourced from mendeleev.models.Element.mendeleev_number, which implements
# the Villars Chem. Met. Alloys (2008) / MPDS helical enumeration.
VILLARS_PN_MAPPING: Dict[int, int] = {
    1: 105,   # H
    2: 112,   # He
    3: 1,     # Li
    4: 75,    # Be
    5: 81,    # B
    6: 87,    # C
    7: 93,    # N
    8: 99,    # O
    9: 106,   # F
    10: 113,  # Ne
    11: 2,    # Na
    12: 76,   # Mg
    13: 82,   # Al
    14: 88,   # Si
    15: 94,   # P
    16: 100,  # S
    17: 107,  # Cl
    18: 114,  # Ar
    19: 3,    # K
    20: 7,    # Ca
    21: 11,   # Sc
    22: 43,   # Ti
    23: 47,   # V
    24: 51,   # Cr
    25: 55,   # Mn
    26: 59,   # Fe
    27: 62,   # Co
    28: 65,   # Ni
    29: 68,   # Cu
    30: 77,   # Zn
    31: 83,   # Ga
    32: 89,   # Ge
    33: 95,   # As
    34: 101,  # Se
    35: 108,  # Br
    36: 115,  # Kr
    37: 4,    # Rb
    38: 8,    # Sr
    39: 12,   # Y
    40: 44,   # Zr
    41: 48,   # Nb
    42: 52,   # Mo
    43: 56,   # Tc
    44: 60,   # Ru
    45: 63,   # Rh
    46: 66,   # Pd
    47: 69,   # Ag
    48: 78,   # Cd
    49: 84,   # In
    50: 90,   # Sn
    51: 96,   # Sb
    52: 102,  # Te
    53: 109,  # I
    54: 116,  # Xe
    55: 5,    # Cs
    56: 9,    # Ba
    57: 13,   # La
    58: 14,   # Ce
    59: 15,   # Pr
    60: 16,   # Nd
    61: 17,   # Pm
    62: 18,   # Sm
    63: 19,   # Eu
    64: 20,   # Gd
    65: 21,   # Tb
    66: 22,   # Dy
    67: 23,   # Ho
    68: 24,   # Er
    69: 25,   # Tm
    70: 26,   # Yb
    71: 27,   # Lu
    72: 45,   # Hf
    73: 49,   # Ta
    74: 53,   # W
    75: 57,   # Re
    76: 61,   # Os
    77: 64,   # Ir
    78: 67,   # Pt
    79: 70,   # Au
    80: 79,   # Hg
    81: 85,   # Tl
    82: 91,   # Pb
    83: 97,   # Bi
    84: 103,  # Po
    85: 110,  # At
    86: 117,  # Rn
    87: 6,    # Fr
    88: 10,   # Ra
    89: 28,   # Ac
    90: 29,   # Th
    91: 30,   # Pa
    92: 31,   # U
    93: 32,   # Np
    94: 33,   # Pu
}


def get_villars_pn(atomic_number: int) -> Optional[int]:
    """Retrieve the Pierre Villars Mendeleev Periodic Number for a given atomic number (Z=1..94)."""
    return VILLARS_PN_MAPPING.get(atomic_number)
