"""Connect Stage 5 geometry to an isolated energy worker; retain provenance."""
import json
from src.similarity_validation import PROJECT_ROOT,validate_symbol
from src.structures.service import StructureService
from src.energy.contracts import relaxation_settings,neutral_geometry_from_stage5
from src.energy.bridge import run_worker


class EnergyService:
    def __init__(self,fusion=None,runner=None):
        self.structures=StructureService(fusion)
        self.runner=runner or run_worker

    def status(self):
        manifest=PROJECT_ROOT/'models/stage_06/checkpoint.json'
        installed=(PROJECT_ROOT/'configs/stage_06/environment_lock.txt').is_file()
        capabilities=PROJECT_ROOT/'models/stage_06/capabilities.json'
        return {'available':installed and manifest.is_file() and capabilities.is_file(),'environment_installed':installed,
                'checkpoint_present':manifest.is_file(),'model':json.loads(manifest.read_text()) if manifest.is_file() else None,
                'capabilities':json.loads(capabilities.read_text()) if capabilities.is_file() else None,
                'scope':'CPU model-predicted energy/forces and optional fixed-cell relaxation; no thermodynamic stability label',
                'maximum_atoms':40,'maximum_relaxation_steps':100,'accuracy_validated':False}

    def assess(self,payload):
        if not isinstance(payload,dict):raise ValueError('Energy request must be an object')
        fields={'host_id','cif_text','supercell','symprec','target','site_index','candidate_symbol','mode','relax','max_steps','fmax'}
        if set(payload)-fields:raise ValueError('Unrecognized energy fields')
        if not {'target','site_index','candidate_symbol'}<=set(payload):raise ValueError('target, site_index and candidate_symbol required')
        settings=relaxation_settings(payload.get('relax',False),payload.get('max_steps',100),payload.get('fmax',.05))
        validate_symbol(payload['candidate_symbol'],'candidate')
        host_fields={k:v for k,v in payload.items() if k in {'host_id','cif_text','supercell','symprec'}}
        host,provenance=self.structures._host(host_fields)
        from src.structures.hosts import diagonal_supercell
        expanded=diagonal_supercell(host,payload.get('supercell',[1,1,1]))
        if len(expanded)>40:raise ValueError('Energy assessment is capped at 40 atoms')
        capabilities=PROJECT_ROOT/'models/stage_06/capabilities.json'
        if capabilities.is_file():
            supported=set(json.loads(capabilities.read_text())['supported_elements'])
            requested={s.specie.symbol for s in expanded}|{payload['candidate_symbol']}
            if requested-supported:raise ValueError(f'Elements absent from the loaded energy checkpoint: {sorted(requested-supported)}')
        generated=self.structures.generate({**host_fields,'target':payload['target'],'site_index':payload['site_index'],
                                            'candidate_symbols':[payload['candidate_symbol']],'k':1,'mode':payload.get('mode','single_site')})
        trial=generated['configurations'][0]
        from pymatgen.core import Structure
        tasks=[{'label':'host','structure':neutral_geometry_from_stage5(expanded).as_dict(),'relax':False},
               {'label':'selected_trial','structure':neutral_geometry_from_stage5(Structure.from_dict(trial['structure'])).as_dict(),'relax':settings['relax'],
                'max_steps':settings['max_steps'],'fmax':settings['fmax_ev_per_angstrom']}]
        result=self.runner(tasks)
        record={'request':payload,'host_provenance':provenance,'trial_metadata':{k:v for k,v in trial.items() if k!='structure'},
                'energy_assessment':result,'cross_composition_ranking':'not_permitted',
                'model_input_policy':'Explicit neutral-atom interpretation. Formal oxidation decorations/serialized bookkeeping charge are not electronic charge-state inputs; original Stage 5 metadata preserved separately.',
                'interpretation':'Host and substituted trial have different compositions. Their raw energies are not a stability ranking.',
                'band_gap_preservation':'not_assessed','doping_activation':'not_assessed'}
        if result.get('record_directory'):
            from pathlib import Path
            path=Path(result['record_directory']).resolve()/'assessment_record.json'
            if not path.is_relative_to(PROJECT_ROOT):raise ValueError('Record directory must stay inside project')
            with path.open('x',encoding='utf-8') as out:json.dump(record,out,indent=2,allow_nan=False)
        return record
