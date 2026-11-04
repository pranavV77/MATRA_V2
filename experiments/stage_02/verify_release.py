"""Verify release integrity, original-file preservation and local report links."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
OUT=ROOT/'results/stage_02/run_001';DEST=OUT/'final_verification.json'
if DEST.exists():raise FileExistsError('Final verification already recorded')
from src.data_audit.validation import load_json
from src.data_audit.release import digest

before=load_json(OUT/'original_tracked_hashes.json')
changed=[p for p,h in before.items() if not (ROOT/p).is_file() or digest(ROOT/p)!=h]
manifest=load_json(ROOT/'data/processed/v2_0_0/release_manifest.json')
bad_release=[p for p,h in manifest['files'].items() if not (ROOT/p).is_file() or digest(ROOT/p)!=h]
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        self.links.extend(value for key,value in attrs if key in ('src','href'))
index=ROOT/'docs/stages/stage_02/index.html';parser=Links();parser.feed(index.read_text(encoding='utf-8'))
bad_links=[p for p in parser.links if not p.startswith(('http:','https:','#')) and not (index.parent/p).resolve().is_file()]
scripts=list((ROOT/'src/data_audit').glob('*.py'))+list((ROOT/'experiments/stage_02').glob('*.py'))+list((ROOT/'tests/stage_02').glob('*.py'))
for p in scripts:compile(p.read_text(encoding='utf-8'),str(p),'exec')
json_files=list((ROOT/'data/raw/stage_02_sources').glob('*.json'))+list((ROOT/'data/processed/v2_0_0').glob('*.json'))+list((ROOT/'data/benchmark/v2_0_0').glob('*.json'))+list(OUT.glob('*.json'))
for p in json_files:load_json(p)
git=r'C:\Users\Suraj Vasireddy\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe'
status=subprocess.check_output([git,'--no-optional-locks','status','--short','--branch'],cwd=ROOT,text=True)
(OUT/'git_status_after.txt').write_text(status,encoding='utf-8')
result={'original_tracked_files_checked':len(before),'original_tracked_files_changed':changed,
    'release_hash_mismatches':bad_release,'local_links_checked':len(parser.links),'missing_links':bad_links,
    'python_files_compiled':len(scripts),'strict_json_files_checked':len(json_files),
    'figures_visually_checked':['native_missingness.png','radius_estimation.png','benchmark_evidence_status.png'],
    'scientific_benchmark_ready':False,'audio_generated':False,'engineering_integrity_pass':not changed and not bad_release and not bad_links}
DEST.write_text(json.dumps(result,indent=2),encoding='utf-8')
paths=[]
for folder in ['src/data_audit','experiments/stage_02','tests/stage_02','data/raw/stage_02_sources','data/processed/v2_0_0','data/benchmark/v2_0_0','docs/stages/stage_02','results/stage_02/run_001','logs/stage_02/run_001']:
    paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file())
paths.append(ROOT/'docs/progress.md')
(OUT/'stage_file_inventory.json').write_text(json.dumps({str(p.relative_to(ROOT)):digest(p) for p in sorted(paths)},indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
raise SystemExit(0 if result['engineering_integrity_pass'] else 1)
