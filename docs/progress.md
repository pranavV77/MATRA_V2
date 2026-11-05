# MATRA central progress

Current status: Stage 6 bounded energy/relaxation engineering milestone implemented and locally verified; owner review pending. Owner approved isolated installation and official checkpoint download (“Yeah, start doing”). Actual Windows CPU stack: MACE 0.3.14/Torch 2.6.0+cpu in .venv_energy; original .venv preserved. Official MACE-MP-0b2-small weights/revision/hash frozen. Final tests: 510 regular + 24 isolated-energy tests passed. Three selected trial relaxations converged under the declared model; separate one-step HTTP request correctly nonconverged. Authoritative results: results/stage_06/run_002. Independent DFT energy/force accuracy: unverified (0 admitted cases). Formation/hull and thermodynamic stability: not assessed. Full scientific Stage 6 remains open; recommend reference curation, not automatic Stage 7. Reports: docs/stages/stage_06/completion_report.md and technical_guide.md.

Authoritative workspace: `C:\Final Project`. Owner approved Stage 1 in chat on 5 November 2026. Required workflow: stage explanation, approval, incremental implementation, executed edge cases, separate validation categories, reports/Telugu narration, owner review; no automatic next stage.

Previous milestone: Stage 3 independent-engine hardening — implemented and locally verified; awaiting owner completion review. Owner explicitly instructed “Start stage 3” after Stage 2 reports disclosed the scientific benchmark hold. Final suite: 320 passed (172 previous + 148 Stage 3 cases). The 15 previously failing Stage 1 behaviors now have passing targeted regressions. All 261 supported engine-target Top-10 results are unchanged; 22,821 ordered pair comparisons differ by at most 6.67e-16. Fresh full-corpus Atom2Vec retraining reproduces rankings with metadata-bearing cache. Stage 2 research hold is carried forward: only two substitution development references, zero fully contextual doping references, zero held-out cases; 23 original broad assertions withheld. No substitution accuracy/property-preservation claim. Stage 4 subsequently authorized for the review prototype; see current status above.

Earlier approved continuation: Stage 2 extended review v2.2.0, run_003. That pass had 143 tests passing. One experimental Bi2Te2Se substitution scope added to the earlier computational Ga–Al scope: two eligible substitution development references across two host families, zero fully contextual doping references. Two inherited doping scopes remain held; three additional source observations are deliberately unscored. No held-out test set or prediction accuracy claim. All 23 broad legacy assertions have explicit follow-up requirements and remain withheld. Earlier v2.0.0/v2.1.0 releases preserved.

## Roadmap

1. Baseline audit and reproducibility — reviewed; owner authorized Stage 2.
2. Dataset correctness, provenance and coverage handling — versioned engineering release implemented; benchmark primary-source curation and owner review pending.
3. Independent similarity-engine hardening — implemented and locally verified; owner authorized later continuation.
4. Similarity fusion and evaluation — implemented; owner authorized continuation to Stage 5; two-reference research limitation carried forward.
5. Host structures, sites and candidate generation — bounded engineering module implemented; 478 full-suite tests passed; owner authorized Stage 6 preparation; scientific chemical validation remains pending.
6. Energy/stability assessment — local energy/force/relaxation engineering implemented; 510 regular + 24 energy-suite tests pass. Independent energy and decomposition-stability validation remain pending; owner milestone review required.
7. Property preservation — pending.
8. Doping assessment — pending.
9. Evidence, explanations and final ranking — pending.
10. Research interface, integration and final evaluation — pending.

## Approved decisions

- Use existing local project and Python 3.10.11 environment; preserve original work.
- Keep substitution and doping evaluation separate; never treat unreported chemistry as negative truth.
- Evaluation is core development work; protocol under docs/evaluation.
- No cloud execution, package installs or upgrades. Approved Stage 2 follow-up retrieved public primary papers and metadata over HTTPS; downloads and all execution remain local. Blocked responses were retained, not bypassed.
- Baseline checkpoint is commit d84caf8 plus a saved dirty-results patch and hashes; local lightweight tag records HEAD. No user presentation files committed.

## Unresolved issues and next-stage inputs

