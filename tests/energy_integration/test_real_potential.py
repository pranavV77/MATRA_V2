"""Run explicitly with .venv_energy. Actual model tests, not mocked DFT labels."""
import pytest
pytest.importorskip('mace',reason='Actual potential tests require the approved isolated .venv_energy')
import numpy as np
from pymatgen.core import Lattice,Structure
from src.structures.prototypes import prototype
from src.structures.hosts import structure_fingerprint
from src.energy.backend import EnergyBackend


@pytest.fixture(scope='module')
def backend():return EnergyBackend()


def test_model_identity_and_coverage(backend):
    info=backend.info()
    assert info['device']=='cpu' and info['dtype']=='float64'
    assert info['model_sha256']=='d5773bf9440e96d6eb8c598f84bd0e6369fcfa432f626a87f890e07da3c651c9'
    assert info['supported_element_count']==len(set(info['supported_atomic_numbers']))
    assert {7,8,16,22,30,31,38,40}<=set(info['supported_atomic_numbers'])


@pytest.mark.parametrize('name',['perovskite','wurtzite'])
def test_real_prediction_repeat_units_and_no_mutation(backend,name):
    host=prototype(name);before=structure_fingerprint(host)
    a=backend.predict(host);b=backend.predict(host)
    assert np.isfinite(a['total_energy_ev'])
    assert a['energy_ev_per_atom']==pytest.approx(a['total_energy_ev']/len(host))
    assert np.asarray(a['forces_ev_per_angstrom']).shape==(len(host),3)
    assert a['total_energy_ev']==pytest.approx(b['total_energy_ev'],abs=1e-8)
    assert structure_fingerprint(host)==before
    assert a['formation_energy_ev_per_atom'] is None


def test_translation_invariance(backend):
    host=prototype('perovskite');moved=host.copy()
    moved.translate_sites(list(range(len(host))),[.137,.283,.419],frac_coords=True,to_unit_cell=True)
    a=backend.predict(host);b=backend.predict(moved)
    assert abs(a['energy_ev_per_atom']-b['energy_ev_per_atom'])<1e-7
    assert np.allclose(a['forces_ev_per_angstrom'],b['forces_ev_per_angstrom'],atol=1e-6,rtol=0)


def test_permutation_invariance(backend):
    host=prototype('perovskite');order=[4,2,0,3,1]
    reordered=Structure(host.lattice,[host[i].specie for i in order],host.frac_coords[order])
    a=backend.predict(host);b=backend.predict(reordered)
    assert abs(a['energy_ev_per_atom']-b['energy_ev_per_atom'])<1e-7
    assert np.allclose(np.asarray(a['forces_ev_per_angstrom'])[order],b['forces_ev_per_angstrom'],atol=1e-6,rtol=0)


def test_rotation_equivariance(backend):
    host=prototype('wurtzite');angle=.321
    rotation=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]])
    rotated=Structure(Lattice(host.lattice.matrix@rotation.T),[s.specie for s in host],host.frac_coords)
    a=backend.predict(host);b=backend.predict(rotated)
    assert abs(a['energy_ev_per_atom']-b['energy_ev_per_atom'])<1e-7
    assert np.allclose(np.asarray(a['forces_ev_per_angstrom'])@rotation.T,b['forces_ev_per_angstrom'],atol=1e-6,rtol=0)


def test_supercell_extensivity(backend):
    host=prototype('perovskite');expanded=host.copy();expanded.make_supercell([2,1,1])
    a=backend.predict(host);b=backend.predict(expanded)
    assert abs(a['energy_ev_per_atom']-b['energy_ev_per_atom'])<1e-7
    assert abs(2*a['total_energy_ev']-b['total_energy_ev'])<1e-6


def test_finite_difference_force(backend):
    host=prototype('perovskite');host.translate_sites([1],[.04,0,0],frac_coords=False)
    delta=1e-4;plus=host.copy();minus=host.copy()
    plus.translate_sites([1],[delta,0,0],frac_coords=False);minus.translate_sites([1],[-delta,0,0],frac_coords=False)
    force=backend.predict(host)['forces_ev_per_angstrom'][1][0]
    derivative=-(backend.predict(plus)['total_energy_ev']-backend.predict(minus)['total_energy_ev'])/(2*delta)
    assert force==pytest.approx(derivative,abs=1e-3)


