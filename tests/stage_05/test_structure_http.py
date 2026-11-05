"""Actual loopback end-to-end host analysis, generation, exports and rejection."""
import json
from pathlib import Path
import threading
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import pytest
from pymatgen.io.cif import CifWriter
from src.review_demo.server import make_server
from src.review_demo.service import DemoService
from src.structures.service import StructureService
from src.structures.prototypes import prototype


@pytest.fixture(scope='module')
def base(tmp_path_factory):
    directory=tmp_path_factory.mktemp('http_structure_exports')
    demo=DemoService(export_dir=directory)
    server=make_server(0,demo,StructureService(demo.engine,directory))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    yield f'http://127.0.0.1:{server.server_port}'
    server.shutdown();server.server_close();thread.join(timeout=3)


def post(base,route,payload):
    request=Request(base+'/api/structure/'+route,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    with urlopen(request,timeout=15) as r:return json.load(r)


def test_catalog_and_static(base):
    with urlopen(base+'/api/structure/catalog') as r: assert len(json.load(r)['hosts'])==3
    with urlopen(base+'/structures.js') as r: assert b'Structure lab' in r.read()


def test_real_structure_workflow(base):
    host=post(base,'analyze',{'host_id':'perovskite','supercell':[2,2,2]})
    assert host['analysis']['site_count']==40
    index=next(s['index'] for s in host['analysis']['sites'] if s['element']=='Ti')
    p={'host_id':'perovskite','supercell':[2,2,2],'target':'Ti','site_index':index,'k':1,'candidate_symbols':['Zr']}
    result=post(base,'generate',p)
    assert result['configurations'][0]['target_sublattice_fraction']==.125
    saved=post(base,'export',p)
    assert saved['saved'] and Path(saved['record_path']).is_file()


def test_real_custom_cif(base):
    text=str(CifWriter(prototype('wurtzite')))
    # A long, legitimate comment exercises the larger structural request limit.
    text+='\n#'+('comment '*2500)+'\n'
    result=post(base,'analyze',{'cif_text':text})
    assert result['analysis']['spacegroup']['number']==186
    assert result['provenance']['evidence_class']=='user_supplied_unverified_CIF'


@pytest.mark.parametrize('route,payload',[('analyze',{}),('analyze',{'host_id':'unknown'}),('analyze',{'host_id':'perovskite','supercell':[4,4,4]}),('generate',{'host_id':'perovskite'}),('generate',{'host_id':'perovskite','target':'Ga','site_index':1}),('analyze',{'cif_text':'bad'}),('export',{'host_id':'perovskite','target':'Ti','site_index':1,'structure':{}})])
def test_bad_structure_requests(base,route,payload):
    with pytest.raises(HTTPError) as error: post(base,route,payload)
    assert error.value.code==400
    assert json.load(error.value)['error']
