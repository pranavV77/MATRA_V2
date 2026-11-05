# MATRA evaluation protocol v1

Date: 5 November 2026. Status: pre-implementation protocol, not a results report.

This protocol defines the experiments and reporting rules for MATRA. No new models have been trained, benchmarks executed, reference cases certified, or performance improvements demonstrated by preparing it. Existing milestone results are retrospective development evidence. Software implementation remains subject to the user's instruction to start.

## 1. Research questions and permitted claims

1. Does combining periodic-number (PN), Atom2Vec, and physical-property similarity retrieve documented substitutes better than individual signals and simple baselines?
2. Does adding host-site information improve recommendations for a specified structure and concentration?
3. Does structural and energetic screening retain promising candidates while reducing unsuitable candidates and computation?
4. Does explicit property assessment improve compliance with a requested band-gap constraint?
5. Can a separately evaluated doping workflow retrieve documented dopants and accurately report the evidence available for their sites and electronic roles?
6. Do explanations faithfully describe the implemented scoring function and reference evidence?
7. Can these operations run reproducibly within the measured hardware and time budget?

A positive answer requires an actual experiment and its uncertainty, population, and limitations. No universal accuracy target is assumed. A successful software test is not evidence of chemical validity. Database presence is not proof of experimental synthesis. A geometrically valid structure is not proof of stability, and a low predicted energy is not proof of synthesis or device performance.

Primary substitution endpoint: macro Recall@5 of documented acceptable substitutes on held-out, site-and-concentration-qualified queries. Primary doping endpoint: separately computed macro Recall@5 of documented dopants satisfying the requested role where that role is known. MRR@10, Hit@1/3/5/10, nDCG@10, coverage, and per-family results accompany these endpoints. If role data are insufficient, doping retrieval is explicitly role-unspecified; it cannot substitute for the role-conditioned endpoint.

Full-pipeline endpoint: reference-confirmed joint constraint success among a predeclared number of recommendations, with evidence coverage and all attempted queries reported. This endpoint is unavailable until sufficient independent structure, stability, and gap references exist. We will not fill it with model self-assessments.

## 2. Evaluation units and label policy

An elemental query is a target element plus a frozen candidate universe. A substitution query is (host ID, polymorph, target site/sublattice, composition or concentration range, environment/conditions, requested constraints). A doping query additionally includes intended donor/acceptor/other role, concentration basis, and charge/activation conditions if available. A structure prediction is one explicit ordered atomic arrangement; multiple arrangements are not automatically independent samples.

Candidate labels are separate fields, not a single success flag:

- `documented_positive`: direct evidence of the stated substitution under recorded conditions.
- `documented_negative`: explicit evidence that a specified criterion fails under recorded conditions. A failed synthesis attempt does not establish universal impossibility.
- `unknown`: evidence is absent or inadequate. Not a negative.
- `conflicting`: credible sources disagree; resolve or report separately.
- `not_applicable`: the question or measurement does not apply.

Also record evidence class: experimental, computational DFT, model prediction, database-derived, or expert judgment. A candidate may be experimentally reported but fail a requested gap window. Keep substitution existence, phase retention, stability, and property success separate.

Do not create false negative labels by selecting random unreported elements. Artificial overlaps and invalid cell matrices are software/geometry test fixtures, not examples of experimentally impossible chemistry. Use ordinal relevance only if source-backed criteria and a grading rubric were frozen before evaluation; similarity score itself cannot define relevance.

Positive-only literature collections support documented-positive retrieval. They do not support ordinary precision, specificity, accuracy, or a complete confusion matrix. Report known-positive yield rather than renaming unlabeled candidates false positives.

## 3. Benchmarks and reference admission

### 3.1 Benchmark register

| ID | Dataset or source | Intended experiment | Admission and limits |
|---|---|---|---|
| B0 | Existing MATRA 94-element table, 79-element embedding cache, raw MP snapshot and metadata | Data checks, coverage, representation diagnostics | Existing artifacts; check hashes, units, imputation and source versions. Not substitution ground truth. The raw formula corpus is not crystal-coordinate data. |
| B1 | Existing 11 primary substitution cases | Baseline regression and development | Already seen during development; never describe as untouched test data. Re-audit every DOI, site, phase, concentration and evidence statement. |
| B2 | New MATRA substitution evidence collection, grouped by host chemistry/family | Primary held-out retrieval and end-to-end evaluation | Curate from primary experimental papers and compatible computational records. Freeze before tuning; all cases provisional until admission audit. Include different targets, sites and families; report actual counts rather than promising a sample size. |
| B3 | New doping evidence collection; existing 5 contexts are development seeds | Separate doping retrieval, site and role assessment | Verify host, substitutional versus interstitial site, role, concentration, activation and conditions. Bulk alloy endpoints are not dilute-dopant labels. |
| B4 | Matbench v0.1: `matbench_mp_e_form`, `matbench_mp_gap`, `matbench_expt_gap` | Property-model benchmarks | Use official task definitions and splits for official comparisons. These are property benchmarks, not direct substitution or doping benchmarks. Verify exact version and counts at ingestion. [S1] |
| B5 | Matbench Discovery / WBM | Structural energy and stability screening | Use official protocols, permitted input structures, train/test and prototype-overlap rules if making official comparisons. A laptop-sized frozen subset is a custom evaluation, not a leaderboard score. [S2] |
| B6 | Materials Project versioned structures, energies, phase diagrams and gaps | Host structures and compatible numerical references | Record IDs, snapshot, method, corrections, competing phases and structure geometry. Check pretrained-model overlap. A single endmember entry cannot validate an entire alloy series. [S3, S4] |
| B7 | JARVIS-DFT, stratified by OptB88vdW, TBmBJ and other explicitly identified methods | External structural/property checks | Keep functionals separate. Check chemical/prototype overlap with development data; cross-database does not automatically mean independent. Do not mix its energies with MP hulls without a justified compatibility procedure. [S5] |
| B8 | Primary defect studies / compatible charged-defect records | Optional defect formation and transition-level assessment | Use matched supercells, charge states, chemical potentials, band-edge convention and finite-size corrections. No universal doping benchmark has yet been established for MATRA. [S6] |
| B9 | CSPBench as used by PNcsp+; DeepOFM evaluation data | Conditional existing-approach comparison | Access, licensing, exact task equivalence and model reproducibility must be verified first. CSP prototype prediction and local-environment recommendation are different tasks; compare only on compatible slices. [S7, S8] |

Matbench/WBM downloads, defect calculations, and new reference extraction have not been performed as part of this protocol. Framework establishment is complete at the specification level; a frozen benchmark release requires the admission work below. Do not claim the new benchmark already exists.

