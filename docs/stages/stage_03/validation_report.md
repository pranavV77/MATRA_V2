# Validation classification

| Category | Status | Evidence / limit |
|---|---|---|
| Functionality | Verified for tested scope | 320 passing tests; all 15 recorded defect behaviours covered |
| Mathematical consistency | Verified for represented pairs | 22,821 ordered pairs, symmetry/self invariants, hand examples, finite bounded scores |
| Behaviour preservation | Verified | Zero changed Top-10 records for all 261 supported engine-target combinations |
| Local reproducibility | Verified | Fresh full-corpus training and cache reload reproduce ranking geometry in this environment |
| Earlier file preservation | Verified | 226 previous/root files checked; only intended engine/docs/Git-rule changes |
| Source metadata | Partial | New caches record/check lineage; legacy default cache has no embedded training metadata |
| Cross-platform/clean-machine reproducibility | Not yet verified | Existing Windows/Python 3.10.11 only; POSIX branch not executed |
| Substitution/doping scientific validity | Not verified here | Stage 2 benchmark hold remains; no new ground-truth labels |
| Band gap/energy/stability preservation | Not evaluated | No structure/property/DFT module implemented in this stage |

Passing software tests is not proof of successful material substitution. The two narrow
development references do not constitute a representative or independent scientific benchmark.
No classification accuracy/precision/recall or ranking-generalization score is claimed.
