"""Real loopback HTTP tests and project-local export safety."""
from pathlib import Path
import json
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from src.review_demo.service import DemoService
from src.review_demo.server import make_server


@pytest.fixture(scope='module')
def service(tmp_path_factory): return DemoService(export_dir=tmp_path_factory.mktemp('review_exports'))


@pytest.fixture(scope='module')
def server(service):
    instance = make_server(0,service)
    thread = threading.Thread(target=instance.serve_forever,daemon=True); thread.start()
    yield f'http://127.0.0.1:{instance.server_port}'
    instance.shutdown(); instance.server_close(); thread.join(timeout=3)


def post(base,payload,route='/api/recommend',headers=None):
    data = json.dumps(payload).encode()
    return urlopen(Request(base+route,data=data,headers=headers or {'Content-Type':'application/json'}),timeout=10)


def test_real_api_and_host_membership(server):
    with post(server,{'target_element':'Ga','host_formula':'Ga2O3'}) as response:
        result = json.load(response)
    assert result['returned_k'] == 10 and result['score_is_probability'] is False
    assert result['host_context']['target_present']
    assert result['validation']['energy_stability'] == 'not_run'
    assert any(r['candidate_element']=='Al' for r in result['reference_notes'])


@pytest.mark.parametrize('path,mime', [('/','text/html'),('/app.js','text/javascript'),('/style.css','text/css'),('/api/health','application/json'),('/api/status','application/json'),('/api/evaluation','application/json')])
def test_routes_and_static_assets(server,path,mime):
    with urlopen(server+path,timeout=10) as response:
        assert response.status == 200 and response.headers.get_content_type() == mime
        assert response.read()


@pytest.mark.parametrize('payload', [{'target_element':'ga'},{'target_element':'Og'}, {'target_element':'Ga','host_formula':'MoS2'},
    {'target_element':'Ga','k':True}, {'target_element':'Ga','weights':{'PN':0,'Atom2Vec':0,'Property':0}},
    {'target_element':'Ga','validated':True}, {}, [], {'target_element':['Ga']}])
def test_bad_requests_return_json_errors(server,payload):
    with pytest.raises(HTTPError) as error: post(server,payload)
    assert error.value.code == 400
    assert json.load(error.value)['error']


def test_request_limits_and_cross_origin(server):
    with pytest.raises(HTTPError) as error:
        post(server,{'target_element':'Ga'},headers={'Content-Type':'text/plain'})
    assert error.value.code == 415
    with pytest.raises(HTTPError) as error:
        post(server,{'target_element':'Ga'},headers={'Content-Type':'application/json','Origin':'https://unrelated.example'})
    assert error.value.code == 403
    with pytest.raises(HTTPError) as error:
        post(server,{'target_element':'Ga','host_formula':'a'*17000})
    assert error.value.code == 413


def test_private_paths_not_served(server):
    with pytest.raises(HTTPError) as error: urlopen(server+'/../.env',timeout=10)
    assert error.value.code == 404


def test_exports_are_unique_and_only_in_project(server,service):
    outputs = []
    for _ in range(2):
        with post(server,{'target_element':'Te','host_formula':'Bi2Te3'},'/api/export') as response: outputs.append(json.load(response))
    assert outputs[0]['json_path'] != outputs[1]['json_path']
    for output in outputs:
        for key in ('json_path','csv_path'):
            path = Path(output[key]); assert path.is_file() and path.parent == service.export_dir
        data = json.loads(Path(output['json_path']).read_text(encoding='utf-8'))
        assert data['result']['score_is_probability'] is False


def test_evidence_annotations_do_not_change_ranking(service):
    base = service.engine.recommend('Ga',host_formula='GaN')
    annotated = service.recommend({'target_element':'Ga','host_formula':'GaN'})
    assert [r['fusion_score'] for r in base['rankings']] == [r['fusion_score'] for r in annotated['rankings']]
    assert all(r['current_request_validated'] is False for r in annotated['reference_notes'])
    assert all(r['requested_parent_formula_matches'] is False for r in annotated['reference_notes'])
