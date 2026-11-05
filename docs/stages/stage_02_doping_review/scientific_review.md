# Doping evidence review: Si, Mg, Nb

No new full-context activation benchmark case is admitted. Existing substitution references
and the v2.2 ledger are unchanged. Source evidence is not a MATRA prediction.

## Mg-GaN: direct site evidence, with a crucial specimen limitation

Wahl et al., DOI 10.1103/PhysRevLett.118.095501, study radioactive 27Mg implanted into
wurtzite GaN. Methods specify stable predoping, probe profiles, fluence and sample treatment.
The authors explicitly state that their actual p-GaN specimens were not electrically
characterized; typical Hall numbers are from similar specimens. Those values cannot establish
activation efficiency for the implanted samples. C-axis alignment alone cannot distinguish
all positions along that axis; off-axis patterns provide the site discrimination. Reported
fit fractions are retained without conversion into calibrated probabilities.

The local archive is a web-tool text extraction, publisher lines 0–396, not a downloaded
PDF. Direct CERN access returned a bot page and the APS download returned 401. The readable
web extraction provided the inspected methods/results. End matter was not fully archived,
and no claim is made that PDF figures were visually verified locally.

Primary source: https://harvest.aps.org/v2/journals/articles/10.1103/PhysRevLett.118.095501/fulltext

## Si-Ga2O3: useful primary lead, full context pending

Iwaya et al., DOI 10.1063/1.3578195, report STM/spectroscopic evidence for substitutional
Si donors in beta-Ga2O3. Full local methods, exact concentration and specific Ga-site assignment
were not obtained. Do not infer an octahedral site from the Sn case. The earlier Villora
electrical-conductivity abstract remains supporting context, not interchangeable specimen data.

Primary source: https://doi.org/10.1063/1.3578195

## Nb-SrTiO3: processing can change incorporation

Jeong et al., DOI 10.1021/nn401101y, contrast bulk substitutional doping with insulating
films containing inferred inactive interstitial Nb. This is an abstract-level lead; full local
sample concentrations, methods and exact matched site/transport evidence are still required.
It is neither a universal negative label for Nb nor a guarantee that every bulk sample activates.
Crossref metadata is archived; the primary abstract was read via web, not treated as full text.

Primary source: https://pubs.acs.org/doi/10.1021/nn401101y

## Quantity table — conventions retained

| Quantity | Relation and values | Unit | Specimen relationship |
|---|---|---|---|
| stable_dopant_number_density | = [2e+19] | cm^-3 | same_experiment |
| radioactive_probe_peak_density | < [300000000000000.0] | cm^-3 | same_experiment |
| implantation_fluence | = [110000000000.0] | cm^-2 | same_experiment |
| hole_number_density | range [1e+17, 2e+17] | cm^-3 | similar_specimens |
| hall_mobility | range [10, 15] | cm^2 V^-1 s^-1 | similar_specimens |
| interstitial_fit_fraction | = [31] | % | same_experiment |
| c_axis_aligned_fit_fraction | = [72] | % | same_experiment |

The 31% interstitial and 72% c-axis-aligned values are the source's fit outputs, not
a normalized 100% population partition or MATRA confidence. Do not apply the previous
fully occupied crystallographic-table sum rule to these fitted channeling components.
No activation fraction was computed from Hall values on similar specimens.

## What is still missing

Matched specimen identity, concentration/profile convention, phase/site characterization and
electrical activation evidence must be traceable together. Full texts for the Si STM and Nb
interstitial papers would improve curation, but access alone does not guarantee a complete
benchmark. Independent expert adjudication and held-out cases remain pending. All 23 broad
legacy assertions remain unknown; the two previously eligible substitution development
references remain the only admitted candidate references.
