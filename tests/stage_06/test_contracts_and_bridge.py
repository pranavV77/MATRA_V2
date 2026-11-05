import json,subprocess
from pathlib import Path
import pytest
from src.energy.contracts import relaxation_settings,regression_metrics,comparable_energy_difference,reference_status
from src.energy import bridge


@pytest.mark.parametrize('kwargs',[{'relax':1},{'relax':'yes'},{'max_steps':0},{'max_steps':101},{'max_steps':True},{'fmax':float('nan')},{'fmax':float('inf')},{'fmax':0},{'fmax':1},{'fmax':True}])
def test_invalid_relaxation_settings(kwargs):
    with pytest.raises((ValueError,TypeError)):relaxation_settings(**kwargs)


def test_metric_math_and_no_fake_stability():
    r=regression_metrics([1,3],[2,2])
    assert r=={'n':2,'mae':1,'rmse':1,'bias':0}
    assert reference_status()['energy_above_hull_ev_per_atom'] is None


@pytest.mark.parametrize('a,b',[([],[]),([1],[]),([True],[1]),([float('nan')],[1]),('x',[1])])
def test_invalid_regression_inputs(a,b):
    with pytest.raises(ValueError):regression_metrics(a,b)


def test_composition_and_checkpoint_comparison_gate():
    a={'composition_counts':{'1':2},'model_sha256':'one','total_energy_ev':-2}
    assert comparable_energy_difference(a,{**a,'total_energy_ev':-3})==-1
    with pytest.raises(ValueError):comparable_energy_difference(a,{**a,'composition_counts':{'2':2}})
    with pytest.raises(ValueError):comparable_energy_difference(a,{**a,'model_sha256':'two'})
    with pytest.raises(ValueError):comparable_energy_difference(a,{**a,'total_energy_ev':float('nan')})
    with pytest.raises(ValueError):comparable_energy_difference(a,{})


@pytest.fixture
def fake_workspace(tmp_path,monkeypatch):
    monkeypatch.setattr(bridge,'PROJECT_ROOT',tmp_path)
    p=tmp_path/'.venv_energy/Scripts/python.exe';p.parent.mkdir(parents=True);p.touch()
    p=tmp_path/'models/stage_06/checkpoint.json';p.parent.mkdir(parents=True);p.write_text('{}')
    return tmp_path


def test_bridge_unique_outputs_and_environment(fake_workspace,monkeypatch):
    def fake_run(command,**kwargs):
        Path(command[command.index('--response')+1]).write_text(json.dumps({'ok':True,'results':[]}))
        assert kwargs['env']['PYTHONNOUSERSITE']=='1'
        return subprocess.CompletedProcess(command,0)
    monkeypatch.setattr(bridge.subprocess,'run',fake_run)
    a=bridge.run_worker([{}]);b=bridge.run_worker([{}])
    assert a['record_directory']!=b['record_directory']
    assert Path(a['record_directory'],'request.json').is_file()


def test_bridge_failures_preserve_records(fake_workspace,monkeypatch):
    monkeypatch.setattr(bridge.subprocess,'run',lambda *a,**k:subprocess.CompletedProcess(a[0],1))
    with pytest.raises(RuntimeError,match='did not write'):bridge.run_worker([{}])
    assert len(list((fake_workspace/'results/energy_assessments').glob('*/request.json')))==1


def test_bridge_timeout_and_busy(fake_workspace,monkeypatch):
    def timed_out(*args,**kwargs):raise subprocess.TimeoutExpired(args[0],1)
    monkeypatch.setattr(bridge.subprocess,'run',timed_out)
    with pytest.raises(RuntimeError,match='exceeded'):bridge.run_worker([{}],timeout=1)
    assert not bridge._WORKER_LOCK.locked()
    bridge._WORKER_LOCK.acquire()
    try:
        with pytest.raises(ValueError,match='already running'):bridge.run_worker([{}])
    finally:bridge._WORKER_LOCK.release()