### 3.2 Reference case register

Use these case families to seed curation, not to assert universally valid substitutions:

| Family | Candidate case | What it can test | Required qualification |
|---|---|---|---|
| Group-III oxides | Al/Ga/In substitutions in specified Ga2O3 phases | Site-sensitive alloy recommendation, gap change versus concentration | Distinguish alpha/beta phases, tetrahedral/octahedral sites and measured/DFT concentration ranges. Wang et al. provides HSE alloy calculations, not blanket experimental proof. [S9] |
| Group-III nitrides | Al/In in GaN | Alloy retrieval and property constraints | Phase, strain, concentration and gap measurement type; evidence still requires primary-paper extraction. |
| Layered chalcogenides | W on Mo sites and Se on S sites in MoS2 | Cation versus anion retrieval, dimensionality and coordination | Monolayer versus bulk, polytype, composition, disorder and optical versus electronic gap. |
| Oxide perovskites | Zr/Hf/Sn on Ti sites; Ca/Sr/Ba on A sites | Different sublattices and host-dependent ranking | Distortion, temperature, phase transitions and solubility limits. Do not assume unchanged space group across a series. |
| Halide perovskites | Sn on Pb sites in CsPbI3 | Phase-sensitive and challenging chemistry | Polymorph, temperature, oxidation/processing conditions and gap evidence. |
| Tetradymites | Sb/Bi and Se/Te substitutions | External functional-material transfer | Site preference and composition range; thermoelectric utility is not established by band gap alone. |
| Dilute GaN doping | Mg on Ga sites | Acceptor-role retrieval and activation caveats | Primary experimental activation evidence plus site evidence; incorporation alone is insufficient. Mg_Ga also appears in the defect-analysis documentation as a computational example. [S6] |
| Other dilute cases | Si/Sn in Ga2O3; Nb in SrTiO3; Re in MoS2 | Donor-role and host-dependent assessment | All remain provisional pending verification of the existing references and concentration/site details. |

Before admission, each case needs: source title and DOI/URL; accessible excerpt or exact figure/table/page locator; experimental or computational status; formula and polymorph; structure ID/file hash if relevant; target and substituted site; concentration and denominator; conditions; measured/predicted property and units; uncertainty if reported; exact supported claim; limits; extraction date and reviewer. Keep independent review status explicit. If only one reviewer is available, report that limitation.

Reject or quarantine mismatched DOIs, unsupported broad solubility claims, phase ambiguity, missing concentration for concentration-specific conclusions, duplicated sources/structures, and claims supported only by generated prose. Keep a rejection log. Reference conflicts remain visible.

## 4. Fair splits and comparisons

### 4.1 Leakage controls

1. Separate legacy/development cases, validation data, and final held-out evaluation before tuning. New cases selected after inspecting model rankings must be marked as such; curate reference cases without consulting MATRA ranks where possible.
2. Group all concentrations/configurations of the same host-substitution pair, polymorph variants where closely related, duplicate structures and shared literature series. Specify groups at each experiment. Do not scatter a single alloy series across train and test.
3. Use host-family-held-out outer evaluation for contextual recommendations where enough independent families exist; use target-element-held-out sensitivity analysis to examine memorization in elemental retrieval. Elemental methods cannot acquire host awareness through evaluation alone.
4. Use grouped 5-fold outer splits only when there are at least five viable groups with usable endpoints; otherwise leave-one-family-out or report descriptive case results. Tune only within each outer training partition, using inner grouped validation. If the small sample cannot support tuning, use fixed equal weights and report no tuned-generalization claim. Save actual fold IDs.
5. Use official Matbench splits for official task comparisons; additional composition/prototype-grouped experiments are separately labelled custom robustness tests.
6. Audit embedding corpus membership and pretrained checkpoint training overlap. Withheld labels do not imply withheld compounds. Report confirmed seen, likely seen, unseen under the available audit, and unknown overlap. Frozen pretrained models are not automatically prospectively clean.
7. Database validation can leak the answer. Distinguish full-knowledge lookup utility from held-out prediction. In masked prediction tests, exclude query-answer evidence and directly linked equivalent records from the evidence store; if the API cannot enforce a snapshot/mask, that feature cannot be credited as independent predictive validation.
8. Freeze a final test snapshot. Any subsequent change driven by its results creates a new development iteration; preserve the old score and seek a new test set for a fresh confirmation claim.

### 4.2 Baseline ladder

- Uniform random ranking over the identical candidate universe, repeated with seeds 0 through 99. This provides a chance baseline, not a scientific recommendation.
- A simple chemical baseline: same/common oxidation-state compatibility where known, ionic-radius mismatch at matching coordination where available, then deterministic tie-breaking. Missing values are explicit; never use benchmark answers as rules.
- PN alone, Atom2Vec alone, standardized physical-property cosine alone.
- Equal-weight fusion; validation-tuned fusion only when the data supports its tuning budget.
- Two-signal fusions and one-signal removals.
- Rank-based fusion such as reciprocal rank fusion as a scaling-robust alternative, with any constant tuned on validation only or fixed in advance.
- Context filters, structure scoring and property constraints added one at a time to the same candidate pool.
- Independent DeepOFM comparison on compatible host/site data if reproducible; otherwise state unavailable rather than use the paper's score as a MATRA comparison. PNcsp+ comparisons are prototype-prediction comparisons only on equivalent tasks.
- For property regression: training-set median, simple composition descriptors plus random forest or ridge regression, then CrabNet or an appropriate structure model if feasible. Train/tune on the same allowed data; compare pretrained models separately with overlap disclosure. [S10]
- For gap-change prediction: a no-change baseline predicts candidate gap equals host gap. It has zero predicted change but can fail badly against reference changes; do not count its own prediction as preservation success.
- For energy screening: compare specified MACE/M3GNet checkpoints individually and any declared ensemble, using identical inputs, geometry budgets and compatible references. Do not ensemble by mixing arbitrary absolute energy zeros.
- For explanations: deterministic evidence template versus template plus LLM prose using the same evidence packet; a more fluent explanation is not automatically more faithful.

Report both a common-support paired comparison (same evaluable cases and candidate universe) and intended-scope performance with unsupported queries/failures counted. Freeze the intended-scope denominator independently of methods. Do not silently drop difficult or unsupported elements. Any renormalization of fusion weights for missing signals is a separate configuration.

## 5. Metric dictionary

