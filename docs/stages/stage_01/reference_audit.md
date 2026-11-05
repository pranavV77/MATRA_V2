# Stage 1 reference and convention audit

Status: partial source verification, not certification of the benchmark. Sources checked 5 November 2026. Original data and labels remain untouched.

## Confirmed source mismatch: BM-S04

The benchmark records `Szot et al., Nature Mater. 1, 102 (2002)` and DOI `10.1038/nmat737` for Nb donor doping in SrTiO3. The publisher page for that DOI identifies Philip S. Salmon, **Order within disorder**, Nature Materials 1, 87-88 (2002), about glass structure. The DOI does not support the recorded doping claim.

Primary publisher source: https://www.nature.com/articles/nmat737

Action: quarantine the citation from evidence-backed claims until the correct primary source is identified and its actual supported conditions are extracted. This finding does not show that Nb doping itself is false. BM-S04 is already excluded from legacy primary metrics, so identifying this issue does not change their numerical reproduction.

## Evidence class needs review: BM-P01

The cited Peelaers paper, DOI `10.1063/1.5036991`, is **Structural and electronic properties of Ga2O3-Al2O3 alloys**. The author-hosted publication record confirms the title. The author manuscript states that the study uses hybrid DFT to assess alloy stability/electronic properties. It discusses experimental context but is not itself blanket direct experimental evidence for every Al/In site-specific claim listed in BM-P01. The benchmark also cites another source whose detailed claim coverage has not been independently audited here.

Sources:

- https://labs.materials.ucsb.edu/speck/james/publications/3226
- https://www.osti.gov/pages/servlets/purl/1497947 (author proof manuscript; final published version and erratum need checking during full curation)

Action: extract exact per-substituent evidence and concentration/site limits; distinguish computational support from primary experimental synthesis. Do not relabel or delete the original case in an audit-only stage.

## Local installed-library conventions

The installed Mendeleev 1.2.0 `Element` class docstring says dipole polarizability is in atomic units. The dataset builder directly copies the numeric value without a conversion. The existing report and test comments label those values Angstrom cubed. This is a unit-label mismatch. A consistent positive multiplicative conversion cancels in per-feature Z-score standardization, so this observation alone does not imply different property rankings. Scientific presentation still requires correction.

The metadata describes PN range 1-103 and division by 103. Actual retained values range 1-117, and the largest `pn_normalized` is 1.1359223300970873. The current PN engine uses integer `mendeleev_number`, not `pn_normalized`; property similarity uses its own 14 features. Do not imply that this unused-column inconsistency invalidates the reproduced ranking scores. Validate the authoritative ordering independently in the dataset stage.

Fr thermal conductivity is assigned 15.0 in source. A comment describing extrapolation is not an executed derivation. Its scientific justification remains unverified. Density/molar-volume phase conventions and complete feature-level provenance also remain to audit.

## Boundaries

- All 16 case entries were inventoried, but only the targeted checks above were independently examined in this stage.
- ACS publisher retrieval for the supplied Mo/W and Cs/Pb/Sn DOIs was inaccessible; they are **not verified**, not declared incorrect.
- JSON/schema tests verify field presence and label consistency, not literature truth.
- Duplicate formulas in a structure/property corpus can represent polymorphs or different database entries. Their presence is not automatically corruption. Their effect on compositional co-occurrence weighting needs a documented policy.
- No new experimentally valid substitution, dopant, band gap, stability, or novel material has been established by this audit.
