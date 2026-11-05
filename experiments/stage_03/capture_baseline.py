"""Preserve pre-change engine behavior and tracked-file hashes once."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
GIT = r'C:\Users\Suraj Vasireddy\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe'


def main():
    out = ROOT / 'results/stage_03/run_001'
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'baseline.json').exists(): raise FileExistsError('Baseline already captured')
    for directory in ('logs/stage_03/run_001', 'work/stage_03', 'docs/stages/stage_03'):
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    tracked = subprocess.check_output([GIT, 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    paths = {p for p in tracked if p}
    paths.update(p.name for p in ROOT.iterdir() if p.is_file())
    hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths if (ROOT / p).is_file()}
    with (out / 'starting_hashes.json').open('x', encoding='utf-8') as f: json.dump(hashes, f, indent=2)
    backup = out / 'original_engines'
    backup.mkdir()
    files = ['src/pn_similarity/pn_engine.py', 'src/property_similarity/property_engine.py', 'src/atom2vec/atom2vec_engine.py']
    for name in files: shutil.copy2(ROOT / name, backup / Path(name).name)
    from src.pn_similarity.pn_engine import PNSimilarityEngine
    from src.property_similarity.property_engine import PropertySimilarityEngine
    from src.atom2vec.atom2vec_engine import Atom2VecEngine
    engines = {'PN': PNSimilarityEngine(), 'Property': PropertySimilarityEngine(), 'Atom2Vec': Atom2VecEngine()}
    result = {}
    for name, engine in engines.items():
        symbols = list(engine.pn_dict if name == 'PN' else engine.sym2idx if name == 'Property' else engine.atom2idx)
        result[name] = {'symbols': symbols, 'top10': {s: engine.get_top_k(s) for s in symbols},
                        'similarity_matrix': [[engine.compute_similarity(a, b) for b in symbols] for a in symbols]}
    with (out / 'baseline.json').open('x', encoding='utf-8') as f: json.dump(result, f, indent=2, allow_nan=False)
    environment = {'python': sys.version, 'operating_system': platform.platform(), 'disk_free_bytes': shutil.disk_usage(ROOT).free,
                   'git_head': subprocess.check_output([GIT, 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
                   'dependencies': {p: importlib.metadata.version(p) for p in ('numpy', 'pandas', 'scipy', 'pymatgen', 'pytest', 'pyarrow')}}
    with (out / 'environment.json').open('x', encoding='utf-8') as f: json.dump(environment, f, indent=2)
    print(json.dumps({'location': str(ROOT), **environment, 'supported_targets': {name: len(data['symbols']) for name, data in result.items()}}))


if __name__ == '__main__': main()