Unless specified otherwise, calculate per-query metrics then macro-average across queries; also show family-macro summaries and per-case values. For unequal family sizes, query-macro and family-macro results answer different questions. Always print units, sample counts, denominators, exclusions and direction of improvement. Undefined metrics are `null` with a reason, not zero.

Notation: Q queries; C_q frozen candidate universe; P_q verified positives available for the task; R_q,K returned first K unique recommendations; r_q best positive rank; y reference; yhat prediction. Positive-only labels are incomplete observations of chemical reality.

### 5.1 Data and representation checks

| Metric | Calculation and what it measures | Why relevant / good result | Limitations |
|---|---|---|---|
| Data completeness and validity | For each field, missing/expected values and valid/checked values; list units, ranges, source and imputation | Identifies unsupported descriptors; complete provenance and valid supplied values are desirable | Zero missingness achieved by speculation is not good data. Missing values can be scientifically correct. |
| Element/method coverage | Supported elements / all 118 recognized elements; separately supported query-candidate pairs / requested pairs and complete-pipeline queries / attempted queries | Shows where MATRA can operate; higher real coverage is useful | Recognition, similarity coverage, energy-model coverage and demonstrated accuracy are different. Test all element inputs, including graceful abstention. |
| Label/reference coverage | Adjudicated returned candidates / returned candidates; numerical-reference matches / requested predictions | Prevents accuracy on a tiny supported subset from being mistaken for full coverage | Lack of references is not evidence of incorrect chemistry. Report reference availability per method and family. |
| Numerical invariants | Fractions of tested similarities finite, within the declared range, symmetric within tolerance, with expected self-similarity and target exclusion | Detects implementation errors; all declared invariants should pass | These establish software behavior, not usefulness of similarity. Use tolerances and zero-vector rules. |
| Repeatability | Same-input ranking agreement and maximum score difference across repeat runs, seeds or environments as applicable | Identifies unstable representation/ranking behavior; repeat agreement under fixed configuration is desirable | Stable wrong answers are possible. Separate cached inference repeatability from independently retrained embedding stability. |
| Top-K Jaccard | count(R_A intersect R_B) / count(R_A union R_B) per query | Describes agreement and redundancy between signals | Low overlap is not proof of complementary accuracy. Report candidate-universe differences. |
| Ranking stability | Kendall tau-b on identical complete candidate sets under defined perturbations; Top-K Jaccard for truncated lists | Checks sensitivity to SVD seed, missing data, imputed values and feature perturbations | Correct changes in chemistry should change ranks. Score gaps/ties can create large rank changes with tiny score changes. |

Similarity distributions, correlation matrices, PCA/UMAP projections and chemical-group enrichment are diagnostics. They do not establish substitution accuracy. Supervised chemical-group labels can be a secondary representation probe with an explicitly defined taxonomy; there is no single universal elemental-similarity ground truth.

### 5.2 Retrieval and ranked recommendations

| Metric | Calculation and meaning | Why relevant / good result | Limitations |
|---|---|---|---|
| Hit@K | mean_q 1[count(R_q,K intersect P_q) > 0], K=1,3,5,10 | Fraction of queries finding at least one documented acceptable candidate; higher is better | Easy to saturate; ignores remaining positives and false suggestions. |
| Recall@K (primary K=5) | mean_q count(R_q,K intersect P_q) / count(P_q) | Fraction of documented options recovered within researcher's reading budget; higher is better | Recall of known positives, not all physically possible substitutions. P_q empty queries are excluded from this metric with counts. |
| MRR@10 | mean_q (1/r_q if r_q<=10 else 0) | Rewards an early first useful result; higher is better | Does not reward recovering additional positives. Full-list MRR requires complete rankings and is labelled separately. |
| nDCG@10 | DCG=sum_{r=1..10} rel_r/log2(r+1); divide by ideal DCG for the same observed labels | Measures position of multiple positives; higher, up to 1, is better | Use binary relevance by default; unknown labels treated as uncredited, not proved negative. Source-backed graded labels need a frozen rubric and gain function. Undefined if ideal DCG=0. |
| Known-positive yield@K | Number of returned candidates with documented-positive labels / actual returned count, accompanied by filled slots / K | Shows the immediately verifiable content of shortlists | This is not true chemical precision on incomplete labels. If all positive labels are correct, it can be interpreted as a conservative observed-positive yield. |
| Precision@K on adjudicated pools | TP among Top-K / actual returned candidates, only where every returned candidate has a valid positive/negative label under the criterion | Measures how often screened suggestions satisfy an assessed criterion; higher is better | Requires independently assessed outputs, ideally blinded and pooled across methods plus random controls. Otherwise report judged precision with judged fraction and selection bias; no full precision claim. |
| AP@K / MAP@K (supplemental) | AP_q = sum_{r<=K} precision@r * rel_r / min(count(P_q),K); MAP averages AP_q | Rewards recovery of several observed positives early | Overlaps with nDCG/recall; incompleteness and normalization convention matter. Not another independent proof of improvement. |
| Positive-rank distribution | Full-ranking best/individual positive ranks, or cumulative fraction recovered versus rank | Shows hard cases hidden by averages; lower ranks are better | With Top-10-only outputs, ranks >10 are censored. Do not call them rank 88 or 999 to compute an ordinary mean. Report censored counts or generate full lists. |
| Filter retention and enrichment | Retained known positives / initial known positives; known-positive fraction after / before filtering on the same assessed pool | Tests search-space narrowing while retaining useful options; high retention with improved yield is desirable | A tiny shortlist can look selective while discarding good options. Unlabeled candidates prevent true enrichment claims; zero baseline yield makes a ratio undefined. |
| End-to-end reference-confirmed success@K | Queries with at least one returned candidate independently satisfying ALL specified criteria / attempted eligible queries | Measures the actual researcher-facing task; higher is better | Separate confirmed pass, confirmed fail, and unassessable. Give lower bound confirmed-pass/Q and upper bound (confirmed-pass+unassessable)/Q if binary success cannot be resolved. The bounds are epistemic, not confidence intervals. |

For short returned lists, Hit/Recall use the actual list and unfilled slots receive no retrieval credit. Report return count and slot fill rate. Do not inflate precision by quietly abstaining on difficult queries.

### 5.3 Classification: only where true labels exist

Applicable to a declared stability threshold, property-constraint pass/fail, verified donor/acceptor/other classification, or an independently adjudicated suitability criterion. Not applicable to unlabeled elemental rankings.

