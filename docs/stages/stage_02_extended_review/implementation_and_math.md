# Files, execution and scientific bookkeeping

The legacy code and v2.0/v2.1 releases are unchanged. New work is additive:

| File | Responsibility / inputs / outputs |
|---|---|
| experiments/stage_02/collect_extended_sources.py | Public PDF requests, local extraction through bundled pypdf; writes raw snapshots, retrieval errors and starting hashes once |
| experiments/stage_02/build_extended_review.py | Prior ledger + reviewed passages -> v2.2 JSON and readiness counts; refuses overwrite |
| src/data_audit/evidence_extension.py | Reuses the unchanged v2.1 admission policy; checks parent hashes, inherited decisions, host-family grouping, all 23 legacy identities, conditional observations and source-table arithmetic |
| tests/stage_02/test_evidence_extension.py | Real source-backed success checks and 38 new boundary/adversarial test cases |
| experiments/stage_02/report_extended_review.py | Actual JUnit + ledger -> reports, two figures, preservation checks and a reproducibility manifest |

`validate_extended_review` verifies data lineage and admission rules; it cannot independently
prove the scientific interpretation. Its output is a dictionary of counts, not accuracy.
`weighted_site_composition` sums occupancy times multiplicity on the listed sites. It does
not construct structures, calculate energies, predict site preferences or validate symmetry.
No new package was installed. Local dependencies are recorded in run_003/verification.json.

## Why site multiplicity matters

Occupancy means the fraction of equivalent positions filled by an element. Multiplicity
means how many such positions occur in the crystallographic cell. For element E,

    N_E = sum over sites j of (m_j * o_E,j)
    f_E = N_E / sum over listed sites j of m_j

N_E is a model atom count, m_j is site multiplicity, o_E,j is occupancy (between 0 and 1),
and f_E is the fraction on the listed sublattice. Each fully occupied site's element fractions
must sum to one. This version deliberately rejects vacancy-bearing tables instead of silently
renormalizing them; vacancies need a separately reviewed convention.

For the source's hexagonal-cell chalcogen sites:

- Outer 6c: 6 * 0.043 = 0.258 modeled Se atoms.
- Inner 3a: 3 * 0.915 = 2.745 modeled Se atoms.
- Total: 3.003 Se atoms on 9 chalcogen positions, giving 0.333666... Se fraction.
- Dividing the cell counts by three formula units gives approximately Bi2Te1.999Se1.001,
  consistent with the nominal Bi2Te2Se model within the reported refinement precision.

This is arithmetic on the reported model, not an independent chemical measurement.
The source fit constrains composition; the calculation is a consistency check, not independent
validation. Nominal Se/(Se+Te) is 1/3; nominal Se/all-atoms would be 1/5. These bases differ.

The notation 0.915(14) means 0.915 with reported refinement uncertainty 0.014, not 91.5%
MATRA confidence. The plot uses these source uncertainties directly. A combined uncertainty
for the derived composition is not calculated because refinement covariances are unavailable.

## How to run and verify

From C:Final Project, run a fresh test directory:

    .venvScriptspython.exe -m pytest tests --basetemp="C:Final Projectworkstage_02extended_reviewpytest_NEW" -q

pytest clears its selected base directory, so choose a new name. Archived actual tests are
logs/stage_02/run_003/pytest.xml and pytest.txt. For a read-only ledger check:

    .venvScriptspython.exe -c "from pathlib import Path; import json; from src.data_audit.evidence_extension import validate_extended_review; p=Path.cwd(); print(validate_extended_review(json.loads((p/'data/benchmark/v2_2_0/extended_evidence.json').read_text(encoding='utf-8')),p))"

No new ledger is automatically activated in production recommendation engines. Rollback is
to continue using the previous release; no migration or deletion is needed. Scoped .gitattributes
rules preserve exact evidence-file bytes across Git checkouts. Unrelated existing user files
and the earlier dirty result remain excluded from this stage's commit.
