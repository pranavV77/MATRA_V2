# Task 2 Independent Similarity Benchmark Summary

## Overall Benchmark Performance (N = 11 Primary Cases, 18 Ground-Truth Targets)

| Method | Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR | Mean Best Rank | Mean Recall@10 |
|---|---|---|---|---|---|---|---|
| **PN** | 63.6% | 100.0% | 100.0% | 100.0% | 0.8182 | 1.36 | 97.0% |
| **Atom2Vec** | 63.6% | 81.8% | 81.8% | 100.0% | 0.7516 | 2.36 | 100.0% |
| **Property** | 36.4% | 72.7% | 90.9% | 100.0% | 0.5394 | 3.09 | 78.8% |

## Pairwise Method Top-10 Jaccard Overlap

| Pairwise Comparison | Mean Top-10 Jaccard Index |
|---|---|
| PN vs Atom2Vec | 0.2347 |
| PN vs Property | 0.3341 |
| Atom2Vec vs Property | 0.1906 |

## Headline Demonstration: beta-Ga2O3 -> Ga

| Rank | PN Candidate (Sim) | Atom2Vec Candidate (Sim) | Property Candidate (Sim) |
|---|---|---|---|
| 1 | **Al** (0.5000) | **Al** (0.8462) | **In** (0.8771) |
| 2 | **In** (0.5000) | **In** (0.7601) | **Sn** (0.8389) |
| 3 | **B** (0.3333) | **Y** (0.7573) | **Ge** (0.7352) |
| 4 | **Tl** (0.3333) | **Bi** (0.6505) | **P** (0.6226) |
| 5 | **C** (0.2000) | **La** (0.6175) | **Tl** (0.6177) |
| 6 | **Hg** (0.2000) | **Sn** (0.6046) | **Bi** (0.6172) |
| 7 | **Cd** (0.1667) | **Sb** (0.5698) | **Pb** (0.5930) |
| 8 | **Si** (0.1667) | **Ti** (0.5373) | **Sb** (0.5788) |
| 9 | **Ge** (0.1429) | **Sc** (0.4963) | **S** (0.5427) |
| 10 | **Zn** (0.1429) | **Zn** (0.4661) | **Se** (0.5259) |
