"""Non-destructive Stage 1 audit. Run with the existing project interpreter.

Inputs: existing src/, tests/, data/, docs/ and recorded benchmark results.
Outputs: a NEW results/stage_01/<run-id>/ tree; originals are never rewritten.
This diagnostic runner reports observed baseline defects without fixing them.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
GIT = Path(r"C:\Users\Suraj Vasireddy\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2, allow_nan=False)


def invoke(command, cwd, log, timeout=180):
    start = time.perf_counter()
    result = subprocess.run(command, cwd=cwd, env=os.environ.copy(),
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=timeout)
    log.write_text(result.stdout + "\nSTDERR:\n" + result.stderr, encoding="utf-8")
    return {"command": list(map(str, command)), "cwd": str(cwd),
            "exit_code": result.returncode, "seconds": time.perf_counter()-start,
            "log": str(log.relative_to(ROOT))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.run_id):
        parser.error("run-id must be a simple directory name")
    out = ROOT / "results" / "stage_01" / args.run_id
    out.mkdir(parents=True, exist_ok=True)
    if (out / "audit_started.json").exists():
        raise FileExistsError("This run already started. Choose a NEW run-id.")
    os.chdir(ROOT)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["PYTHONUTF8"] = "1"
    os.environ["MPLCONFIGDIR"] = str(out / "matplotlib_cache")
    temp = out / "temp"
    temp.mkdir()
    os.environ["TMP"] = os.environ["TEMP"] = str(temp)
    write_json(out / "audit_started.json", {"utc": datetime.now(timezone.utc).isoformat(),
               "root": str(ROOT), "scope": "Stage 1 baseline audit only"})

    # Preserve all tracked files plus root-level untracked presentations/scripts.
    tracked = subprocess.check_output([str(GIT), "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    originals = {p for p in tracked if p}
    originals.update(p.name for p in ROOT.iterdir() if p.is_file())
    before = {p: sha(ROOT/p) for p in sorted(originals) if (ROOT/p).is_file()}
    write_json(out / "original_hashes_before.json", before)
    backup = out / "preserved_original_results"
    shutil.copytree(ROOT / "results" / "runs", backup / "runs")
    shutil.copytree(ROOT / "results" / "tables", backup / "tables")
    packages = sorted((d.metadata.get("Name", ""), d.version)
                      for d in importlib.metadata.distributions())
    write_json(out / "environment.json", {"python": sys.version, "executable": sys.executable,
        "platform": platform.platform(), "packages": dict(packages),
        "disk_free_bytes": shutil.disk_usage(ROOT).free,
        "git_executable": str(GIT), "source_commit": subprocess.check_output(
            [str(GIT), "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()})

    print("Running the existing test suite...", flush=True)
    tests = invoke([sys.executable, "-B", "-X", "utf8", "-m", "pytest", "tests", "-v",
                    "-p", "no:cacheprovider", "--basetemp", str(temp / "pytest"),
                    "--junitxml", str(out / "existing_tests.xml")], ROOT,
                   out / "existing_tests.txt")
    write_json(out / "existing_tests_execution.json", tests)

    import numpy as np
    import pandas as pd
    import pymatgen.core as mg
    from src.pn_similarity.pn_engine import PNSimilarityEngine
    from src.atom2vec.atom2vec_engine import Atom2VecEngine
    from src.property_similarity.property_engine import PropertySimilarityEngine

    print("Checking dataset integrity and source conventions...", flush=True)
    master = pd.read_parquet(ROOT / "data/processed/elements_master.parquet")
    meta = json.loads((ROOT / "data/processed/feature_metadata.json").read_text(encoding="utf-8-sig"))
    bench = json.loads((ROOT / "data/benchmark/benchmark_cases.json").read_text(encoding="utf-8-sig"))
    manifest = (ROOT / "docs/Task_1_2_Milestone_Manifest.md").read_text(encoding="utf-8-sig")
    checksums = []
    for line in manifest.splitlines():
        match = re.search(r"`([^`]+)`.*`([0-9a-f]{64})`", line)
        if match:
            path, expected = match.groups()
            actual = sha(ROOT/path)
            checksums.append({"path": path, "expected": expected, "actual": actual,
                              "matches": actual == expected})
    with gzip.open(ROOT / "data/raw/mp_nostruct_20181018.json.gz", "rt", encoding="utf-8") as f:
        raw = json.load(f)
    from mendeleev.models import Element
    write_json(out / "dataset_audit.json", {
        "shape": list(master.shape), "duplicate_symbols": int(master.symbol.duplicated().sum()),
        "missing_by_column": {k: int(v) for k,v in master.isna().sum().items() if v},
        "imputed_elements": master.loc[master.has_imputed_values, "symbol"].tolist(),
        "pn_min": int(master.mendeleev_number.min()), "pn_max": int(master.mendeleev_number.max()),
        "pn_normalized_max": float(master.pn_normalized.max()),
        "metadata_pn_range": meta["pn_convention"]["range"], "checksums": checksums,
        "raw_records": len(raw["data"]), "raw_columns": raw["columns"],
        "raw_duplicate_formulas": len(raw["data"])-len(set(row[raw["columns"].index("formula")] for row in raw["data"])),
        "primary_cases": len(bench["primary_cases"]),
        "primary_positive_entries": sum(len(c["known_substituents"]) for c in bench["primary_cases"]),
        "unique_primary_targets": sorted({c["target_element"] for c in bench["primary_cases"]}),
        "secondary_cases": len(bench["secondary_doping_cases"]),
        "installed_mendeleev_polarizability_doc": [s.strip() for s in Element.__doc__.splitlines() if "dipole_polarizability" in s],
        "scientific_reference_claims": "Not independently certified by JSON/schema tests"})

    print("Reproducing benchmark in a protected local workspace...", flush=True)
    workspace = out / "legacy_workspace"
    shutil.copytree(ROOT / "src", workspace / "src", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / "data", workspace / "data")
    benchmark = invoke([sys.executable, "-B", "-X", "utf8", "-m", "src.benchmark.evaluate_benchmark"],
                       workspace, out / "benchmark_execution.txt")
    write_json(out / "benchmark_execution.json", benchmark)
    reproduced = json.loads((workspace/"results/runs/task2_benchmark_evaluation.json").read_text())
    original = json.loads((ROOT/"results/runs/task2_benchmark_evaluation.json").read_text())
    compare_fields = ["summary_metrics", "pairwise_jaccard_overlap", "ga2o3_headline_demonstration", "detailed_case_evaluations"]
    comparison = {field: reproduced[field] == original[field] for field in compare_fields}
    write_json(out / "benchmark_comparison.json", {"equal_fields_excluding_metadata": comparison,
        "summary_metrics": reproduced["summary_metrics"],
        "note": "Timestamp changes are expected. This is legacy retrospective retrieval, not independent chemistry validation."})

    engines = {"PN": PNSimilarityEngine(), "Atom2Vec": Atom2VecEngine(), "Property": PropertySimilarityEngine()}
    records = []
    def probe(name, requirement, action, accept):
        start = time.perf_counter()
        try:
            value = action()
            observation = {"returned": value}
            passed = bool(accept(value, None))
        except Exception as exc:
            observation = {"exception": type(exc).__name__, "message": str(exc)}
            passed = bool(accept(None, exc))
        records.append({"name": name, "requirement": requirement,
                        "status": "passed" if passed else "failed",
                        "observation": observation, "seconds": time.perf_counter()-start})

    print("Executing coverage and edge-case probes...", flush=True)
    coverage = []
    for z in range(1,119):
        symbol = str(mg.Element.from_Z(z))
        row = {"atomic_number": z, "symbol": symbol}
        for name, engine in engines.items():
            try:
                ranked = engine.get_top_k(symbol, 10)
                row[name] = "supported" if (len(ranked)==10 and len({v['candidate_element'] for v in ranked})==10
                    and symbol not in [v['candidate_element'] for v in ranked]
                    and all(np.isfinite(v['similarity_score']) for v in ranked)) else "invalid_output"
            except ValueError:
                row[name] = "unsupported"
        coverage.append(row)
    write_json(out / "element_coverage.json", coverage)
    invalid_inputs = ["", "Xx", "ga", " Ga ", "Ga2O3", None, 31, [], {}]
    for name, engine in engines.items():
        for i, target in enumerate(invalid_inputs):
            probe(f"{name}:invalid_target:{i}", "Reject invalid target explicitly", lambda e=engine,t=target:e.get_top_k(t),
                  lambda v,e:isinstance(e,(ValueError,TypeError)))
        for k in [0,1,1000]:
            universe = len(engine.candidate_elements) if name=="PN" else len(engine.common_symbols) if name=="Atom2Vec" else len(engine.symbols)
            probe(f"{name}:k={k}", "Return min(k, available candidates), no target", lambda e=engine,k=k:e.get_top_k("Ga",k),
                  lambda v,e,k=k,n=universe:e is None and len(v)==min(k,n-1))
        for k in [-1,1.5,"10",True]:
            probe(f"{name}:invalid_k:{repr(k)}", "Reject negative, noninteger or boolean k", lambda e=engine,k=k:e.get_top_k("Ga",k),
                  lambda v,e:isinstance(e,(ValueError,TypeError)))
        probe(f"{name}:repeat", "Same input produces identical rankings", lambda e=engine:e.get_top_k("Ga")==e.get_top_k("Ga"), lambda v,e:v is True)
        symbols = list(engine.pn_dict) if name=="PN" else engine.common_symbols if name=="Atom2Vec" else engine.symbols
        pairs = [(a,b) for a in symbols for b in symbols]
        asym = max(abs(engine.compute_similarity(a,b)-engine.compute_similarity(b,a)) for a,b in pairs)
        selferr = max(abs(engine.compute_similarity(a,a)-1) for a in symbols)
        probe(f"{name}:all_pair_symmetry", "Symmetry within 1e-12", lambda a=asym:a, lambda v,e:v<=1e-12)
        probe(f"{name}:all_self_similarity", "Self similarity within 1e-12", lambda a=selferr:a, lambda v,e:v<=1e-12)
    fixture_dir = out / "fixtures"
    fixture_dir.mkdir()
    missing = fixture_dir / "missing.parquet"
    for cls in [PNSimilarityEngine,PropertySimilarityEngine]:
        probe(f"{cls.__name__}:missing_file", "Reject missing dataset", lambda c=cls:c(str(missing)),lambda v,e:isinstance(e,FileNotFoundError))
    variants = {}
    variants["duplicate"] = pd.concat([master,master[master.symbol=="Ga"]],ignore_index=True)
    variants["empty"] = master.iloc[:0].copy()
    variants["missing_feature"] = master.drop(columns=["density"])
    variants["nan_feature"] = master.copy(); variants["nan_feature"].loc[master.symbol=="Ga","density"] = np.nan
    variants["infinite_feature"] = master.copy(); variants["infinite_feature"].loc[master.symbol=="Ga","density"] = np.inf
    variants["negative_density"] = master.copy(); variants["negative_density"].loc[master.symbol=="Ga","density"] = -1.0
    variants["invalid_type"] = master.copy(); variants["invalid_type"]["density"] = variants["invalid_type"].density.astype(object); variants["invalid_type"].loc[master.symbol=="Ga","density"]="bad"
    for label, frame in variants.items():
        path = fixture_dir/f"{label}.parquet"
        if label=="invalid_type":
            frame["density"]=frame["density"].astype(str)
        frame.to_parquet(path,index=False)
        probe(f"Property:{label}", "Reject invalid master dataset before scoring", lambda p=path:PropertySimilarityEngine(str(p)).get_top_k("Ga"),
              lambda v,e:e is not None)
        if label in ("duplicate","empty"):
            probe(f"PN:{label}", "Reject invalid master dataset", lambda p=path:PNSimilarityEngine(str(p)).get_top_k("Ga"),lambda v,e:e is not None)
    malformed = fixture_dir / "malformed.parquet"; malformed.write_bytes(b"not parquet")
    probe("Property:malformed_file", "Reject corrupt file", lambda:PropertySimilarityEngine(str(malformed)),lambda v,e:e is not None)
    badcache=fixture_dir/"bad_cache.npz"
    np.savez_compressed(badcache,common_symbols=np.array(["Ga","Al"]),F_norm=np.array([[np.nan,0],[1,0]]))
    probe("Atom2Vec:nan_cache", "Reject nonfinite cached vectors before scoring", lambda:Atom2VecEngine(cache_embedding_path=str(badcache)).get_top_k("Ga"),lambda v,e:e is not None)
    np.savez_compressed(fixture_dir/"shape_cache.npz",common_symbols=np.array(["Ga","Al"]),F_norm=np.array([[1.,0.]]))
    probe("Atom2Vec:shape_cache", "Reject symbol/vector shape mismatch",lambda:Atom2VecEngine(cache_embedding_path=str(fixture_dir/"shape_cache.npz")).get_top_k("Ga"),lambda v,e:e is not None)
    probe("Atom2Vec:missing_corpus", "Reject missing corpus when cache absent",lambda:Atom2VecEngine(raw_mp_path=str(fixture_dir/"none.gz"),cache_embedding_path=str(fixture_dir/"none.npz")),lambda v,e:isinstance(e,FileNotFoundError))
    # A requested dimensionality must not silently use a different cached model.
    probe("Atom2Vec:cache_dimension", "Requested embedding dimension agrees with loaded cache",lambda:Atom2VecEngine(embedding_dim=10).F_norm.shape[1],lambda v,e:v==10)
    # NaN observations in diagnostic payloads are represented explicitly as strings.
    for record in records:
        if isinstance(record["observation"].get("returned"), list):
            record["observation"]["returned"] = json.loads(json.dumps(record["observation"]["returned"]).replace("NaN",'"NaN"').replace("Infinity",'"Infinity"'))
    write_json(out / "edge_case_results.json", records)

    print("Attempting fresh master-table rebuild in isolation...", flush=True)
    rebuild_code = "from src.features.build_elements_master import build_elements_master; build_elements_master('rebuild/elements_master.parquet','rebuild/feature_metadata.json')"
    rebuild = invoke([sys.executable,"-B","-X","utf8","-c",rebuild_code],workspace,out/"master_rebuild.txt",timeout=240)
    if rebuild["exit_code"]==0:
        rebuilt=pd.read_parquet(workspace/"rebuild/elements_master.parquet")
        rebuild["values_equal_to_original"]=rebuilt.equals(master)
    write_json(out/"master_rebuild_execution.json",rebuild)

    print("Retraining Atom2Vec without the original cache...", flush=True)
    training_code = "from src.atom2vec.atom2vec_engine import Atom2VecEngine; import json; e=Atom2VecEngine(cache_embedding_path='fresh/embeddings.npz'); print(json.dumps({'shape':list(e.F_norm.shape),'ga':e.get_top_k('Ga')}))"
    training=invoke([sys.executable,"-B","-X","utf8","-c",training_code],workspace,out/"atom2vec_retraining.txt",timeout=240)
    if training["exit_code"]==0:
        fresh=np.load(workspace/"fresh/embeddings.npz",allow_pickle=False)
        saved=np.load(ROOT/"data/processed/atom2vec_embeddings_d20.npz",allow_pickle=False)
        same_symbols=np.array_equal(fresh["common_symbols"],saved["common_symbols"])
        training["same_symbols"]=same_symbols
        training["shape"]=list(fresh["F_norm"].shape)
        if same_symbols:
            gram_fresh=fresh["F_norm"]@fresh["F_norm"].T; gram_saved=saved["F_norm"]@saved["F_norm"].T
            training["maximum_pairwise_similarity_difference"]=float(np.max(np.abs(gram_fresh-gram_saved)))
            eng_fresh=Atom2VecEngine(cache_embedding_path=str(workspace/"fresh/embeddings.npz"))
            training["top10_equal_for_all_supported_targets"]=all(eng_fresh.get_top_k(s)==engines["Atom2Vec"].get_top_k(s) for s in eng_fresh.common_symbols)
    write_json(out/"atom2vec_retraining_execution.json",training)

    after = {p:sha(ROOT/p) for p in before}
    unchanged=before==after
    write_json(out/"original_hashes_after.json",after)
    summary={"legacy_tests":tests,"benchmark":benchmark,"benchmark_equal":comparison,
        "edge_probe_counts":{s:sum(r["status"]==s for r in records) for s in ["passed","failed"]},
        "edge_failures":[r["name"] for r in records if r["status"]=="failed"],
        "coverage_counts":{name:sum(r[name]=="supported" for r in coverage) for name in engines},
        "master_rebuild":rebuild,"atom2vec_retraining":training,
        "original_files_unchanged":unchanged,"original_files_checked":len(before),
        "status":"audit_executed_with_findings; not a clean scientific-validation pass"}
    write_json(out/"summary.json",summary)
    print(json.dumps(summary,indent=2),flush=True)
    return 0 if unchanged else 2


if __name__=="__main__":
    raise SystemExit(main())
