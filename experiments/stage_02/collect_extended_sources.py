"""Acquire additional public primary sources, never overwriting prior evidence."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data/raw/stage_02_extended_sources'
RUN = ROOT / 'results/stage_02/run_003'
GIT = Path(r'C:\Users\Suraj Vasireddy\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe')
EXTRACT_PYTHON = Path(r'C:\Users\Suraj Vasireddy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
SOURCES = [
    ('Sn_Ga_XAS', 'https://www.osti.gov/servlets/purl/1371047'),
    ('Nb_STO_polar', 'https://www.nature.com/articles/s41535-022-00524-9.pdf'),
    ('MoW_atomic', 'https://www.nature.com/articles/ncomms2351.pdf'),
    ('BiTeSe_structure', 'https://arxiv.org/pdf/1112.1648'),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    RUN.mkdir(parents=True, exist_ok=True)
    for directory in ('logs/stage_02/run_003', 'work/stage_02/extended_review',
                      'docs/stages/stage_02_extended_review', 'data/benchmark/v2_2_0'):
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    if (OUT / 'acquisition_manifest.json').exists():
        raise FileExistsError('Acquisition already recorded')
    tracked = subprocess.check_output([str(GIT), 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in tracked if p and (ROOT / p).is_file()}
    with (RUN / 'starting_hashes.json').open('x', encoding='utf-8') as stream:
        json.dump(hashes, stream, indent=2)
    records = []
    for sid, url in SOURCES:
        record = {'source_id': sid, 'url': url, 'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
                  'identity_status': 'candidate_unverified', 'artifacts': [], 'errors': []}
        print('Retrieving', sid, flush=True)
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'MATRA local academic source review/0.3'})
            with urllib.request.urlopen(request, timeout=25) as response:
                content = response.read()
                record['resolved_url'] = response.url
                record['content_type'] = response.headers.get('Content-Type')
            if not content.startswith(b'%PDF'):
                raise ValueError('Response is not a PDF; no full-text credit')
            pdf = OUT / (sid + '.pdf')
            with pdf.open('xb') as stream:
                stream.write(content)
            extraction = OUT / (sid + '_pages.txt')
            code = ('from pypdf import PdfReader; from pathlib import Path; import sys; '
                    'r=PdfReader(sys.argv[1]); '
                    't="\\n".join("--- PAGE %d ---\\n%s"%(i+1,p.extract_text()) for i,p in enumerate(r.pages)); '
                    'Path(sys.argv[2]).write_text(t,encoding="utf-8")')
            subprocess.run([str(EXTRACT_PYTHON), '-c', code, str(pdf), str(extraction)], check=True, timeout=45)
            for path in (pdf, extraction):
                record['artifacts'].append({'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
            record['identity_status'] = 'full_pdf_requires_identity_review'
        except Exception as exc:
            record['errors'].append(str(exc))
        records.append(record)
    with (OUT / 'acquisition_manifest.json').open('x', encoding='utf-8') as stream:
        json.dump(records, stream, indent=2)
    print(json.dumps(records, indent=2))


if __name__ == '__main__':
    main()
