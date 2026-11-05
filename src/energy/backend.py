"""CPU-only MACE adapter. Import in the isolated energy environment.

Uses one explicit checkpoint, no implicit downloads, no formation/hull claims.
"""
from pathlib import Path
import hashlib,importlib.metadata,json,math,time
from numbers import Real
import numpy as np
from pymatgen.core import Structure
from src.similarity_validation import PROJECT_ROOT
from src.structures.hosts import geometry_check,structure_fingerprint
from src.energy.contracts import relaxation_settings,reference_status


class EnergyBackend:
    def __init__(self):
        import torch
        from mace.calculators import MACECalculator
        torch.set_num_threads(2)
        self.manifest=json.loads((PROJECT_ROOT/'models/stage_06/checkpoint.json').read_text())
        path=(PROJECT_ROOT/self.manifest['path']).resolve()
        if not path.is_relative_to(PROJECT_ROOT) or not path.is_file():raise ValueError('Project-local model file required')
        self.sha256=hashlib.sha256(path.read_bytes()).hexdigest()
        if self.sha256!=self.manifest['sha256']:raise ValueError('Checkpoint hash does not match frozen acquisition')
        start=time.perf_counter()
        self.calculator=MACECalculator(model_paths=str(path),device='cpu',default_dtype='float64')
        self.load_ms=(time.perf_counter()-start)*1000
        self.supported=tuple(int(x) for x in self.calculator.models[0].atomic_numbers.detach().cpu().tolist())

    def info(self):
        return {'model_id':self.manifest['model_id'],'model_sha256':self.sha256,'model_load_ms':self.load_ms,
                'device':'cpu','dtype':'float64','torch_threads':2,'supported_atomic_numbers':list(self.supported),
                'supported_element_count':len(self.supported),
                'versions':{p:importlib.metadata.version(p) for p in ['mace-torch','torch','ase','numpy','pymatgen']},
                'scope':'neural-potential prediction; no external accuracy established',**reference_status()}

    def _atoms(self,structure):
        from ase import Atoms
        geometry_check(structure)
        if len(structure)>40:raise ValueError('Initial energy workload is capped at 40 atoms')
        explicit_charge=structure.as_dict().get('charge')
        if explicit_charge is not None and abs(float(explicit_charge))>1e-8:
            raise ValueError('Explicit charged-cell calculations are unsupported by this neutral potential workflow')
        numbers=[site.specie.Z for site in structure]
        unsupported=sorted(set(numbers)-set(self.supported))
        if unsupported:raise ValueError(f'Elements not represented by this checkpoint (atomic numbers): {unsupported}')
        atoms=Atoms(numbers=numbers,positions=structure.cart_coords,cell=structure.lattice.matrix,pbc=True)
        atoms.calc=self.calculator
        return atoms

    def _prediction(self,atoms):
        raw_energy=atoms.get_potential_energy()
        forces=np.asarray(atoms.get_forces())
        if isinstance(raw_energy,(bool,np.bool_)) or not isinstance(raw_energy,Real):
            raise ValueError('Model energy must be a real scalar, not a coerced value')
        energy=float(raw_energy)
        if not math.isfinite(energy) or forces.dtype.kind not in 'iuf' or forces.shape!=(len(atoms),3) or not np.isfinite(forces).all():
            raise ValueError('Model returned nonfinite energy/forces or wrong force shape')
        return {'total_energy_ev':energy,'energy_ev_per_atom':energy/len(atoms),
                'forces_ev_per_angstrom':forces.tolist(),
                'maximum_force_ev_per_angstrom':float(np.linalg.norm(forces,axis=1).max()),
                'composition_counts':{str(int(z)):int(sum(atoms.numbers==z)) for z in sorted(set(atoms.numbers))},
                'model_sha256':self.sha256,'stress':'not_requested'}

    def predict(self,structure):
        atoms=self._atoms(structure)
        # A new public static prediction performs inference, even for identical
        # inputs. ASE may otherwise reuse a calculator's previous result.
        self.calculator.reset()
        start=time.perf_counter();prediction=self._prediction(atoms)
        return {**prediction,'inference_ms':(time.perf_counter()-start)*1000,
                'input_structure_sha256':structure_fingerprint(structure),
                'source':'MACE neural-potential prediction','geometry_policy':'fixed_input_geometry',
                'cache_policy':'calculator reset before each public static prediction',
                'oxidation_state_policy':'formal oxidation decorations are not charge-state inputs to this potential',
                **reference_status()}

    def assess(self,structure,relax=False,max_steps=100,fmax=.05):
        settings=relaxation_settings(relax,max_steps,fmax)
        initial=self.predict(structure)
        result={'initial':initial,'settings':settings,'relaxation':{'attempted':False,'converged':None},
                'validation':{'model_inference':'executed','external_dft_accuracy':'not_verified',
                              'thermodynamic_stability':'not_assessed','band_gap':'not_assessed','doping_activation':'not_assessed'}}
        if not relax:return result
        from ase.optimize import FIRE
        atoms=self._atoms(structure);history=[]
        optimizer=FIRE(atoms,logfile=None,maxstep=.1)
        def capture():
            prediction=self._prediction(atoms)
            history.append({'step':int(optimizer.nsteps),'total_energy_ev':prediction['total_energy_ev'],
                            'maximum_force_ev_per_angstrom':prediction['maximum_force_ev_per_angstrom']})
        optimizer.attach(capture,interval=1)
        start=time.perf_counter();optimizer.run(fmax=settings['fmax_ev_per_angstrom'],steps=max_steps)
        final=self._prediction(atoms)
        relaxed=Structure(atoms.cell.array,[int(z) for z in atoms.numbers],atoms.positions,coords_are_cartesian=True)
        checked=geometry_check(relaxed)
        cell_same=bool(np.array_equal(atoms.cell.array,structure.lattice.matrix))
        if not cell_same:raise RuntimeError('Fixed-cell relaxation changed the cell')
        result['relaxation']={'attempted':True,'converged':final['maximum_force_ev_per_angstrom']<=settings['fmax_ev_per_angstrom'],
                              'steps':int(optimizer.nsteps),'elapsed_ms':(time.perf_counter()-start)*1000,
                              'history':history,'final':final,'final_structure':relaxed.as_dict(),
                              'final_structure_sha256':structure_fingerprint(relaxed),'geometry':checked,'cell_unchanged':cell_same,
                              'energy_change_ev_same_composition':final['total_energy_ev']-initial['total_energy_ev'],
                              'note':'Local optimizer convergence under this potential; not thermodynamic or experimental stability.'}
        return result
