"""Approved isolated Stage 6 setup; all environments, caches and logs project-local."""
from pathlib import Path
import os,subprocess,sys,json
ROOT=Path(__file__).resolve().parents[2]


def local_environment():
    env=os.environ.copy()
    env.update({'TEMP':str(ROOT/'work/stage_06/temp'),'TMP':str(ROOT/'work/stage_06/temp'),
                'PIP_CACHE_DIR':str(ROOT/'work/stage_06/cache/pip'),
                'XDG_CACHE_HOME':str(ROOT/'work/stage_06/cache'),
                'TORCH_HOME':str(ROOT/'work/stage_06/cache/torch'),
                'HF_HOME':str(ROOT/'work/stage_06/cache/huggingface'),
                'MPLCONFIGDIR':str(ROOT/'work/stage_06/cache/matplotlib'),
                'PYTHONNOUSERSITE':'1','PYTHONUTF8':'1','PIP_DISABLE_PIP_VERSION_CHECK':'1'})
    return env


def main():
    env=local_environment();environment=ROOT/'.venv_energy';python=environment/'Scripts/python.exe'
    if environment.exists():raise FileExistsError('Existing energy environment preserved; inspect before resuming installation')
    subprocess.run([sys.executable,'-m','venv',str(environment)],cwd=ROOT,env=env,check=True)
    commands=[
        [str(python),'-m','pip','install','pip==26.2.1'],
        [str(python),'-m','pip','install','torch==2.6.0','--index-url','https://download.pytorch.org/whl/cpu','--only-binary=:all:','--report',str(ROOT/'results/stage_06/run_001/torch_install_report.json')],
        [str(python),'-m','pip','install','mace-torch==0.3.14','pymatgen==2025.10.7','numpy==2.2.6','pytest==9.1.1','--prefer-binary','--report',str(ROOT/'results/stage_06/run_001/mace_install_report.json')],
        [str(python),'-m','pip','check']]
    for i,command in enumerate(commands,1):
        log=ROOT/f'logs/stage_06/run_001/install_{i:02d}.txt'
        with log.open('x',encoding='utf-8') as out:
            result=subprocess.run(command,cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT)
        print(f'Step {i}: exit={result.returncode}; log={log.relative_to(ROOT)}',flush=True)
        if result.returncode:raise RuntimeError(f'Installation step {i} failed; inspect preserved log')
    frozen=subprocess.check_output([str(python),'-m','pip','freeze','--all'],cwd=ROOT,env=env,text=True)
    with (ROOT/'configs/stage_06/environment_lock.txt').open('x',encoding='utf-8') as out:out.write(frozen)


if __name__=='__main__':main()
