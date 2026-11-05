"""Retrieve public primary sources locally; failures are retained explicitly.

No authentication bypass or remote execution. Full-text availability is not
equivalent to evidence admission. Captcha/error responses are not paper text.
"""
from pathlib import Path
from datetime import datetime,timezone
from html.parser import HTMLParser
import hashlib,json,subprocess,sys,time
import urllib.request,urllib.parse
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/raw/stage_02_primary_sources'
if (OUT/'acquisition_manifest.json').exists():raise FileExistsError('Acquisition already recorded')
SOURCES=[
 ('MoW_atomic','10.1038/ncomms2351','https://www.nature.com/articles/ncomms2351'),
 ('MoW_Chen','10.1021/nn401420h',None),
 ('MoSe_Gong','10.1021/nl4032296',None),
 ('Re_MoS2','10.1002/adma.201304985','https://krasheninnikov.de/publ/adma201304985-13.pdf'),
 ('Nb_STO','10.1038/s41598-022-06361-3','https://pmc.ncbi.nlm.nih.gov/articles/PMC8847566/'),
 ('Nb_STO_polar','10.1038/s41535-022-00524-9','https://www.nature.com/articles/s41535-022-00524-9'),
 ('Sn_Ga_XAS',None,'https://dash.harvard.edu/entities/publication/73120378-e473-6bd4-e053-0100007fdf3b'),
 ('Si_Ga_Villora','10.1063/1.2919728',None),
 ('Mg_GaN_Amano','10.1143/JJAP.28.L2112',None),
 ('Al_Ga_Peelaers','10.1063/1.5036991','https://www.osti.gov/pages/servlets/purl/1497947'),
 ('CsPbSn','10.1039/D4MA00034J','https://pubs.rsc.org/en/content/articlehtml/2024/ma/d4ma00034j'),
 ('BiTeSe','10.34133/2020/4361703','https://pmc.ncbi.nlm.nih.gov/articles/PMC7150672/'),
 ('BaSr_neutron','10.48550/arXiv.2007.00972','https://arxiv.org/pdf/2007.00972'),
 ('GaAl_HSE','10.1103/PhysRevApplied.10.011003','https://arxiv.org/pdf/1806.03360'),
]
class Extract(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.hidden=0
 def handle_starttag(self,t,a):
  if t in ['script','style']:self.hidden+=1
  if t in ['p','h1','h2','h3','h4','div','tr','li','section']:self.parts.append('\n')
 def handle_endtag(self,t):
  if t in ['script','style']:self.hidden=max(0,self.hidden-1)
 def handle_data(self,d):
  if not self.hidden:self.parts.append(d)

def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'MATRA local academic evidence review/0.2'})
 with urllib.request.urlopen(req,timeout=25) as r:return r.read(),r.headers.get('Content-Type','')
def save_json(path,data):
 with path.open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
def save_text(path,text):
 lines=[' '.join(s.split()) for s in text.splitlines() if s.strip()]
 path.write_text('\n'.join(f'{i+1:05d} {s}' for i,s in enumerate(lines)),encoding='utf-8')

manifest=[]
for sid,doi,url in SOURCES:
 record={'source_id':sid,'candidate_doi':doi,'requested_primary_url':url,'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'artifacts':[],'errors':[]}
 print('Retrieving',sid,flush=True)
 if doi and not doi.startswith('10.48550/'):
  try:
   content,_=fetch('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='/'));meta=json.loads(content)
   save_json(OUT/(sid+'_metadata.json'),meta);record['registered_title']=meta['message'].get('title');record['registered_doi']=meta['message'].get('DOI')
   if meta['message'].get('abstract'):save_text(OUT/(sid+'_abstract.txt'),meta['message']['abstract'])
  except Exception as exc:record['errors'].append({'step':'crossref','message':str(exc)})
 if url:
  try:
   content,ctype=fetch(url)
   if content.startswith(b'%PDF'):
    path=OUT/(sid+'.pdf');path.write_bytes(content)
    # Use local bundled PDF reader, leaving scientific execution in project .venv.
    reader=Path(r'C:\Users\Suraj Vasireddy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
    code="from pypdf import PdfReader; from pathlib import Path; import sys; d=PdfReader(sys.argv[1]); Path(sys.argv[2]).write_text('\\n'.join('--- PAGE '+str(i+1)+' ---\\n'+p.extract_text() for i,p in enumerate(d.pages)),encoding='utf-8')"
    run=subprocess.run([str(reader),'-B','-X','utf8','-c',code,str(path),str(OUT/(sid+'_pages.txt'))],capture_output=True,text=True,encoding='utf-8')
    if run.returncode:record['errors'].append({'step':'pdf_read','message':run.stderr})
    record['artifacts'].append({'path':path.name,'sha256':hashlib.sha256(content).hexdigest(),'kind':'primary_full_pdf'})
   else:
    text=content.decode('utf-8',errors='replace')
    if any(x in text[:5000].lower() for x in ['checking your browser','recaptcha','just a moment...']):raise ValueError('Challenge page, not source text')
    path=OUT/(sid+'.html');path.write_bytes(content)
    parser=Extract();parser.feed(text);save_text(OUT/(sid+'_text.txt'),''.join(parser.parts))
    record['artifacts'].append({'path':path.name,'sha256':hashlib.sha256(content).hexdigest(),'kind':'primary_page_requires_review'})
  except Exception as exc:record['errors'].append({'step':'primary_url','message':str(exc)})
 # Official Europe PMC OA full text is an alternate public repository, not a paywall bypass.
 if doi:
  try:
   query='DOI:'+doi
   content,_=fetch('https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='+urllib.parse.quote(query)+'&format=json')
   search=json.loads(content);save_json(OUT/(sid+'_europepmc_search.json'),search)
   for hit in search.get('resultList',{}).get('result',[])[:1]:
    if hit.get('pmcid'):
     record['pmcid']=hit['pmcid']
     xml,_=fetch('https://www.ebi.ac.uk/europepmc/webservices/rest/'+hit['pmcid']+'/fullTextXML')
     path=OUT/(sid+'_fulltext.xml');path.write_bytes(xml)
     tree=ET.fromstring(xml)
     parts=[]
     for el in tree.iter():
      if el.tag in ['article-title','title','p','table-wrap']:
       parts.append('['+el.tag+(' id='+el.attrib['id'] if 'id' in el.attrib else '')+'] '+''.join(el.itertext()))
     save_text(OUT/(sid+'_fulltext.txt'),'\n'.join(parts))
     record['artifacts'].append({'path':path.name,'sha256':hashlib.sha256(xml).hexdigest(),'kind':'primary_fulltext_xml'})
  except Exception as exc:record['errors'].append({'step':'europepmc','message':str(exc)})
 manifest.append(record)
 print(' ',sid,len(record['artifacts']),'source artifacts;',len(record['errors']),'retrieval issues',flush=True)
 time.sleep(.2)
save_json(OUT/'acquisition_manifest.json',manifest)
print('Acquisition complete; every source still requires claim-level review.',flush=True)
