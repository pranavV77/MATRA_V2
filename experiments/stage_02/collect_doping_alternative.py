"""Use the publisher's public full-text endpoint; retain failed earlier requests."""
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import urllib.request
from experiments.stage_02.collect_doping_sources import RAW, PDF_PYTHON


def main():
    url = 'https://harvest.aps.org/v2/journals/articles/10.1103/PhysRevLett.118.095501/fulltext'
    pdf = RAW / 'Mg_GaN_channeling_publisher.pdf'
    extracted = RAW / 'Mg_GaN_channeling_publisher_pages.txt'
    record = RAW / 'publisher_alternative.json'
    if any(p.exists() for p in (pdf, extracted, record)): raise FileExistsError('Alternative outputs exist')
    data = urllib.request.urlopen(url, timeout=25).read()
    if not data.startswith(b'%PDF'): raise ValueError('Not PDF')
    with pdf.open('xb') as stream: stream.write(data)
    code = ('from pypdf import PdfReader;import sys;'
            'r=PdfReader(sys.argv[1]);t="\\n".join("--- PAGE %d ---\\n%s"%(i+1,p.extract_text()) for i,p in enumerate(r.pages));'
            'f=open(sys.argv[2],"x",encoding="utf-8");f.write(t);f.close()')
    subprocess.run([PDF_PYTHON, '-c', code, str(pdf), str(extracted)], check=True, timeout=45)
    with record.open('x', encoding='utf-8') as stream:
        json.dump({'url': url, 'utc': datetime.now(timezone.utc).isoformat(),
                   'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
                   'text_sha256': hashlib.sha256(extracted.read_bytes()).hexdigest()}, stream, indent=2)
    print('Publisher PDF saved and extracted; previous failed acquisition preserved.')


if __name__ == '__main__': main()