| Metric | Calculation | Why relevant / good result | Limitations |
|---|---|---|---|
| Precision | TP/(TP+FP) | High value means fewer wasted follow-up assessments | Can rise by rejecting nearly everything; report recall, coverage and class prevalence. |
| Recall / sensitivity | TP/(TP+FN) | High value means fewer suitable candidates missed | Can rise by accepting everything; report precision. |
| Specificity | TN/(TN+FP) | Measures rejection of known failures | Requires credible negatives; chemistry-specific failure conditions matter. |
| Accuracy | (TP+TN)/(TP+TN+FP+FN) | Overall correct labels | Misleading for imbalanced data; never the sole endpoint. |
| Balanced accuracy | (sensitivity+specificity)/2 | Balances positive/negative performance | Undefined if a reference class is absent; report support. |
| F1 | 2TP/(2TP+FP+FN) | Summarizes precision-recall trade-off | Ignores TN and unequal research costs; threshold-dependent. |
| PR-AUC / average precision | Sweep continuous decision score over thresholds; declare whether average precision or trapezoidal PR area is used | Useful for rare positives; compare to positive prevalence | Requires reliable binary labels. Scores need not be calibrated probabilities. Different prevalence changes comparability. |
| ROC-AUC (secondary) | Probability a random positive has higher score than a random negative, with tie handling | Threshold-independent discrimination | Can look strong with rare positives despite poor research yield; compute from continuous scores, not thresholded labels. |
| Confusion matrix | Raw TP,FP,FN,TN or class-by-class counts plus row-normalized matrix | Makes error types visible | Only on adjudicated labels; include sample counts and unknown/abstained counts outside the matrix. |

For multiclass role classification, compute each role's precision, recall and F1 one-versus-rest, then take the arithmetic mean of class F1 for macro-F1, reporting each class support. If a class is absent, declare the undefined-metric convention and do not imply its performance was measured.

If the actual decision is ternary (pass/fail/uncertain), keep it ternary and report abstentions rather than manufacture binary certainty. Numerical uncertainty near a threshold deserves a separate borderline slice.

### 5.4 Geometry and structural validity

| Metric | Calculation | Why relevant / good result | Limitations |
|---|---|---|---|
| Construction validity | Candidates passing declared composition/site-count, occupancy, finite-coordinate, positive-volume, lattice and periodic-distance checks / generation attempts | Detects invalid generation; all correctly specified construction operations should satisfy invariants | Distance cutoffs need element-pair rules and validation; passing checks does not prove bonding or synthesis. |
| Concentration correctness | abs(x_generated-x_requested), with x defined as fraction on target sublattice; also report total atomic fraction | Confirms intended substitution/doping level; exact representable values preferred | A finite supercell cannot represent every requested dilute level. Log rounding and actual counts. |
| Site/coordination agreement | Correct documented site assignment / adjudicated assignments; coordination-number error or agreement under a fixed neighbor definition | Tests contextual compatibility | Neighbor methods and tolerances affect assignments; ambiguous/disordered references need separate handling. |
| Structural match rate | Predicted relaxed structures matching reference under pinned StructureMatcher settings / reference-matched attempts | Tests recovery of known geometry | Species-aware match for actual same-composition recovery; anonymous matching only for declared prototype retention. Match is not stability. Different valid polymorphs can be counted as failures if reference set is incomplete. [S11] |
| Aligned periodic RMSD | sqrt(mean_i norm(rhat_i-r_i)^2) after explicit atom mapping, cell/origin alignment and periodic minimum-image handling | Quantifies geometric error in Angstrom; lower is better | Do not compare unmapped cells or unrelated compositions directly. State affine strain treatment; report atom counts. |
| Volume and lattice errors | abs(Vhat-V)/V; lattice-length errors and angle errors against compatible reference cells | Captures distortion and relaxation quality | Cell representation and finite-temperature/strain differences confound comparison. Standardize cells and report reference conditions. |
| Relaxation convergence | Converged attempts / attempted relaxations, with max force, stress, optimizer and step budget | Operational reliability; high convergence within budget is desirable | A force minimum can be metastable, dynamically unstable or physically wrong. A potential's convergence is not DFT agreement. |
| Uniqueness and database match | Unique structures / valid generated structures; known matches / matchable structures | Avoids repeated recommendations and separates rediscovery | Database absence establishes only no match under that snapshot and matcher, not novelty or synthesizability. |

Space-group agreement is descriptive, not a universal pass criterion: substitutions and dopants can legitimately lower symmetry. Phonon/elastic stability checks are conditional advanced experiments; do not claim dynamical or mechanical stability without actually assessing the corresponding quantities. Imaginary-mode classification requires wave-vector coverage and a declared numerical tolerance, not just absence of one imaginary Gamma mode.

### 5.5 Regression, energies and thermodynamic screening

Let e_i=yhat_i-y_i. Use eV/atom for bulk formation/hull energy, eV/defect for defect formation energy, eV for gaps; never mix units in one metric.

| Metric | Calculation | Why relevant / good result | Limitations |
|---|---|---|---|
| MAE | mean abs(e_i) | Typical absolute numerical error; lower is better | Does not expose tail errors or bias; compare to a simple baseline and reference uncertainty. |
| RMSE | sqrt(mean e_i^2) | Penalizes large mistakes; lower is better | Outlier-sensitive; meaningful outliers should not be deleted to improve it. |
| Signed bias | mean e_i | Identifies systematic over/underestimation; near zero desirable | Positive and negative errors cancel; zero bias is not high accuracy. |
| Median/P90 absolute error | Median and 90th percentile of abs(e_i) | Shows typical and difficult predictions | Quantiles unreliable for tiny samples; give counts and errors per case. |
| R-squared (secondary) | 1-sum e_i^2 / sum(y_i-mean y)^2 | Improvement over reference-set mean in variance terms | Can be negative; undefined for constant reference. Wide property ranges can hide unacceptable local errors. |
| Spearman rho / Kendall tau-b | Correlation of predicted and reference ranks on the same objects | Useful when selecting lower-energy candidates matters more than absolute accuracy | Good rank correlation does not guarantee correct stable/unstable decisions or low error; handle ties and stratify within comparable queries. |
| Pairwise energy-order accuracy | Correct non-tied reference orderings / comparable pairs within a fixed host/composition context | Tests selection among configurations or candidates | Exclude reference differences below a declared uncertainty tolerance. Pairs are correlated; bootstrap at host/group level. |
| Hull-distance error | MAE/RMSE/bias on independently referenced energy above hull | Tests decomposition-stability estimates rather than only elemental formation | Hull completeness, correction scheme, functional and reference energies matter. Do not use the prediction itself as its reference. |
| Stability precision/recall/F1 | Apply Section 5.3 to y_hull<=tau_ref and predicted decision under a frozen policy | Tests screening utility | tau_ref is a declared definition/engineering allowance, not a universal synthesis boundary. Thresholds and uncertainty must be stated. |
| Discovery yield and acceleration | Reference-confirmed suitable candidates found within fixed count/time budget; yield divided by matched random-baseline yield | Measures useful screening per follow-up budget | Only valid on assessed pools and comparable costs; zero baseline makes ratio undefined. No claimed DFT speedup without matched measurements. |

