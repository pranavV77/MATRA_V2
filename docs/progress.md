# MATRA central progress

Current status: Stage 4 fusion and a partial review UI are implemented and tested. 386 tests passed. Two development references only; no held-out accuracy claim. Owner requested a partial working demo and measurable improvement for November 7 noon / November 9. Full Stage 5–9 scientific modules remain pending. See docs/stages/stage_04/completion_report.md. Await owner review before next stage.

Authoritative workspace: `C:\Final Project`. Owner approved Stage 1 in chat on 5 November 2026. Required workflow: stage explanation, approval, incremental implementation, executed edge cases, separate validation categories, reports/Telugu narration, owner review; no automatic next stage.

Previous milestone: Stage 3 independent-engine hardening — implemented and locally verified; awaiting owner completion review. Owner explicitly instructed “Start stage 3” after Stage 2 reports disclosed the scientific benchmark hold. Final suite: 320 passed (172 previous + 148 Stage 3 cases). The 15 previously failing Stage 1 behaviors now have passing targeted regressions. All 261 supported engine-target Top-10 results are unchanged; 22,821 ordered pair comparisons differ by at most 6.67e-16. Fresh full-corpus Atom2Vec retraining reproduces rankings with metadata-bearing cache. Stage 2 research hold is carried forward: only two substitution development references, zero fully contextual doping references, zero held-out cases; 23 original broad assertions withheld. No substitution accuracy/property-preservation claim. Stage 4 subsequently authorized for the review prototype; see current status above.

Earlier approved continuation: Stage 2 extended review v2.2.0, run_003. That pass had 143 tests passing. One experimental Bi2Te2Se substitution scope added to the earlier computational Ga–Al scope: two eligible substitution development references across two host families, zero fully contextual doping references. Two inherited doping scopes remain held; three additional source observations are deliberately unscored. No held-out test set or prediction accuracy claim. All 23 broad legacy assertions have explicit follow-up requirements and remain withheld. Earlier v2.0.0/v2.1.0 releases preserved.

## Roadmap

1. Baseline audit and reproducibility — reviewed; owner authorized Stage 2.
2. Dataset correctness, provenance and coverage handling — versioned engineering release implemented; benchmark primary-source curation and owner review pending.
3. Independent similarity-engine hardening — implemented and locally verified; owner review pending.
4. Similarity fusion and evaluation — implemented; 386 full-suite tests passed; owner review pending.
5. Host structures, sites and candidate generation — pending.
6. Energy/stability assessment — pending.
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