def test_relaxation_trajectory_and_convergence(backend):
    host=prototype('perovskite');host.translate_sites([1],[.08,0,0],frac_coords=False)
    before=structure_fingerprint(host);result=backend.assess(host,relax=True,max_steps=100,fmax=.05)
    r=result['relaxation']
    assert r['attempted'] and r['converged']
    assert r['final']['maximum_force_ev_per_angstrom']<=.05
    assert r['energy_change_ev_same_composition']<=1e-7
    assert r['cell_unchanged'] and r['history']
    assert structure_fingerprint(host)==before


def test_nonconvergence_is_reported(backend):
    host=prototype('perovskite');host.translate_sites([1],[.2,.1,0],frac_coords=False)
    r=backend.assess(host,relax=True,max_steps=1,fmax=.01)['relaxation']
    assert r['steps']<=1
    assert r['converged']==(r['final']['maximum_force_ev_per_angstrom']<=.01)
    assert not r['converged']


def test_no_relaxation_is_explicit(backend):
    assert backend.assess(prototype('perovskite'))['relaxation']=={'attempted':False,'converged':None}


def test_unsupported_and_oversized_and_charged(backend):
    with pytest.raises(ValueError,match='not represented'):backend.predict(Structure(Lattice.cubic(4),['Og'],[[0,0,0]]))
    host=prototype('perovskite');host.make_supercell([3,3,1])
    with pytest.raises(ValueError,match='40'):backend.predict(host)
    host=prototype('perovskite');host.set_charge(1)
    with pytest.raises(ValueError,match='charged'):backend.predict(host)


@pytest.mark.parametrize('energy,forces',[(float('nan'),[[0,0,0]]),(float('inf'),[[0,0,0]]),(True,[[0,0,0]]),('1',[[0,0,0]]),(1.0,[[0,0]]),(1.0,[[float('nan'),0,0]]),(1.0,[['1','0','0']])])
def test_invalid_calculator_outputs_are_rejected(backend,energy,forces):
    class FakeAtoms:
        numbers=np.array([14])
        def __len__(self):return 1
        def get_potential_energy(self):return energy
        def get_forces(self):return forces
    with pytest.raises(ValueError):backend._prediction(FakeAtoms())


def test_stage5_partial_formal_charge_is_explicitly_normalized(backend):
    from src.energy.contracts import neutral_geometry_from_stage5
    host=prototype('perovskite');host.replace(1,'Zr')
    archived=Structure.from_dict(host.as_dict())
    assert archived.as_dict()['charge']==-4
    before=structure_fingerprint(archived)
    neutral=neutral_geometry_from_stage5(archived)
    assert neutral.as_dict()['charge']==0
    assert np.array_equal(neutral.cart_coords,archived.cart_coords)
    assert np.isfinite(backend.predict(neutral)['total_energy_ev'])
    assert structure_fingerprint(archived)==before


def test_public_predictions_actually_rerun_calculator(backend):
    from unittest.mock import patch
    host=prototype('perovskite')
    with patch.object(backend.calculator,'calculate',wraps=backend.calculator.calculate) as calculate:
        backend.predict(host);backend.predict(host)
        assert calculate.call_count==2


@pytest.mark.parametrize('case',['missing','tampered','outside'])
def test_checkpoint_integrity_guards(tmp_path,monkeypatch,case):
    import json
    from src.energy import backend as module
    monkeypatch.setattr(module,'PROJECT_ROOT',tmp_path)
    directory=tmp_path/'models/stage_06';directory.mkdir(parents=True)
    path=directory/'test.model'
    if case=='tampered':path.write_bytes(b'not a trusted checkpoint')
    manifest={'path':'../outside.model' if case=='outside' else 'models/stage_06/test.model','sha256':'0'*64}
    (directory/'checkpoint.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError):module.EnergyBackend()
