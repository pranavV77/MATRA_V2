"""Capture local source values and authoritative DOI registry metadata.

No properties are invented. Registry resolution checks bibliographic identity,
not experimental validity. Existing raw data is never replaced.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import inspect
import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import warnings

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/raw/stage_02_sources'
if (OUT/'source_snapshot.json').exists():raise FileExistsError('Source snapshot exists; do not overwrite')
sys.path.insert(0,str(ROOT))
import mendeleev
from mendeleev import element
from mendeleev.fetch import fetch_table
import pymatgen.core as mg
from src.features.build_elements_master import parse_subshell_valence

def clean(v):
    if isinstance(v,dict):return {str(k):clean(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [clean(x) for x in v]
    if v is None:return None
    if hasattr(v,'item'):v=v.item()
    if isinstance(v,float) and not math.isfinite(v):return None
    return v

def save(path,obj):
    with path.open('x',encoding='utf-8') as f:json.dump(clean(obj),f,ensure_ascii=False,indent=2,allow_nan=False)

metadata=fetch_table('propertymetadata')
source_elements=fetch_table('elements')
wanted=['atomic_number','symbol','name','period','group_id','block','mendeleev_number','density','atomic_weight','atomic_radius','en_pauling','covalent_radius_cordero','dipole_polarizability','thermal_conductivity','electronic_configuration']
registry=source_elements[wanted].to_dict(orient='records')
properties=['atomic_radius','density','atomic_weight','dipole_polarizability','mendeleev_number','thermal_conductivity','melting_point','covalent_radius_cordero','en_pauling','ionenergies','nvalence','electronic_configuration']
source_meta=metadata[metadata.attribute_name.isin(properties)].to_dict(orient='records')
records=[];warning_records=[]
for z in range(1,95):
    if z%15==1:print('Capturing local source properties:',z,'/ 94',flush=True)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        e=element(z);p=mg.Element(e.symbol)
        pauling=e.electronegativity('pauling');psource='mendeleev.electronegativity(pauling)'
        if pauling is None:
            x=getattr(p,'X',None)
            if x is not None and not math.isnan(float(x)):pauling=float(x);psource='pymatgen.Element.X'
        melt=e.melting_point;msource='mendeleev.Element.melting_point'
        if melt is None and p.melting_point is not None:melt=float(p.melting_point);msource='pymatgen.Element.melting_point'
        thermal=e.thermal_conductivity;tsource='mendeleev.Element.thermal_conductivity'
        if thermal is None and p.thermal_conductivity is not None:thermal=float(p.thermal_conductivity);tsource='pymatgen.Element.thermal_conductivity'
        density=e.density;dsource='mendeleev.Element.density'
        if density is None and p.density_of_solid is not None:density=float(p.density_of_solid);dsource='pymatgen.Element.density_of_solid'
        record={'atomic_number':z,'symbol':e.symbol,'name':e.name,'period':e.period,'group_id':e.group_id,'block':e.block,
                'mendeleev_number':e.mendeleev_number,'atomic_weight':e.atomic_weight,'electronic_configuration':e.econf,
                'native_values':{'pauling_electronegativity':pauling,'covalent_radius_cordero_pm':e.covalent_radius_cordero,
                    'atomic_radius_slater_pm':e.atomic_radius,'first_ionization_energy_ev':e.ionenergies.get(1),
                    'melting_point_k':melt,'thermal_conductivity_w_mk':thermal,'dipole_polarizability_bohr3':e.dipole_polarizability,
                    'valence_electrons':e.nvalence(),**parse_subshell_valence(e.econf,z),
                    'density_g_cm3':density,'atomic_molar_volume_cm3_mol_atoms':float(e.atomic_weight)/float(density) if density and density>0 else None},
                'selected_sources':{'pauling_electronegativity':psource,'melting_point_k':msource,'thermal_conductivity_w_mk':tsource,'density_g_cm3':dsource}}
    records.append(clean(record))
    warning_records.extend({'atomic_number':z,'symbol':e.symbol,'message':str(w.message)} for w in caught)
save(OUT/'source_snapshot.json',{'captured_at_utc':datetime.now(timezone.utc).isoformat(),
    'versions':{'mendeleev':mendeleev.__version__,'pymatgen':mg.__version__},
    'source_registry':clean(registry),'property_metadata':clean(source_meta),'elements_1_94':records,
    'subshell_rule_source_sha256':hashlib.sha256(inspect.getsource(parse_subshell_valence).encode()).hexdigest(),
    'warnings':warning_records,'statement':'Library-stored values are not automatically experimental measurements.'})

print('Resolving DOI metadata (does not certify scientific claims)...',flush=True)
benchmark=json.loads((ROOT/'data/benchmark/benchmark_cases.json').read_text(encoding='utf-8-sig'))
lookup={};network_log=[]
for case in benchmark['primary_cases']+benchmark['secondary_doping_cases']:
    doi=case['doi']
    if doi in lookup:continue
    filename=doi.replace('/','_')+'.json';success=False
    services=[('datacite','https://api.datacite.org/dois/') ] if doi.startswith('10.17188/') else [('crossref','https://api.crossref.org/works/')]
    for service,base in services:
        url=base+urllib.parse.quote(doi,safe='/')
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'MATRA-academic-reference-audit/0.1','Accept':'application/json'})
            with urllib.request.urlopen(request,timeout=20) as response:raw=json.load(response)
            save(OUT/filename,raw)
            if service=='crossref':
                m=raw['message'];titles=m.get('title',[]);authors=m.get('author',[])
                abstract=m.get('abstract')
            else:
                m=raw['data']['attributes'];titles=[v['title'] for v in m.get('titles',[])];authors=m.get('creators',[])
                abstract=m.get('descriptions')
            lookup[doi]={'status':'metadata_resolved','registry':service,'url':url,'local_file':filename,
                         'titles':titles,'authors':authors,'abstract_or_descriptions':abstract,
                         'scientific_claim_admission':'not established by DOI metadata'}
            print(case['case_id'],titles,flush=True);success=True
        except Exception as exc:
            network_log.append({'doi':doi,'url':url,'exception':type(exc).__name__,'message':str(exc)})
            print(case['case_id'],type(exc).__name__,str(exc),flush=True)
    if not success:lookup[doi]={'status':'unresolved','scientific_claim_admission':'not verified'}
    time.sleep(.2)
save(OUT/'doi_lookup.json',lookup);save(OUT/'network_errors.json',network_log)
print('Source capture complete. Existing datasets unchanged.',flush=True)
