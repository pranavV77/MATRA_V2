# Stage 2 doping-source review — curation pass report

1. **Objective:** assess Si/Mg/Nb sources without conflating site location and activation.
2. **Implemented:** immutable supplement; seven typed quantities; specimen-identity, bounds,
   archive-format and overclaim guards. No new full-context doping admission.
3. **Created:** four experiments/stage_02 scripts (collect sources/alternative, build, report);
   src/data_audit/doping_review.py; tests/stage_02/test_doping_review.py; raw doping sources;
   doping_review_v1_0_0 data; run_004 logs/results; this report directory.
4. **Modified:** docs/progress.md and scoped .gitattributes. Earlier code/data/results preserved.
5. **Methods:** primary-text/abstract review, metadata resolution, hashes and passage anchors;
   typed units, explicit bounds/ranges, specimen identity. No new prediction algorithm.
6. **Actual results:** three leads, seven quantities distinguished. No new complete doping
   case or held-out case. Earlier two substitution development references unchanged.
7. **Executed edge cases:** 29 new tests; total 172 passing tests, zero failures,
   errors or skips. Detailed cases in implementation_and_validation.md; overwrite refusal logged.
8. **Validation:** same cached review rebuilds identically; 191 previous tracked files
   checked. Software/local reproducibility verified for tested scope. Scientific adjudication pending.
9. **Known issues:** local full-text routes blocked; Mg study explicitly lacks electrical
   characterization of actual study specimens; Si/Nb full contextual evidence unavailable.
10. **Scientific limits:** no activation efficiency, calibrated probability, recommendation
    accuracy, property preservation or generalization result established.
11. **Incomplete:** matched site/concentration/transport cases; independent expert review;
    representative held-out benchmark and later implementation stages. All 23 broad old assertions
    remain withheld. Earlier Stage 1 engine issues remain unresolved until Stage 3.
12. **Telugu:** complete narration script in telugu_transcript.md. No playable audio generated.
13. **Readiness:** this source-review pass is delivered. Stage 2 scientific benchmark remains
    incomplete; Stage 3 not started. A stage transition still requires informed owner approval.

Tables are used instead of a misleading numeric comparison plot because the quantities
have different units/populations and no MATRA predictions were produced. Source extraction
is honestly marked as web text, with partial coverage, not a downloaded PDF.
