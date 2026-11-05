# Primary-source review ledger

This is a bounded curation pass, not completion of a representative benchmark.
Full text does not automatically establish every original assertion. Source identity,
material form, phase, site and concentration must match the particular claim.

| Source | Access/review status | DOI (candidate unless verified) | Decision |
|---|---|---|---|
| MoW_atomic | blocked | 10.1038/ncomms2351 | Local HTML is a client challenge, not the paper. No full-text credit. |
| MoW_Chen | metadata_only | 10.1021/nn401420h | Metadata/abstract screening only; no quantitative admission. |
| MoSe_Gong | metadata_only | 10.1021/nl4032296 | Metadata/abstract screening only; no quantitative admission. |
| Re_MoS2 | full_text | 10.1002/adma.201304985 | Source identity and scoped passages reviewed; source values are not MATRA predictions. |
| Nb_STO | full_text | 10.1038/s41598-021-03199-7 | Acquisition candidate DOI was wrong and rejected. Correct DOI read from article header, line 44. No retrospective alteration of acquisition log. |
| Nb_STO_polar | blocked | 10.1038/s41535-022-00524-9 | Local HTML is a client challenge, not the paper. No full-text credit. |
| Sn_Ga_XAS | unavailable | unverified | Repository retrieval returned HTTP 429; no local paper evidence. |
| Si_Ga_Villora | metadata_only | 10.1063/1.2919728 | Metadata/abstract screening only; no quantitative admission. |
| Mg_GaN_Amano | metadata_only | 10.1143/JJAP.28.L2112 | Metadata/abstract screening only; no quantitative admission. |
| Al_Ga_Peelaers | acquired_unreviewed | 10.1063/1.5036991 | PDF acquired; detailed claim and publication-version review pending. Not admitted. |
| CsPbSn | metadata_only | 10.1039/D4MA00034J | Metadata/abstract screening only; no quantitative admission. |
| BiTeSe | metadata_only | 10.34133/2020/4361703 | Metadata/abstract screening only; no quantitative admission. |
| BaSr_neutron | acquired_unreviewed | 10.48550/arXiv.2007.00972 | PDF acquired; detailed claim and publication-version review pending. Not admitted. |
| GaAl_HSE | full_text | 10.1103/PhysRevApplied.10.011003 | Source identity and scoped passages reviewed; source values are not MATRA predictions. |

Three detailed source cards are stored in data/benchmark/v2_1_0/primary_evidence_reviewed.json,
including local extraction line ranges, exact anchor fragments, document/text SHA-256 hashes,
concentration conventions and limitations. These are single-reviewer decisions; independent
materials-expert adjudication is pending. The initial primary_evidence.json is retained as
an intermediate build; use primary_evidence_reviewed.json for the final reviewed release.

## What the three sources establish

- Wang et al., DOI 10.1103/PhysRevApplied.10.011003, author manuscript arXiv:1806.03360v2:
  a computed monoclinic AlGaO3 arrangement at cation fraction x=0.5, with octahedral Al
  and tetrahedral Ga. This is a computational reference, not experimental validation or
  evidence of preserved band gap. Figure 1 and the abstract were checked visually.
- Lin et al., DOI 10.1002/adma.201304985: atomic microscopy identifies Re on Mo sites
  in single-layer MoS2 and also observes Re adatoms. The reported concentration convention
  is retained. Bulk space-group/Wyckoff assumptions are not transferred to this monolayer.
  Figure 1 was inspected. Electrical activation is not independently established here.
- Zhang et al., DOI 10.1038/s41598-021-03199-7: Nb-doped SrTiO3 single crystals have
  explicitly defined weight-percent concentrations and nominal formulas. Selected passages
  do not establish direct occupancy refinement and a fully specified phase/temperature case.
  The acquisition DOI candidate was incorrect; article-header DOI corrected in the reviewed
  record while retaining the original acquisition history.

## Remaining scientific work

All 23 broad legacy assertions remain withheld in frozen v2.0.0. The new computed case
does not certify the broader old Ga–Al range. Other acquired papers require complete
claim review; sources available only as metadata need primary passages. Add independent
expert review, broader held-out host/site cases and documented counterexamples before
claiming benchmark representativeness. Absence of evidence is not a negative label.
