"""Final integrity/format checks for Stage 1; no product algorithms run."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/stage_01/run_001'
target=OUT/'final_verification.json'
if target.exists():raise FileExistsError('Final verification already recorded')
before=json.loads((OUT/'original_hashes_before.json').read_text())
changed=[p for p,h in before.items() if not (ROOT/p).is_file() or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ('href','src'):self.links.append(value)
index=ROOT/'docs/stages/stage_01/index.html'
parser=Links();parser.feed(index.read_text(encoding='utf-8'))
missing_links=[v for v in parser.links if not v.startswith(('https:','http:','#')) and not (index.parent/v).resolve().is_file()]
json_count=0
for p in OUT.glob('*.json'):
    json.loads(p.read_text(encoding='utf-8-sig'),parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
    json_count+=1
compiled=[]
for p in (ROOT/'experiments/stage_01').glob('*.py'):
    compile(p.read_text(encoding='utf-8'),str(p),'exec');compiled.append(p.name)
git=Path(r'C:\Users\Suraj Vasireddy\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe')
gitstatus=subprocess.check_output([str(git),'--no-optional-locks','status','--short','--branch'],cwd=ROOT,text=True)
(OUT/'git_status_after.txt').write_text(gitstatus,encoding='utf-8')
tracked_diff=subprocess.check_output([str(git),'diff','--name-only','HEAD'],cwd=ROOT,text=True).splitlines()
tag=subprocess.check_output([str(git),'rev-parse','matra-stage-01-baseline-20261105'],cwd=ROOT,text=True).strip()
result={'original_files_checked':len(before),'original_files_changed':changed,
        'local_html_links_checked':len(parser.links),'missing_local_links':missing_links,
        'strict_json_files_parsed':json_count,'audit_scripts_compiled':compiled,
        'tracked_differences_from_HEAD':tracked_diff,'baseline_tag_commit':tag,
        'figures_visually_reviewed':['legacy_metrics.png','element_coverage.png','case_rank_heatmap.png'],
        'audio_generated':False,'audio_limitation':'Only en-US Windows voice exposed; no supported Telugu synthesis tool',
        'overall_pass':not changed and not missing_links and tracked_diff==['results/runs/task2_benchmark_evaluation.json']}
target.write_text(json.dumps(result,indent=2),encoding='utf-8')
paths=[]
for base in [ROOT/'experiments/stage_01',ROOT/'docs/stages/stage_01',ROOT/'docs/evaluation',OUT,ROOT/'logs/stage_01']:
    paths.extend(p for p in base.rglob('*') if p.is_file())
paths.append(ROOT/'docs/progress.md')
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}
(OUT/'stage_file_inventory.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
raise SystemExit(0 if result['overall_pass'] else 1)
