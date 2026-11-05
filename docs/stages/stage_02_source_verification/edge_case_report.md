# Executed edge cases

Final full suite: 105 tests, 0 failures, 0 errors,
0 skipped; runtime 2.930 seconds. This includes 32 new evidence tests
and 73 earlier tests. JUnit: logs/stage_02/run_002/pytest_final.xml.

Executed cases: empty source/claim collections; missing IDs; duplicate source and claim IDs;
invalid element and self-substitution; unknown label earning credit; missing phase verification;
boolean, NaN, negative and overfull concentrations; unknown units and missing concentration
basis; absent passage anchors and out-of-range source lines; altered source checksum;
path traversal; missing files and source references; metadata-only evidence; challenge page
with an otherwise valid checksum; unsupported property-preservation assertion; missing DOI;
incorrect URL/conditions/concentration types; deterministic rebuild; final saved/build equality;
retained legacy unknowns; retained incorrect retrieval identifier alongside corrected DOI.

First test invocation used a nonexistent tests/stage_01 folder: collection failed and no
tests executed. It is retained in pytest.txt/pytest.xml. Corrected invocation ran tests/.
A docstring escape warning was then fixed. Final invocation passed without warnings.

Not tested: authenticated publisher retrieval, arbitrary website formats, every malformed
nested JSON possibility, clean-machine installation, independent scientific adjudication,
chemistry generalization or future prediction performance. No chemical negatives fabricated.
