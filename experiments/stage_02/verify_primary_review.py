"""Read-only checks plus a fresh manifest; refuses to overwrite verification."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.stage_02.build_primary_review import build_release
from src.data_audit.primary_evidence import validate_primary_evidence


def main():
    final = ROOT / 'data/benchmark/v2_1_0/primary_evidence_reviewed.json'
    release = json.loads(final.read_text(encoding='utf-8'))
    assert build_release() == release
    counts = validate_primary_evidence(release, ROOT)
    index = ROOT / 'docs/stages/stage_02_source_verification/index.html'
    links = re.findall(r'(?:href|src)="([^"]+)"', index.read_text(encoding='utf-8'))
    if not all((index.parent / link).is_file() for link in links):
        raise ValueError('Broken report link')
    directories = ['data/raw/stage_02_primary_sources', 'data/benchmark/v2_1_0',
                   'docs/stages/stage_02_source_verification']
    files = [p for directory in directories for p in sorted((ROOT / directory).rglob('*')) if p.is_file()]
    files += [ROOT / 'src/data_audit/primary_evidence.py', ROOT / 'tests/stage_02/test_primary_evidence.py']
    files += sorted((ROOT / 'experiments/stage_02').glob('*primary*.py'))
    hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    result = {'evidence_counts': counts, 'report_links_verified': len(links), 'artifact_hashes': hashes,
              'dependencies': {name: importlib.metadata.version(name) for name in ('numpy', 'pandas', 'pymatgen', 'pytest', 'matplotlib')},
              'parameters': {'ranking_run': False, 'training_run': False, 'new_dft_run': False,
                             'admission_conditions': ['host', 'phase', 'site', 'concentration'],
                             'unknown_is_negative': False, 'substitution_doping_separate': True}}
    output = ROOT / 'results/stage_02/run_002/final_manifest.json'
    with output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    print(json.dumps({'artifacts_hashed': len(hashes), 'links_verified': len(links), 'evidence_counts': counts}))


if __name__ == '__main__':
    main()