Formation energy per atom is (E_compound-sum n_i*mu_i)/N under a compatible reference convention. Energy above hull compares to the lowest competing phase mixture at the same overall composition. Negative formation energy alone does not establish stability. [S3]

Evaluate fixed-geometry single-point energy and relaxation-assisted prediction separately. A reference relaxed structure given as model input is a retrospective energy task; it must not masquerade as discovery from unrelaxed structures. Preserve model checkpoint identity and uncertainty/domain restrictions. Compatible DFT and potential reference accounting are mandatory; averaging incompatible total energies is invalid.

For custom exploratory stability screening, plot a predeclared sensitivity grid tau_ref=0,0.025,0.05,0.10 eV/atom, with numerical tolerance specified. These are protocol sensitivity values, not experimentally validated universal cutoffs. Choose any primary nonzero cutoff from the declared task/literature before test inspection. Official benchmark comparisons retain official thresholds. Mark borderline references and reference-method uncertainty.

### 5.6 Band-gap preservation and constraint satisfaction

Do not pool PBE, HSE, TBmBJ, optical gaps and experimental electronic gaps as interchangeable truth. Keep phase, temperature, dimensionality, strain, spin-orbit treatment and direct/indirect/optical definitions. Compare model errors within each reference track. [S4, S5]

| Metric | Calculation | Why relevant / good result | Limitations |
|---|---|---|---|
| Gap prediction error | MAE/RMSE/bias in eV against the selected reference track | Tests whether the numerical model is useful | A low error versus PBE is not necessarily accuracy versus experiment. Metals and small-gap cases need separate summaries. |
| Gap-change error | MAE of (Eghat_candidate-Eghat_host)-(Egref_candidate-Egref_host) | Directly tests substitution-induced change | Requires matched host/candidate references at the actual composition and conditions. Endpoints cannot certify intermediate alloys. |
| Reference preservation fraction | mean 1[abs(Egref_candidate-Egref_host)<=delta] for assessed recommendations | Tests a specified preservation tolerance; higher is better for preservation tasks | delta must come from the researcher's objective, not be enlarged after seeing results. No universal delta. |
| Window violation | max(L-Egref,0,Egref-U), mean in eV; fraction within [L,U] | Measures how far suggestions miss the requested functional range; lower violation is better | Window satisfaction is only one functional criterion; it does not establish mobility or device performance. |
| Preservation decision precision/recall | Section 5.3 with reference constraint labels and predicted pass/fail | Exposes false reassurance about property preservation | Needs complete assessed labels and declared thresholds. Unknown gaps must remain unknown. |
| Gap versus concentration curve error | MAE at matched reference concentrations; bowing-parameter error only if sufficiently sampled and same fitted model | Tests alloy response, not just endpoints | Sparse references and disorder/strain cause uncertainty. Never assume linear interpolation is experimental evidence. |

Report predicted satisfaction separately from reference-confirmed satisfaction. A model predicting that its own candidates meet a window is not external validation. Relative percentage gap error and MAPE are not primary metrics because near-zero gaps make them unstable.

### 5.7 Dilute doping, separate from substitution

| Metric | Calculation | Why relevant / good result | Limitations |
|---|---|---|---|
| Dopant retrieval | Hit@K, Recall@K, MRR@10, nDCG@10 from Section 5.2 on doping labels only | Tests recovery of documented dilute dopants | Does not establish activation or carrier concentration; role-specific labels must be available. |
| Role classification | Macro-F1 and per-role precision/recall for donor, acceptor and other, on adjudicated roles | Tests requested electronic role while exposing imbalance | Dopant role can depend on site, charge and host; unknown role is not an extra confirmed chemical class. |
| Site preference agreement | Correct preferred site / references with distinguishable site preference; rank correlation of site energies where available | Tests local environment specificity | Requires reference site comparisons under matching conditions, not just a plausible site label. |
| Defect formation-energy error (conditional) | MAE/RMSE in eV/defect at specified charge q, chemical potentials and Fermi level | Tests defect thermodynamic accounting | Neutral energy-only potentials generally cannot establish charged-defect levels. No such metric until compatible calculations or a validated specialized model exist. |
| Charge-transition-level error (conditional) | Absolute error in eV relative to a consistently aligned VBM, matched charge transition | Tests shallow/deep defect predictions | Needs band-edge alignment, charged-defect energies and corrections; missing transitions are not zero error. |
| Supercell convergence (conditional) | Change in defect quantity across increasing cell sizes/separations; report actual atomic counts, target-site fraction and image distances | Tests whether finite-size interactions dominate | An arbitrary supercell is not the dilute limit; charge corrections and electrostatic effects remain important. |

Reference formalism: E_f(defect^q)=E_defect^q-E_bulk-sum n_i*mu_i+q(E_F+E_VBM)+E_corr, with all energy zeros explicitly defined. Some implementations absorb E_VBM into the Fermi-level convention. Donor/acceptor effectiveness further depends on compensation and activation. [S6]

An optional quantum-defect database includes calculated defects in several semiconductors, but its quantum-emitter objectives differ from electrical doping. Admit only compatible point-defect slices after auditing the actual data. It is not a ready-made universal dopability benchmark. [S12]

### 5.8 Explainability and evidence

