"""Retrieve public doping-source leads without overwriting earlier runs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
GIT = r'C:\Users\Suraj Vasireddy\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe'
PDF_PYTHON = r'C:\Users\Suraj Vasireddy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
RAW = ROOT / 'data/raw/stage_02_doping_sources'
SOURCES = [
    ('Mg_GaN_channeling', '10.1103/PhysRevLett.118.095501', 'https://cds.cern.ch/record/2242570/files/CERN-OPEN-2017-005.pdf'),
    ('Nb_STO_interstitial', '10.1021/nn401101y', 'https://pubs.acs.org/doi/pdf/10.1021/nn401101y'),
    ('Si_Ga_STM', '10.1063/1.3578195', 'https://pubs.aip.org/aip/apl/article/98/14/142116/340248/Atomically-resolved-silicon-donor-states-of-Ga2O3'),
]


def save_json(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)


def main():
    for directory in ('data/raw/stage_02_doping_sources', 'results/stage_02/run_004',
                      'logs/stage_02/run_004', 'work/stage_02/doping_review', 'docs/stages/stage_02_doping_review'):
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    if (RAW / 'acquisition_manifest.json').exists(): raise FileExistsError('Acquisition recorded already')
    tracked = subprocess.check_output([GIT, 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    save_json(ROOT / 'results/stage_02/run_004/starting_hashes.json',
              {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in tracked if p and (ROOT / p).is_file()})
    records = []
    for sid, doi, url in SOURCES:
        record = {'source_id': sid, 'candidate_doi': doi, 'requested_url': url,
                  'utc': datetime.now(timezone.utc).isoformat(), 'artifacts': [], 'errors': []}
        print('Retrieving', sid, flush=True)
        for step, link in [('metadata', 'https://api.crossref.org/works/' + doi), ('paper', url)]:
            try:
                req = urllib.request.Request(link, headers={'User-Agent': 'MATRA local source review/0.4'})
                with urllib.request.urlopen(req, timeout=25) as response:
                    data = response.read()
                    content_type = response.headers.get('Content-Type', '')
                if step == 'metadata':
                    path = RAW / (sid + '_metadata.json')
                    save_json(path, json.loads(data))
                elif data.startswith(b'%PDF'):
                    path = RAW / (sid + '.pdf')
                    with path.open('xb') as stream: stream.write(data)
                    extracted = RAW / (sid + '_pages.txt')
                    code = ('from pypdf import PdfReader; import sys; '
                            'r=PdfReader(sys.argv[1]); '
                            't="\\n".join("--- PAGE %d ---\\n%s"%(i+1,p.extract_text()) for i,p in enumerate(r.pages)); '
                            'f=open(sys.argv[2],"x",encoding="utf-8");f.write(t);f.close()')
                    subprocess.run([PDF_PYTHON, '-c', code, str(path), str(extracted)], check=True, timeout=45)
                    record['artifacts'].append({'path': extracted.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(extracted.read_bytes()).hexdigest()})
                    record['access'] = 'pdf_requires_scoped_review'
                else:
                    path = RAW / (sid + '_response.html')
                    with path.open('xb') as stream: stream.write(data)
                    record['access'] = 'non_pdf_response_requires_review'
                    record['content_type'] = content_type
                record['artifacts'].append({'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
            except Exception as exc:
                record['errors'].append({'step': step, 'error': str(exc)})
        records.append(record)
    save_json(RAW / 'acquisition_manifest.json', records)
    print(json.dumps(records, indent=2))


if __name__ == '__main__': main()
