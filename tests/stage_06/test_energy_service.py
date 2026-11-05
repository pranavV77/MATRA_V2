import pytest
from src.energy.service import EnergyService


@pytest.fixture(scope='module')
def service():
    return EnergyService(runner=lambda tasks:{'ok':True,'tasks_seen':tasks})


def test_geometry_and_energy_bridge_inputs(service):
    r=service.assess({'host_id':'perovskite','target':'Ti','site_index':1,'candidate_symbol':'Zr'})
    tasks=r['energy_assessment']['tasks_seen']
    assert len(tasks)==2 and tasks[0]['relax'] is False
    assert tasks[1]['structure']['sites'][1]['species'][0]['element']=='Zr'
    assert tasks[1]['structure']['charge']==0
    assert all('oxidation_state' not in s['species'][0] for s in tasks[1]['structure']['sites'])
    assert r['cross_composition_ranking']=='not_permitted'
    assert r['band_gap_preservation']=='not_assessed'


def test_whole_orbit_not_silently_changed_to_one_site(service):
    r=service.assess({'host_id':'wurtzite','target':'Ga','site_index':0,'candidate_symbol':'Al','mode':'symmetry_orbit'})
    assert r['trial_metadata']['replacement_count']==2
    assert r['trial_metadata']['target_sublattice_fraction']==1


@pytest.mark.parametrize('updates',[{'target':'Ti','site_index':0,'candidate_symbol':'Zr'}, {'target':'Ti','site_index':1,'candidate_symbol':'Og'},
    {'target':'Ti','site_index':1,'candidate_symbol':'Ti'}, {'target':'Ti','site_index':1,'candidate_symbol':'Zr','relax':1},
    {'target':'Ti','site_index':1,'candidate_symbol':'Zr','max_steps':101}, {'target':'Ti','site_index':1,'candidate_symbol':'Zr','mode':'unsupported'},
    {'target':'Ti','site_index':1,'candidate_symbol':'Zr','supercell':[3,3,1]}, {'target':'Ti','site_index':1,'candidate_symbol':'Zr','formation_energy':0},{}])
def test_service_rejects_bad_inputs_before_worker(service,updates):
    with pytest.raises((ValueError,TypeError)):service.assess({'host_id':'perovskite',**updates})


def test_non_object(service):
    with pytest.raises(ValueError):service.assess([])