| Metric | Calculation | Why relevant / good result | Limitations |
|---|---|---|---|
| Numeric consistency | Correct numeric assertions / all numeric assertions, against immutable result packet with rounding tolerance | Tests whether prose faithfully copies scores, units and conditions; all should agree | Can be perfect while omitting important caveats. |
| Supported-claim fraction | Scientific factual claims supported by supplied evidence / all scientific factual claims | Detects unsupported assertions; higher is better | Requires claim decomposition and expert/source review; unsupported is not automatically false. No claims gives undefined score, not perfect score. |
| Citation correctness and coverage | Correctly entailed citation-claim links / all links; evidence-requiring claims with valid citations / all evidence-requiring claims | Tests whether references support what is said | URL validity alone is insufficient; cite exact supporting passage/figure and respect source access. |
| Caveat disclosure | Required case-specific caveats actually stated / required caveats in rubric | Tests disclosure of predictions, missing data, overlap, concentration and uncertainty | Checklist-based and task-specific; bloated prose is not automatically useful. |
| Score decomposition residual | abs(f(x)-phi_0-sum phi_j) in declared output space, or direct weighted-component reconstruction error | Checks arithmetic faithfulness of additive score explanations; low residual desirable | Not proof of physical causality or correctness. Direct component contributions are preferable for a simple weighted sum; SHAP requires a declared function/background/masker. [S13] |
| Perturbation fidelity | Correlation/agreement of attributed influence with actual score changes under declared valid interventions; optionally infidelity E[(I^T phi-(f(x)-f(x-I)))^2] | Checks sensitivity claims against implemented behavior | Physically invalid feature perturbations mislead; fix perturbation distribution, units, background and output space. This is model faithfulness, not a causal chemistry experiment. [S14] |
| Expert clarity/usefulness | Blinded ratings using anchored rubric (1 unusable, 3 understandable but incomplete, 5 clear and evidence-complete); paired template/LLM comparison | Tests researcher communication value | Subjective; report reviewer expertise, count, disagreement and conflicts. If fewer than two reviewers, no inter-rater reliability claim. |

Do not use BLEU/ROUGE or an LLM's self-rating as the primary scientific explanation metric. A different LLM can assist screening but cannot be the sole judge. GNNExplainer is a separate graph-attribution method; it is not automatically implemented by adding SHAP or Gemini.

### 5.9 Uncertainty, abstention and operational performance

| Metric | Calculation | Why relevant / good result | Limitations |
|---|---|---|---|
| Prediction-interval coverage and width (conditional) | Fraction of references inside intervals; mean interval width at declared nominal coverage | Tests whether uncertainty is informative | Wide intervals trivially cover; calibration must use separate data and deployment exchangeability may fail. Ensemble disagreement alone is not a calibrated interval. |
| Brier score (conditional) | mean(p-y)^2 for predicted binary probabilities | Measures probabilistic accuracy; lower is better | Not valid on arbitrary weighted confidence scores or unknown labels. Calibrate on validation only. |
| Calibration curve/ECE (conditional) | Per-bin observed positive fraction versus mean probability; ECE=sum n_b/N * abs(mean_probability_b-positive_fraction_b) with declared binning | Tests interpretation of stated probabilities | ECE depends on bins and is unreliable at small N. Reliability diagrams need counts; do not promise calibrated synthesis probabilities. |
| Selective risk versus coverage | Error on accepted assessed predictions as an abstention threshold changes; accepted/attempted queries | Tests whether abstention reduces error responsibly | Easy to hide unsupported cases; report intended-scope denominators and reference availability. |
| Latency | Wall-clock p50/p95 per stage and end-to-end; cold and warm separately | Measures responsiveness on Acer hardware; lower at equal quality is better | Depends on batch size, model, cache and network; never compare machines without disclosure. |
| Throughput and memory | Completed cases/time; peak process RAM and GPU VRAM with measured sampling method | Shows feasible scale | Exclude nothing silently: include failures, timeouts and batch settings. Mac and NVIDIA results are separate environments. |
| Cost and workload | API calls/cost, structures scored, relaxation steps, candidates assessed and cache hit rate | Measures research budget and screening effort | Estimates are labelled; a DFT cost comparison requires actual equivalent calculations or clearly sourced estimates. |
| Operational reliability | Success/failure/timeout/unsupported counts divided by attempts | Prevents failed runs from disappearing from accuracy results | Successful execution says nothing about chemistry. Log error categories and retry policy. |

Latency protocol: 5 warm-up requests followed by 30 measured repeats for lightweight deterministic stages; use up to 3 repeats per frozen structure for expensive inference/relaxation if feasible and report exact repeats. Cache-cold timing separately. Synchronize GPU work before timing. Never label one timing measurement p95. Preserve API/network timing separately from local computation.

## 6. Experiment register

| Experiment | Dataset and input | Comparison / procedure | Primary outputs and limits |
|---|---|---|---|
| E00 data audit | B0 | Source/units checks, hashes, missing values, imputation derivation | Coverage and validity tables; no accuracy claim |
| E01 legacy reproduction | B1 | Reproduce independent engines and existing rankings | Metrics labelled retrospective; document truncated MRR and censored-rank conventions |
| E02 held-out element retrieval | B2 site-qualified positives and elemental slice | Random, chemical baseline, 3 signals, fusions; common-support and intended-scope views | Recall@5, MRR@10, Hit@K, nDCG, uncertainty; no unsupported precision |
| E03 representation robustness | B0 and E02 queries | SVD seeds 0-4; repeatability, dimensions 10/20/40 where mathematically valid; property leave-one-feature/group-out; imputation sensitivity | Ranking/metric changes; tune choices on validation only; diagnostics do not prove chemistry |
| E04 host/site contribution | B2 with verified structures/sites | Global rankings versus contextual checks; shared initial candidate pool | Site agreement, retained positive recall, contextual ranking improvement; mismatched-site controls only if adjudicated |
| E05 structure generation | B2/B6 | Generate requested concentrations and arrangements; compare reference geometries where present | Construction correctness, concentration error, uniqueness, match/RMSD, failures |
| E06 energy prediction | B4 energy track, B5 or frozen custom subset | Explicit potential/checkpoint versus simple models; fixed-geometry and relaxation tasks separated | Energy errors and rank metrics; training overlap and energy conventions |
| E07 stability filtering | B5 and/or qualified B6 custom pool | Frozen cutoff, candidate budget, per-model and ensemble policies | PR/confusion matrix on known reference stability; hull-error plots; no synthesis proof |
| E08 gap prediction | B4 gap tracks/B7 | Median, descriptors+RF, feasible learned model; official and grouped robustness tracks distinct | Gap MAE/RMSE, bias and overlap audit |
| E09 gap preservation | B2 paired host/candidate gap records, S9 alloy data after extraction | No-change baseline versus property-aware selection and full pipeline | Gap-change error, window violation, reference-confirmed joint success; no interpolated truth |
| E10 dopant retrieval | B3 | Separate random/chemical/signals/fusions and role-aware contextual ranking | Doping Recall@5 and coverage; no mixing with alloy metrics |
| E11 defect validation (conditional) | B8/compatible quantum-defect slices if curated | Matched defect reference calculations and specialized method | Formation/transition-level errors; unavailable without suitable references and model |
| E12 evidence and explanation | Frozen evidence packets from held-out queries | Numeric/template checks, blinded template versus LLM comparison; mask withheld evidence for prediction track | Claim/citation accuracy, fidelity, caveats, reviewer ratings |
| E13 ablation and full pipeline | Common held-out assessed pool | Remove each signal, site, energy, property or evidence component; paired comparisons at fixed budgets | Retention, yield, retrieval and joint outcomes; no post-hoc best-subset headline |
| E14 runtime and scope | Frozen request sizes plus all-element input suite | Acer primary measurements; Mac optional separate replication | Latency, throughput, RAM/VRAM, failure rates, support matrix |