- Stage 2 delivered native data with explicit units, PN/118 metadata, 1,316 provenance records, 118-element recognition registry, separately assessed radius estimates, source-condition flags and evidence-admission safeguards. Legacy artifacts remain intact.
- Stage 2 research hold: 6 citation-mismatch cases, 5 unresolved identifiers, 4 partial-support cases and 1 review-source case. All 16 original cases and 23 assertions preserved, none admitted to strict contextual evaluation yet. Unknown is not false chemistry. Correct primary passages/site/concentration evidence still required.
- Follow-up: additive v2.1.0 source-audited seed, with local document/extraction hashes and passage locators. Corrected Nb paper DOI 10.1038/s41598-021-03199-7; rejected candidate retained in acquisition history. Ga–Al model at x=0.5 is computational evidence only, not broad-range/experimental/property-preservation validation. Re monolayer occupancy and Nb weight-percent records retain incomplete-context holds. Independent expert adjudication pending.
- Stage 3 fixes: invalid k/types, duplicate tables/vocabularies, nonfinite/negative/zero-invalid features, undefined cosine vectors, cache shape/norm/config checks, explicit 118-element recognition/support status, corpus validation and no-overwrite cache publication. Legacy cache metadata remains unavailable; compatibility load is explicit in cache_info, strict metadata mode rejects it, non-default seed requests reject metadata-free caches. Fresh metadata-bearing cache available under results/stage_03/run_001.
- Research: new held-out source-audited cases; clean overlap-aware evaluation; no property/stability claims from similarity alone.
- Audio: actual Telugu voice generation unavailable; complete narration script supplied.
- Clean-machine installation and cross-platform reproducibility not yet established.

Stage 1 review: docs/stages/stage_01/completion_report.md; evidence under results/stage_01/run_001. Stage 2 review: docs/stages/stage_02/index.html and completion_report.md; evidence under results/stage_02/run_001. New release: data/processed/v2_0_0 and data/benchmark/v2_0_0. No Stage 3 work has started.

## Approval gate after Stage 2

Engineering functionality/reproducibility passes do not certify the benchmark. Recommended next action is primary-source curation within Stage 2. Proceeding to Stage 3 with the scientific benchmark withheld requires informed owner approval. Do not silently activate the native data in legacy engines or claim improved accuracy.

## Approved primary-source follow-up

Owner approved continuation within Stage 2. Reports: docs/stages/stage_02_source_verification/index.html and completion_report.md. Final ledger: data/benchmark/v2_1_0/primary_evidence_reviewed.json (initial intermediate retained separately). Actual tests and verification: logs/stage_02/run_002 and results/stage_02/run_002. Telugu transcript provided; no audio generated. This bounded review pass is delivered, but a representative scientific benchmark is still pending; Stage 3 has not started. Continue primary-source curation unless owner explicitly accepts engine-only progress with the research hold documented.

## Extended review follow-up

Owner's latest “Yeah” was interpreted explicitly in chat as approval to continue Stage 2 curation, not Stage 3. Reports: docs/stages/stage_02_extended_review/index.html. Ledger: data/benchmark/v2_2_0/extended_evidence.json. Local evidence: data/raw/stage_02_extended_sources; execution and verification: logs/stage_02/run_003, results/stage_02/run_003. Sn-Ga XAS establishes source-reported site preference but exact concentration tied to the XAS crystal is still missing from reviewed tabulated text; no graph point invented. Sn-rich amorphous film transport bounds are unscored observations, not universal negative chemistry. Ba/Sr neutron source has unresolved coordination/symmetry wording conflicts. Two additional PDF requests returned non-PDF responses; no full-text credit. Telugu narration script supplied; no playable audio. No stage change, production-engine edits, model training or new DFT execution.

## Doping-source follow-up, run_004

Owner authorized continued Stage 2 curation. Reviewed Si-Ga2O3 STM and Nb-SrTiO3 interstitial primary abstracts plus Mg-GaN channeling methods/results through a web-tool PDF text extraction. Direct local routes returned a CERN bot page, publisher 403s, and APS 401; failures retained, no bypass. Mg extraction is archived as text (lines 0–396), not claimed as a downloaded PDF. Source explicitly states no electrical characterization of its actual p-GaN specimens; typical Hall numbers concern similar specimens and cannot supply activation efficiency. Seven distinct quantities retain units, point/bound/range and specimen relationships. Reported 31% interstitial and 72% c-axis-aligned fit values are not normalized; c-axis alignment alone does not uniquely determine the Ga site. No new full-context doping admission or negative chemistry label. Supplement: data/benchmark/doping_review_v1_0_0/doping_evidence.json. Reports: docs/stages/stage_02_doping_review/index.html. Telugu script provided; no audio generated. Stage 3 remains pending; representative independent evaluation and expert adjudication remain incomplete.

