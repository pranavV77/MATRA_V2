"""Launch the isolated CPU worker without importing Torch into the demo environment."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess,threading,uuid
from src.similarity_validation import PROJECT_ROOT

_WORKER_LOCK=threading.Lock()


def worker_environment():
    env=os.environ.copy()
    env.update({'TEMP':str(PROJECT_ROOT/'work/stage_06/temp'),'TMP':str(PROJECT_ROOT/'work/stage_06/temp'),
                'XDG_CACHE_HOME':str(PROJECT_ROOT/'work/stage_06/cache'),
                'TORCH_HOME':str(PROJECT_ROOT/'work/stage_06/cache/torch'),
                'MPLCONFIGDIR':str(PROJECT_ROOT/'work/stage_06/cache/matplotlib'),
                'PYTHONNOUSERSITE':'1','PYTHONUTF8':'1','OMP_NUM_THREADS':'2','MKL_NUM_THREADS':'2'})
    return env


def run_worker(tasks,timeout=300):
    python=PROJECT_ROOT/'.venv_energy/Scripts/python.exe'
    if not python.is_file():raise RuntimeError('Approved isolated energy environment is not available')
    if not (PROJECT_ROOT/'models/stage_06/checkpoint.json').is_file():raise RuntimeError('Official checkpoint has not been acquired')
    # Serialize expensive jobs rather than multiplying model-memory usage on this laptop.
    if not _WORKER_LOCK.acquire(blocking=False):raise ValueError('An energy assessment is already running; wait for it to finish')
    try:
        directory=PROJECT_ROOT/'results/energy_assessments'/('assessment_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ_')+uuid.uuid4().hex[:10])
        directory.mkdir(parents=True,exist_ok=False)
        request=directory/'request.json';response=directory/'response.json';log=directory/'worker.log'
        with request.open('x',encoding='utf-8') as out:json.dump({'tasks':tasks},out,indent=2,allow_nan=False)
        with log.open('x',encoding='utf-8') as out:
            try:
                process=subprocess.run([str(python),'-m','src.energy.worker','--request',str(request),'--response',str(response)],
                                       cwd=PROJECT_ROOT,env=worker_environment(),stdout=out,stderr=subprocess.STDOUT,
                                       timeout=timeout,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            except subprocess.TimeoutExpired as exc:raise RuntimeError(f'Energy job exceeded {timeout}s; request/log preserved at {directory}') from exc
        if not response.is_file():raise RuntimeError(f'Energy worker did not write a response; inspect {log}')
        result=json.loads(response.read_text(encoding='utf-8'))
        if process.returncode or not result.get('ok'):raise RuntimeError(f'Energy assessment failed: {result.get("error","worker error")}; inspect {log}')
        return {**result,'record_directory':str(directory)}
    finally:_WORKER_LOCK.release()