All conditional experiments are marked not run if their admission conditions are unmet. Published scores from external papers appear in a related-work table, not as if rerun on our benchmark.

Use explicitly logged validation grids rather than unlimited tuning. Proposed initial weight search: nonnegative weights summing to 1 at increments of 0.25 (15 combinations), plus fixed equal weights; scaling fitted on validation/training partitions where learned. Choose the simplest configuration within practical equivalence of validation performance, recording the tie rule. RRF constants and energy thresholds require a separately declared small grid or fixed default. Keep each baseline's tuning budget comparable.

## 7. Figures and tables to generate from actual results

| Figure/table | Data and axes | What it establishes / what it does not |
|---|---|---|
| Dataset evidence map | Counts by source, chemistry, site, label and evidence class | Shows what was evaluated and where evidence is sparse |
| Periodic-table support matrix | Element versus available signal/model/reference | Shows coverage; not elemental accuracy |
| Similarity heatmaps and distributions | Pairwise scores per method, raw and transformed separately | Shows behavior and scale differences; no label accuracy proof |
| Embedding projection | PCA/UMAP with declared parameters and seed | Exploratory geometry only; proximity in 2D is not substitution validation |
| Retrieval comparison bars | Method versus Recall@5/MRR@10 with paired uncertainty | Tests combination idea on identical cases |
| Retrieval curves | K versus Hit@K/Recall@K, K up to 10 primary | Shows reading-budget trade-off; no precision claim on unknowns |
| Per-case rank heatmap | Queries versus methods, rank of each observed positive; >K/unsupported shown explicitly | Exposes host/target/family failures and censoring |
| Signal overlap | Pairwise Top-K Jaccard and disagreement cases | Describes redundancy; improvement must be measured separately |
| Ablation difference plot | Metric difference versus baseline, confidence intervals | Shows module contribution; includes negative effects |
| Structural case panels | Site-labelled host and candidate, matched coordinates | Makes what was substituted inspectable; illustration is not proof |
| Geometry error plots | RMSD/lattice/volume error by family and concentration | Evaluates reference geometry agreement |
| Energy parity and residual plots | Reference versus prediction, y=x line; residual versus reference | Shows bias/tails; label eV/atom and fixed/relaxed task |
| Stability PR curve and confusion matrix | Continuous score versus reference stable labels; counts at frozen cutoff | Measures screening discrimination on adjudicated data |
| Gap parity by method/source | Predicted versus reference gap, facet by reference type | Shows numerical prediction quality without mixing functionals |
| Paired gap changes and concentration curves | Candidate-host gap difference or x versus gap; requested tolerance/window and reference points | Tests actual property preservation; predictions dashed, references distinct |
| Stability-gap trade-off | Gap deviation versus hull distance; uncertainty and evidence status marked | Shows multi-criterion candidates; model-only points labelled predictions |
| Screening funnel plus positive retention | Candidate counts and retained verified positives at each stage | Shows efficiency together with lost useful candidates |
| Dopant-specific plots | Role-conditioned retrieval, role confusion matrix if labels exist; defect formation diagrams only if calculated | Separate doping claims; no invented charge-state lines |
| Explanation audit | Unsupported claims, numeric errors, citation coverage and reviewer ratings | Shows fidelity; attractive narrative examples are secondary |
| Risk-coverage/calibration | Error versus accepted fraction; reliability only if calibrated | Shows abstention trade-offs and probability reliability |
| Runtime and resource plots | Stage latency, structure size versus time/VRAM; cold/warm separated | Shows feasibility on measured hardware |
| Final scorecard and failure table | Dataset, method, N, coverage, metric, interval, failure modes, evidence class | Makes conclusions and limitations reviewable |

Every figure caption includes experiment ID, split, N and grouping unit, reference type, threshold/units, error-bar definition and main caveat. Export underlying numeric tables and plotting settings. Do not use invented demonstration values in scientific result figures. Empty sections say not run, not assessed, or insufficient evidence. Use consistent colors for methods and visual distinction between predictions and references.

## 8. Uncertainty, statistical comparisons and success rules

- Save per-query results before aggregation. Compare methods on the same queries with paired differences, not unrelated means.
- Use 2,000 paired cluster-bootstrap resamples with seed 42 for exploratory 95% intervals, clustering by independent host family/alloy series as defined in the split manifest. If too few independent groups make intervals unreliable, show all group differences, label intervals exploratory or omit them; never count correlated configurations as independent replicates.
- For seed-dependent models use seeds 0-4 if feasible; report all completed seeds and mean/dispersion. Seed variation and dataset uncertainty are different and must not be conflated.
- Where appropriate use a paired permutation test at the group level; if inferential tests are attempted, identify a primary comparison in advance and control secondary comparisons (e.g. Holm adjustment). Statistical significance alone does not establish practical usefulness.
- Freeze a minimum practically meaningful improvement or acceptable error from task requirements before final testing. There is no defensible universal requirement such as 95% accurate substitutions or 0.1 eV error for all chemistry. If no such application requirement exists, report effect sizes and uncertainty without a pass/fail superiority claim.
- The primary fusion comparison is fused versus the best single-signal baseline selected on validation, not chosen on test. Also report every individual method. If the interval includes meaningful harm and benefit, conclude inconclusive rather than improved.
- Macro-average gaps/energies by query/family as well as sample-weighted errors where necessary; a large family must not silently dominate the conclusion.
- Unsupported, failed and unassessable cases have explicit denominators and outcomes. Report conditional performance on answered cases and intended-scope failure/abstention alongside it. Never turn missing numeric predictions into made-up reference errors.
- No claim of new material discovery solely from no database match. Label as an unvalidated candidate until appropriate independent validation exists.

## 9. Reproducibility contract

Each experiment directory must contain:

```
experiment_manifest.json       # Intent, dataset/version/hash, split, methods, parameters
references.jsonl               # Provenance, passage locators, claims, evidence classification
split_manifest.json            # Query/group IDs; train/validation/test assignments
predictions.jsonl              # Every query-candidate result, raw scores, outputs, statuses
metrics.json                   # Values, units, N, denominators, CI method; null if unavailable
failures.jsonl                 # Errors, unsupported cases, timeouts, retries, exclusions
environment.json              # OS, Python/packages, device, VRAM/RAM, code/model hashes
figures/                      # Actual plots plus machine-readable source tables
report.md                     # Plain-language interpretation, comparison and limitations
```

