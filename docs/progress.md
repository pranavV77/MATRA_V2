# MATRA central progress

Authoritative workspace: `C:\Final Project`. Owner approved Stage 1 in chat on 5 November 2026. Required workflow: stage explanation, approval, incremental implementation, executed edge cases, separate validation categories, reports/Telugu narration, owner review; no automatic next stage.

Current stage: Stage 2 data release and approved primary-source review — engineering tested; scientific benchmark remains incomplete. Final suite: 105 passed (73 previous + 32 primary-evidence tests). Fourteen source leads screened, three narrowly scoped claims curated: one computational substitution seed eligible, zero experimental full-context cases eligible, two doping scopes held. All 23 original broad assertions remain withheld in frozen v2.0.0. Stage 1's 15 legacy-engine diagnostic failures remain open for Stage 3; they are not reclassified as passed. No production recommendation engine was changed.

## Roadmap (unchanged)

1. Baseline audit and reproducibility — reviewed; owner authorized Stage 2.
2. Dataset correctness, provenance and coverage handling — versioned engineering release implemented; benchmark primary-source curation and owner review pending.
3. Independent similarity-engine hardening — pending.
4. Similarity fusion and evaluation — pending.
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
- Engine stage: invalid k/types, duplicate validation, nonfinite/negative features, cache shape/norm/config checks, support-policy consistency and errors.
- Research: new held-out source-audited cases; clean overlap-aware evaluation; no property/stability claims from similarity alone.
- Audio: actual Telugu voice generation unavailable; complete narration script supplied.
- Clean-machine installation and cross-platform reproducibility not yet established.

Stage 1 review: docs/stages/stage_01/completion_report.md; evidence under results/stage_01/run_001. Stage 2 review: docs/stages/stage_02/index.html and completion_report.md; evidence under results/stage_02/run_001. New release: data/processed/v2_0_0 and data/benchmark/v2_0_0. No Stage 3 work has started.

## Approval gate after Stage 2

Engineering functionality/reproducibility passes do not certify the benchmark. Recommended next action is primary-source curation within Stage 2. Proceeding to Stage 3 with the scientific benchmark withheld requires informed owner approval. Do not silently activate the native data in legacy engines or claim improved accuracy.

## Approved primary-source follow-up

Owner approved continuation within Stage 2. Reports: docs/stages/stage_02_source_verification/index.html and completion_report.md. Final ledger: data/benchmark/v2_1_0/primary_evidence_reviewed.json (initial intermediate retained separately). Actual tests and verification: logs/stage_02/run_002 and results/stage_02/run_002. Telugu transcript provided; no audio generated. This bounded review pass is delivered, but a representative scientific benchmark is still pending; Stage 3 has not started. Continue primary-source curation unless owner explicitly accepts engine-only progress with the research hold documented.
