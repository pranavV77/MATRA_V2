"""
Benchmark Evaluation Runner for Task 2.

Evaluates the three independent similarity engines (PN, Atom2Vec, Property)
across the 11 primary substitution benchmark cases (18 ground-truth targets).

Computes:
- Multi-target Hit@1, Hit@3, Hit@5, Hit@10
- Mean Reciprocal Rank (MRR)
- Mean Best Rank
- Mean Recall@10
- Pairwise Top-10 Jaccard Overlap

Outputs:
- Machine-readable JSON results in results/runs/task2_benchmark_evaluation.json
- Formatted Markdown tables in results/tables/
"""

import os
import json
import datetime
from typing import Dict, List, Any
import pandas as pd
import numpy as np

from src.pn_similarity.pn_engine import PNSimilarityEngine
from src.atom2vec.atom2vec_engine import Atom2VecEngine
from src.property_similarity.property_engine import PropertySimilarityEngine


def run_benchmark():
    benchmark_path = os.path.join("data", "benchmark", "benchmark_cases.json")
    with open(benchmark_path, "r", encoding="utf-8") as f:
        bench_data = json.load(f)
        
    primary_cases = bench_data["primary_cases"]
    secondary_cases = bench_data["secondary_doping_cases"]
    
    # Initialize engines
    pn_eng = PNSimilarityEngine()
    a2v_eng = Atom2VecEngine()
    prop_eng = PropertySimilarityEngine()
    
    engines = {
        "PN": pn_eng,
        "Atom2Vec": a2v_eng,
        "Property": prop_eng
    }
    
    detailed_case_results = []
    
    # Track metrics per method
    method_metrics = {
        m: {
            "hits_at_1": 0,
            "hits_at_3": 0,
            "hits_at_5": 0,
            "hits_at_10": 0,
            "reciprocal_ranks": [],
            "best_ranks": [],
            "recalls_at_10": []
        }
        for m in engines.keys()
    }
    
    # Pairwise overlap tracking
    jaccard_pairs = {
        ("PN", "Atom2Vec"): [],
        ("PN", "Property"): [],
        ("Atom2Vec", "Property"): []
    }
    
    for case in primary_cases:
        cid = case["case_id"]
        formula = case["formula"]
        target = case["target_element"]
        known_subs = set(case["known_substituents"])
        num_known = len(known_subs)
        
        case_res = {
            "case_id": cid,
            "material": formula,
            "target_element": target,
            "known_substituents": sorted(list(known_subs)),
            "rankings": {}
        }
        
        top10_by_method = {}
        
        for m_name, eng in engines.items():
            top10 = eng.get_top_k(target, k=10)
            top10_cands = [item["candidate_element"] for item in top10]
            top10_by_method[m_name] = set(top10_cands)
            
            # Evaluate against known substituents
            hits_in_top10 = [c for c in top10_cands if c in known_subs]
            ranks_of_known = [top10_cands.index(h) + 1 for h in hits_in_top10]
            
            best_rank = min(ranks_of_known) if ranks_of_known else 999
            rr = 1.0 / best_rank if best_rank != 999 else 0.0
            
            h1 = 1 if best_rank <= 1 else 0
            h3 = 1 if best_rank <= 3 else 0
            h5 = 1 if best_rank <= 5 else 0
            h10 = 1 if best_rank <= 10 else 0
            rec10 = len(hits_in_top10) / num_known
            
            method_metrics[m_name]["hits_at_1"] += h1
            method_metrics[m_name]["hits_at_3"] += h3
            method_metrics[m_name]["hits_at_5"] += h5
            method_metrics[m_name]["hits_at_10"] += h10
            method_metrics[m_name]["reciprocal_ranks"].append(rr)
            method_metrics[m_name]["best_ranks"].append(best_rank if best_rank != 999 else 88)
            method_metrics[m_name]["recalls_at_10"].append(rec10)
            
            case_res["rankings"][m_name] = {
                "top_10": top10,
                "hits": hits_in_top10,
                "best_rank": best_rank if best_rank != 999 else None,
                "reciprocal_rank": round(rr, 4),
                "recall_at_10": round(rec10, 4)
            }
            
        # Overlaps
        jaccard_pairs[("PN", "Atom2Vec")].append(
            len(top10_by_method["PN"] & top10_by_method["Atom2Vec"]) / len(top10_by_method["PN"] | top10_by_method["Atom2Vec"])
        )
        jaccard_pairs[("PN", "Property")].append(
            len(top10_by_method["PN"] & top10_by_method["Property"]) / len(top10_by_method["PN"] | top10_by_method["Property"])
        )
        jaccard_pairs[("Atom2Vec", "Property")].append(
            len(top10_by_method["Atom2Vec"] & top10_by_method["Property"]) / len(top10_by_method["Atom2Vec"] | top10_by_method["Property"])
        )
        
        detailed_case_results.append(case_res)
        
    N = len(primary_cases)
    summary_metrics = {}
    for m_name in engines.keys():
        mm = method_metrics[m_name]
        summary_metrics[m_name] = {
            "hit_at_1": round(mm["hits_at_1"] / N, 4),
            "hit_at_3": round(mm["hits_at_3"] / N, 4),
            "hit_at_5": round(mm["hits_at_5"] / N, 4),
            "hit_at_10": round(mm["hits_at_10"] / N, 4),
            "mrr": round(float(np.mean(mm["reciprocal_ranks"])), 4),
            "mean_best_rank": round(float(np.mean(mm["best_ranks"])), 2),
            "mean_recall_at_10": round(float(np.mean(mm["recalls_at_10"])), 4)
        }
        
    overlap_summary = {
        f"{pair[0]} vs {pair[1]}": round(float(np.mean(vals)), 4)
        for pair, vals in jaccard_pairs.items()
    }
    
    # Headline Ga2O3 -> Ga comparison
    ga_demo = {
        "material": "beta-Ga2O3",
        "target_element": "Ga",
        "target_site": "Octahedral Ga_II (4i)",
        "known_primary_substituents": ["Al", "In"],
        "known_secondary_dopants": ["Si", "Sn"],
        "rankings": {
            m_name: engines[m_name].get_top_k("Ga", k=10)
            for m_name in engines.keys()
        }
    }
    
    full_output = {
        "metadata": {
            "evaluation_name": "Task 2 Independent Similarity Benchmark Evaluation",
            "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
            "total_primary_cases": N,
            "total_verified_targets": sum(len(c["known_substituents"]) for c in primary_cases),
            "software_versions": {
                "mendeleev": "1.2.0",
                "pymatgen": "2025.10.7",
                "scipy": "1.15.3",
                "scikit-learn": "1.7.2",
                "pandas": "2.3.3"
            }
        },
        "summary_metrics": summary_metrics,
        "pairwise_jaccard_overlap": overlap_summary,
        "ga2o3_headline_demonstration": ga_demo,
        "detailed_case_evaluations": detailed_case_results
    }
    
    # Save outputs
    os.makedirs(os.path.join("results", "runs"), exist_ok=True)
    os.makedirs(os.path.join("results", "tables"), exist_ok=True)
    
    run_file = os.path.join("results", "runs", "task2_benchmark_evaluation.json")
    with open(run_file, "w", encoding="utf-8") as f:
        json.dump(full_output, f, indent=2)
    print(f"Saved machine-readable run results to {run_file}")
    
    # Generate Markdown Summary Tables
    md_table_path = os.path.join("results", "tables", "benchmark_metrics_summary.md")
    with open(md_table_path, "w", encoding="utf-8") as f:
        f.write("# Task 2 Independent Similarity Benchmark Summary\n\n")
        f.write("## Overall Benchmark Performance (N = 11 Primary Cases, 18 Ground-Truth Targets)\n\n")
        f.write("| Method | Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR | Mean Best Rank | Mean Recall@10 |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for m_name, sm in summary_metrics.items():
            f.write(f"| **{m_name}** | {sm['hit_at_1']:.1%} | {sm['hit_at_3']:.1%} | {sm['hit_at_5']:.1%} | {sm['hit_at_10']:.1%} | {sm['mrr']:.4f} | {sm['mean_best_rank']:.2f} | {sm['mean_recall_at_10']:.1%} |\n")
        f.write("\n## Pairwise Method Top-10 Jaccard Overlap\n\n")
        f.write("| Pairwise Comparison | Mean Top-10 Jaccard Index |\n|---|---|\n")
        for pair, val in overlap_summary.items():
            f.write(f"| {pair} | {val:.4f} |\n")
        f.write("\n## Headline Demonstration: beta-Ga2O3 -> Ga\n\n")
        f.write("| Rank | PN Candidate (Sim) | Atom2Vec Candidate (Sim) | Property Candidate (Sim) |\n")
        f.write("|---|---|---|---|\n")
        for r in range(10):
            pn_c = ga_demo["rankings"]["PN"][r]
            a2v_c = ga_demo["rankings"]["Atom2Vec"][r]
            pr_c = ga_demo["rankings"]["Property"][r]
            f.write(f"| {r+1} | **{pn_c['candidate_element']}** ({pn_c['similarity_score']:.4f}) | **{a2v_c['candidate_element']}** ({a2v_c['similarity_score']:.4f}) | **{pr_c['candidate_element']}** ({pr_c['similarity_score']:.4f}) |\n")
            
    print(f"Saved summary tables to {md_table_path}")
    return full_output


if __name__ == "__main__":
    run_benchmark()