## Stage 3 review

Reports: docs/stages/stage_03/index.html and completion_report.md. Reproducibility data, original engine copies, score comparisons and fresh cache: results/stage_03/run_001. Logs/tests: logs/stage_03/run_001. Core equations, feature definitions, ranking schema, six-decimal display and default legacy data/cache are preserved. Input/data errors are now rejected earlier. A Windows hard-link failure in initial cache-publication tests was resolved with no-overwrite Windows rename; the POSIX path is not executed/validated here. Initial failures and their correction remain in logs. No native-feature migration, fusion, structural calculation, benchmark-label change, package installation or cloud execution. Telugu narration script supplied; no actual audio generation available. Await owner approval before Stage 4.

## Stage 5 review

Reports: docs/stages/stage_05. Authoritative results: results/stage_05/run_002; final tests: logs/stage_05/run_002/pytest_005.xml. Initial failed tests and duplicate-CIF-label warnings remain preserved under run_001. Source acquisition: data/raw/stage_05_hosts (AFLOW original hash frozen). Added explicit ordered-host site selection, periodic geometry, bounded supercells, concentration accounting and unique unrelaxed CIF/JSON exports. Candidate order remains Stage 4 elemental fusion; no learned site preference. Original source data, engine implementations, presentations and owner dirty results preserved. Actual Telugu audio unavailable; complete narration script supplied. Pending: independent host diversity/site chemistry and planned Stage 6 energy/stability methodology. No automatic next-stage work.

## Stage 6 preparation

Owner authorized preparation and requested a progress estimate. Estimate 40–45% of full research implementation is judgment, not a measured metric. Existing Python 3.10.11, RTX 3050 4 GB/driver 552.27; required energy packages absent. Current MACE documentation requires Python >=3.11, while 0.3.14 release metadata declares >=3.7; actual Windows compatibility remains untested. Proposed isolated CPU-first environment and official small checkpoint require concrete implementation approval. No change to the working demo or existing environment. Audit: results/stage_06/preparation_001/feasibility_audit.json. Plan: docs/stages/stage_06/preimplementation_plan.md.

## Stage 6 approved implementation and review

Owner approved isolated installation and official model download. Existing no-install decision is superseded only for the approved .venv_energy within C:\Final Project. No cloud, new Python installation, GPU runtime or original .venv upgrade. Official 0a GitHub acquisition reset repeatedly; selected available official 0b2 small with frozen HF revision and published LFS hash, explicitly disclosed. Partial formal oxidation annotations separated from neutral model inputs. Initial cached timing superseded by fresh inference run_002; old outputs preserved. Actual model coverage 89 includes all 79 fusion elements, without universal chemistry accuracy claim. Current reports and full Telugu transcript under docs/stages/stage_06; no actual audio tool available. Next required scientific work: compatible independent energy references and phase data within Stage 6. Do not claim stable substitutions, energy MAE or full Stage 6 scientific completion.

## End-of-day owner handoff — 5 November 2026

Owner explicitly states Stage 6 has not been reviewed and is stopping work for today. Authorized action: back up the complete project updates to the existing GitHub origin. No Stage 6 acceptance or next-stage approval inferred. Work remains stopped after backup. Stage 6 engineering/scientific status and open reference-validation gate remain as above. Backup-only setup fixes allow restoring the ignored energy environment/model alongside committed manifests without overwriting earlier results. Four mocked restoration regressions added; full regular suite 514 passed (logs/handoff/2026-11-05/regular.xml). Separate 24-test energy suite remains the previously executed numerical validation; no new chemistry claim. Resume with owner review, not automatic Stage 7.

GitHub backup upload is pending authentication. Local end-of-day commits are prepared, but connected account tsjharsha has push=false for pranavV77/MATRA; local native credential retrieval failed. Remote main was still original d84caf8 at verification. No upload success or Stage 6 acceptance is claimed. Resume upload after connecting an account with repository write access; all work remains local and a Git bundle is retained.