Prediction records include raw and transformed similarity signals, signal availability, fusion weights, rank, host/site/concentration/structure hash, geometry source, checkpoint, energy zero/reference method, relaxation status, gap source/type, evidence IDs, thresholds, final decision, uncertainty and time. Store alternatives rejected at each stage and why. Missing signals are null with a reason, never fabricated zero similarities.

Capture API snapshot/retrieval date and cached-response hash; model/provider/version, prompt and generation settings for LLM prose; stochastic seeds; dependency lockfile; hardware and batch sizes; exact command; reference licensing/access limitations; changes from the previous protocol version. Do not store API keys. Secrets-free manifests are committed with results when implementation begins.

The companion `MATRA_Experiment_Record_Template.json` is an unexecuted template, not a JSON Schema or results file. Null fields must be completed or explicitly explained before a run can be admitted to the final report. Freeze the configuration hash before evaluating the final test set.

## 10. Stage gates and explanation to the user

| Stage | Evaluation gate | What can be claimed afterwards |
|---|---|---|
| Dataset audit | Units/provenance checked, references classified, coverage and imputation transparent | Dataset integrity and known support |
| Existing engines | Reproduced legacy results, full coverage/input checks and ranking conventions verified | Retrospective baseline behavior |
| Fusion | Fixed grouped evaluation and paired baseline comparison | Whether fusion helps within that population |
| Structures/sites | Correct construction, site and concentration checks; reference geometry comparisons | Structural implementation validity and measured match quality |
| Energetics | Compatible references/checkpoints, energy/hull errors and screening outcomes | Measured energy/stability-assessment performance, not synthesis proof |
| Gap module | Independent gap errors and reference-confirmed constraint decisions | Property assessment on the evaluated reference track |
| Doping | Independent dopant benchmark and role/site checks; optional defect validation | Only the doping capabilities actually assessed |
| Explanation | Numeric/claim/citation audits and optional expert review | Explanation faithfulness and measured clarity |
| Integration | Complete query outcomes, screening trade-offs, runtime and reproducible exports | Evaluated end-to-end utility and documented limits |

After each stage, use this reporting sequence:

1. What question we tested and which dataset/families were used.
2. What was held out and what each method could access.
3. Actual numbers with denominator, unit and uncertainty; link plots and raw records.
4. A plain-language interpretation, e.g. 'the method retrieved at least one documented option within five places in X of N queries' using actual values only.
5. Whether a change beat the baseline, was inconclusive or harmed performance; show effect size.
6. Where it failed, including per-family and unsupported examples.
7. Which scientific questions the result does not answer.
8. The next improvement justified by those observations.

## 11. Final report and claims ledger

The final evaluation report includes: frozen scope and protocol changes; dataset/evidence and split audit; reproducibility environment; baseline and tuned-method tables; primary endpoint results with coverage/uncertainty; per-module experiments; substitution and doping in separate sections; ablations and failure cases; numerical/structural/property checks; evidence/explanation audit; runtime/resource budget; explicit overlap and reference limitations; conclusions mapped to experiment IDs; downloadable predictions, plot data and figures.

Claims ledger columns: proposed claim, required independent evidence, experiment ID, observed result, uncertainty, population, support status (supported/inconclusive/contradicted/not tested), and allowed wording. A combined overall accuracy percentage will not replace the separate scientific endpoints. If no measurable improvement is found, that is the conclusion to report.

## 12. Primary and official sources

Sources accessed 5 November 2026; numerical dataset sizes and version-specific API defaults must be rechecked when pinned. These sources motivate benchmark selection and scientific distinctions; the custom experiment choices above are MATRA protocol decisions, not claimed community standards.

- S1: [Matbench official repository and task protocols](https://github.com/materialsproject/matbench); [Dunn et al., benchmark paper](https://arxiv.org/abs/2005.00707).
- S2: [Matbench Discovery paper](https://www.nature.com/articles/s42256-025-01055-1); [official WBM dataset documentation](https://github.com/janosh/matbench-discovery/blob/main/data/wbm/readme.md). Retain official task conditions when comparing to published benchmark scores.
- S3: [Materials Project phase-diagram methodology](https://docs.materialsproject.org/methodology/materials-methodology/thermodynamic-stability/phase-diagrams-pds).
- S4: [Materials Project electronic-structure methodology](https://docs.materialsproject.org/methodology/materials-methodology/electronic-structure).
- S5: [NIST JARVIS](https://jarvis.nist.gov/); [JARVIS download and property definitions](https://jarvis-materials-design.github.io/dbdocs/thedownloads/). Database totals change and are not frozen in this protocol.
- S6: [pymatgen-analysis-defects formation-energy methodology](https://materialsproject.github.io/pymatgen-analysis-defects/content/formation-energy/); [defect-analysis source repository](https://github.com/materialsproject/pymatgen-analysis-defects).
- S7: [PNcsp+](https://doi.org/10.1021/acs.jctc.6c00044). Supplied project reference; any benchmark replication requires independent access/protocol verification.
- S8: [DeepOFM / Learning Hidden Chemistry](https://arxiv.org/abs/2101.11902). Supplied project reference; comparison is conditional on equivalent local-environment tasks.
- S9: [Wang et al., Ga2O3 alloy HSE study](https://arxiv.org/abs/1806.03360), [published paper](https://doi.org/10.1103/PhysRevApplied.10.011003). A candidate numerical-reference source, not a certified experimental substitution benchmark.
- S10: [CrabNet paper](https://doi.org/10.1038/s41524-021-00545-1). Supplied project reference; use as a property baseline only on equivalent data/splits.
- S11: [pymatgen StructureMatcher documentation](https://pymatgen.org/pymatgen.analysis). Pin actual version and tolerances, because defaults and parameter meanings can change.
- S12: [Ivanov et al., quantum-defect database paper](https://arxiv.org/abs/2303.16283). Conditional auxiliary source; domain mismatch with general electrical dopability must be disclosed.
- S13: [SHAP explainer specification](https://shap.readthedocs.io/en/latest/generated/shap.Explainer.html).
- S14: [Yeh et al., explanation infidelity and sensitivity](https://papers.neurips.cc/paper_files/paper/2019/hash/a7471fdc77b3435276507cc8f2dc2569-Abstract.html).
- S15: [MACE foundation-model documentation](https://mace-docs.readthedocs.io/en/latest/guide/foundation_models.html).

