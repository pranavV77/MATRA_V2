"""Backup restore-path regressions; downloads/processes are explicitly mocked."""
import hashlib,importlib.util,io,json,subprocess
from pathlib import Path
import pytest


def script(name):
    path=Path(__file__).resolve().parents[2]/'experiments/stage_06'/f'{name}.py'
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_restore_weight_preserves_committed_manifest(tmp_path,monkeypatch):
    module=script('download_model');monkeypatch.setattr(module,'ROOT',tmp_path)
    content=b'controlled test bytes';sha=hashlib.sha256(content).hexdigest()
    monkeypatch.setattr(module,'EXPECTED_BYTES',len(content));monkeypatch.setattr(module,'EXPECTED_SHA256',sha)
    folder=tmp_path/'models/stage_06';folder.mkdir(parents=True)
    manifest=folder/'checkpoint.json';manifest.write_text(json.dumps({'sha256':sha,'bytes':len(content),'original':True}));before=manifest.read_bytes()
    class Response(io.BytesIO):headers={'Content-Type':'application/octet-stream'}
    monkeypatch.setattr(module,'urlopen',lambda *a,**k:Response(content))
    module.main()
    assert (folder/'mace_mp_0_small.model').read_bytes()==content
    assert manifest.read_bytes()==before and len(list(folder.glob('restoration_*.json')))==1
    monkeypatch.setattr(module,'urlopen',lambda *a,**k:pytest.fail('Verified model should not download again'))
    module.main();assert manifest.read_bytes()==before


def test_corrupted_weight_not_overwritten(tmp_path,monkeypatch):
    module=script('download_model');monkeypatch.setattr(module,'ROOT',tmp_path)
    folder=tmp_path/'models/stage_06';folder.mkdir(parents=True)
    path=folder/'mace_mp_0_small.model';path.write_bytes(b'existing')
    with pytest.raises(ValueError,match='preserved'):module.main()
    assert path.read_bytes()==b'existing'


def test_setup_restore_preserves_lock_and_old_logs(tmp_path,monkeypatch):
    module=script('setup_environment');monkeypatch.setattr(module,'ROOT',tmp_path)
    lock=tmp_path/'configs/stage_06/environment_lock.txt';lock.parent.mkdir(parents=True);lock.write_text('pip==26.2.1\n')
    old=tmp_path/'logs/stage_06/run_001/install_01.txt';old.parent.mkdir(parents=True);old.write_text('original log')
    commands=[]
    def run(command,**kwargs):
        commands.append(command)
        if 'venv' in command:(tmp_path/'.venv_energy').mkdir()
        return subprocess.CompletedProcess(command,0)
    monkeypatch.setattr(module.subprocess,'run',run)
    monkeypatch.setattr(module.subprocess,'check_output',lambda *a,**k:'pip==26.2.1\n')
    module.main()
    assert lock.read_text()=='pip==26.2.1\n' and old.read_text()=='original log'
    assert any('--constraint' in c and str(lock) in c for c in commands)
    assert len(list((tmp_path/'results/stage_06').glob('setup_*/environment_lock.txt')))==1


def test_setup_existing_environment_is_preserved(tmp_path,monkeypatch):
    module=script('setup_environment');monkeypatch.setattr(module,'ROOT',tmp_path)
    (tmp_path/'.venv_energy').mkdir()
    with pytest.raises(FileExistsError,match='preserved'):module.main()
