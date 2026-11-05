"""Checkpoint the approved partial review prototype before implementation."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
GIT = r'C:\Users\Suraj Vasireddy\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe'


def main():
    for directory in ('results/stage_04/run_001', 'logs/stage_04/run_001', 'work/stage_04', 'docs/stages/stage_04'):
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    names = subprocess.check_output([GIT, 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    paths = {p for p in names if p} | {p.name for p in ROOT.iterdir() if p.is_file()}
    result = {'baseline_commit': subprocess.check_output([GIT, 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
              'sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sorted(paths) if (ROOT / p).is_file()},
              'scope': 'Stage 4 fusion/evaluation plus limited local review demo requested for Nov 7 code review; complete scientific integration remains pending'}
    with (ROOT / 'results/stage_04/run_001/starting_checkpoint.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps({'commit': result['baseline_commit'], 'protected_files': len(result['sha256'])}))


if __name__ == '__main__': main()
