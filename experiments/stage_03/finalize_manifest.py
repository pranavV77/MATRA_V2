"""Preserve the report-time manifest and finalize byte-preserving Git checks."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/stage_03/run_001'
GIT = r'C:\Users\Suraj Vasireddy\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe'


def main():
    previous = json.loads((OUT / 'artifact_manifest.json').read_text(encoding='utf-8'))
    actual = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in previous['sha256']}
    differences = [name for name, checksum in actual.items() if checksum != previous['sha256'][name]]
    if differences != ['.gitattributes']:
        raise ValueError(f'Unexpected post-report changes: {differences}')
    this_file = Path(__file__)
    actual[this_file.relative_to(ROOT).as_posix()] = hashlib.sha256(this_file.read_bytes()).hexdigest()
    mismatches = [name for name, checksum in actual.items()
                  if hashlib.sha256(subprocess.check_output([GIT, 'show', ':'+name], cwd=ROOT)).hexdigest() != checksum]
    if mismatches: raise ValueError(f'Staged byte mismatches: {mismatches}')
    result = {'sha256': actual, 'report_links_verified': previous['report_links_verified'],
              'supersedes': 'artifact_manifest.json', 'reason': 'Scoped Git -text rules prevent CRLF normalization of hashed audit files; numerical results unchanged',
              'staged_hash_mismatches': mismatches}
    with (OUT / 'artifact_manifest_final.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps({'artifacts_checked': len(actual), 'staged_hash_mismatches': mismatches, 'report_links_verified': previous['report_links_verified']}))


if __name__ == '__main__': main()
