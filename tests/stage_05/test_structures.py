"""Executed geometric invariants, analytical prototypes and malformed inputs."""
import copy
import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
from pymatgen.core import Lattice, Structure
from pymatgen.io.cif import CifWriter

from src.structures.hosts import analyze_sites, diagonal_supercell, geometry_check, load_cif, parse_cif, structure_fingerprint
from src.structures.candidates import CandidateGenerator, export_configurations, formal_charge_screen
from src.structures.prototypes import prototype
from src.structures.service import StructureService


@pytest.fixture(scope='module')
def generator(): return CandidateGenerator()


@pytest.mark.parametrize('name,sg,counts',[('perovskite',221,[12,6,2,2,2]),('wurtzite',186,[4,4,4,4])])
def test_analytical_site_counts_and_symmetry(name,sg,counts):
    host=prototype(name);before=structure_fingerprint(host);a=analyze_sites(host)
    assert a['spacegroup']['number']==sg
    assert [s['nearest_shell_count'] for s in a['sites']]==counts
    assert sorted(i for g in a['orbits'] for i in g['indices'])==list(range(len(host)))
    assert structure_fingerprint(host)==before
    assert all(s['neighbor_search_complete_for_shell'] for s in a['sites'])
    assert a['geometry']['chemical_validity_established'] is False


def test_periodic_images_count_even_single_atom():
    a=analyze_sites(Structure(Lattice.cubic(3),['Si'],[[0,0,0]]))
    assert a['sites'][0]['nearest_shell_count']==6
    assert a['sites'][0]['nearest_distance_angstrom']==pytest.approx(3)


@pytest.mark.parametrize('name',['perovskite','wurtzite'])
def test_cif_roundtrip_and_no_primitive_reduction(name):
    host=prototype(name);parsed,metadata=parse_cif(str(CifWriter(host)))
    assert len(parsed)==len(host)
    assert parsed.composition.element_composition==host.composition.element_composition
    assert parsed.lattice.volume==pytest.approx(host.volume,rel=1e-7)
    assert metadata['primitive_reduction'] is False
    assert len(metadata['input_sha256'])==64


@pytest.mark.parametrize('text',['',' ','not a CIF','data_bad\n_cell_length_a 2',None,{},'x'*500001],ids=['empty','space','not-cif','incomplete','none','object','oversized'])
def test_bad_cif(text):
    with pytest.raises((ValueError,TypeError)): parse_cif(text)


def test_multi_phase_not_silently_first():
    text=str(CifWriter(prototype('perovskite')))
    with pytest.raises(ValueError,match='Exactly one CIF data block'):
        parse_cif(text+'\n'+text.replace('data_SrTiO3','data_other'))


def test_disorder_rejected():
    host=Structure(Lattice.cubic(4),[{'Ga':.5,'Al':.5},'N'],[[0,0,0],[.5,.5,.5]])
    with pytest.raises(ValueError,match='occupancies'): geometry_check(host)
    with pytest.raises(ValueError): parse_cif(str(CifWriter(host)))


@pytest.mark.parametrize('positions',[[[0,0,0],[0,0,0]],[[0,0,0],[1,0,0]],[[0,0,0],[.01,0,0]]])
def test_periodic_collisions_rejected(positions):
    host=Structure(Lattice.cubic(4),['Ga','N'],positions)
    with pytest.raises(ValueError,match='Overlapping'): geometry_check(host)


@pytest.mark.parametrize('length',[.1,.99,201])
def test_bounded_lattice(length):
    with pytest.raises(ValueError): geometry_check(Structure(Lattice.cubic(length),['Si'],[[0,0,0]]))


def test_invalid_geometry_types_and_nonfinite():
    with pytest.raises(TypeError): geometry_check('SrTiO3')
    with pytest.raises(ValueError): geometry_check(Structure(Lattice.cubic(4),[],[]))
    host=prototype('perovskite');host[0].frac_coords[0]=np.nan
    with pytest.raises(ValueError,match='finite'): geometry_check(host)
    with pytest.raises(ValueError): geometry_check(Structure(Lattice.cubic(4,pbc=(True,True,False)),['Si'],[[0,0,0]]))


@pytest.mark.parametrize('factors',[[],[1,1],[0,1,1],[-1,1,1],[True,1,1],[1.5,1,1],[5,1,1],'222',[4,4,4]])
def test_bad_supercells(factors):
    with pytest.raises((ValueError,TypeError)): diagonal_supercell(prototype('perovskite'),factors)


def test_supercell_exact_volume_composition_and_immutability():
    host=prototype('perovskite');fingerprint=structure_fingerprint(host)
    expanded=diagonal_supercell(host,[2,2,2])
    assert len(expanded)==40 and expanded.volume==pytest.approx(host.volume*8)
    assert expanded.composition['Ti']==8
    assert structure_fingerprint(host)==fingerprint


@pytest.mark.parametrize('kwargs',[{'symprec':0},{'symprec':float('nan')},{'symprec':True},{'symprec':.2},{'shell_factor':.9},{'shell_factor':2},{'neighbor_radius':9},{'neighbor_radius':0}])
def test_bad_analysis_parameters(kwargs):
    with pytest.raises((ValueError,TypeError)): analyze_sites(prototype('perovskite'),**kwargs)


def test_symmetry_failure_explicit():
    with patch('src.structures.hosts.SpacegroupAnalyzer',side_effect=RuntimeError('dependency failure')):
        with pytest.raises(ValueError,match='no fallback'): analyze_sites(prototype('perovskite'))


def test_no_neighbors_does_not_invent_coordination():
    a=analyze_sites(Structure(Lattice.cubic(20),['Si'],[[0,0,0]]))
    assert a['sites'][0]['nearest_shell_count']==0
    assert a['sites'][0]['neighbor_search_complete_for_shell'] is False


@pytest.mark.parametrize('symprec',[.001,.01,.05])
def test_ideal_symmetry_tolerance_sensitivity(symprec):
    assert analyze_sites(prototype('perovskite'),symprec=symprec)['spacegroup']['number']==221


def test_generate_known_site_and_fraction(generator):
    host=prototype('wurtzite');before=structure_fingerprint(host)
    result=generator.generate(host,'Ga',0,k=1,candidate_symbols=['Al'],candidate_oxidation_states={'Al':3})
    c=result['configurations'][0];trial=Structure.from_dict(c['structure'])
    assert c['target_sublattice_fraction']==.5
    assert c['all_atoms_replaced_fraction']==.25
    assert c['selected_orbit_fraction']==.5
    assert trial[0].specie.symbol=='Al' and trial[1].specie.symbol=='Ga'
    assert c['formal_charge_screen']['trial_formal_charge_e']==0
    assert c['formal_charge_screen']['compensation_needed_under_assumptions'] is False
    assert c['coordinates_and_lattice_preserved']
    assert structure_fingerprint(host)==before
    assert c['validation']['energy_stability']=='not_run'


def test_orbit_and_single_site_are_distinct(generator):
    single=generator.generate(prototype('wurtzite'),'Ga',0,k=1,candidate_symbols=['Al'])
    orbit=generator.generate(prototype('wurtzite'),'Ga',0,k=1,candidate_symbols=['Al'],mode='symmetry_orbit')
    assert single['configurations'][0]['replacement_count']==1
    assert orbit['configurations'][0]['replacement_count']==2
    assert orbit['configurations'][0]['target_sublattice_fraction']==1


def test_supercell_fraction_expanded_site_index(generator):
    r=generator.generate(prototype('perovskite'),'Ti',8,k=1,supercell=[2,2,2],candidate_symbols=['Zr'])
    c=r['configurations'][0]
    assert c['target_sublattice_fraction']==pytest.approx(1/8)
    assert c['all_atoms_replaced_fraction']==pytest.approx(1/40)
    assert c['formal_charge_screen']['status']=='unknown'


def test_charge_bookkeeping_not_a_defect_prediction():
    c=formal_charge_screen(prototype('perovskite'),[1],'Nb',5)
    assert c['formal_charge_delta_e']==1 and c['trial_formal_charge_e']==1
    assert c['compensation_needed_under_assumptions'] is True
    host=prototype('perovskite');host.remove_oxidation_states()
    assert formal_charge_screen(host,[1],'Nb',5)['status']=='unknown'


@pytest.mark.parametrize('overrides',[{'target':'Ga'},{'target':'ti'},{'site_index':0},{'site_index':100},{'site_index':-1},{'site_index':True},{'k':0},{'k':21},{'mode':'doping'},{'candidate_symbols':[]},{'candidate_symbols':['Ti']},{'candidate_symbols':['Zr','Zr']},{'candidate_symbols':['Og']},{'candidate_symbols':['XX']},{'candidate_oxidation_states':[]},{'candidate_oxidation_states':{'Zr':float('nan')}},{'candidate_oxidation_states':{'Zr':True}},{'candidate_oxidation_states':{'Og':4}}])
def test_bad_generation_inputs(generator,overrides):
    kwargs={'target':'Ti','site_index':1,'k':1,'candidate_symbols':['Zr']};kwargs.update(overrides)
    with pytest.raises((ValueError,TypeError)): generator.generate(prototype('perovskite'),**kwargs)


def test_deterministic_no_reference_rank_changes_and_no_aliasing(generator):
    host=prototype('perovskite');a=generator.generate(host,'Ti',1,k=3);b=generator.generate(host,'Ti',1,k=3)
    assert a==b
    assert [c['candidate_element'] for c in a['configurations']]==[r['candidate_element'] for r in generator.fusion.recommend('Ti',k=3)['rankings']]
    a['configurations'][0]['structure']['sites'][0]['abc'][0]=999
    assert generator.generate(host,'Ti',1,k=3)==b


def test_host_element_candidates_are_explicitly_flagged(generator):
    r=generator.generate(prototype('perovskite'),'Ti',1,k=1,candidate_symbols=['Sr'])
    assert r['configurations'][0]['candidate_already_present_in_host'] is True


def test_exports_and_roundtrip(generator,tmp_path):
    r=generator.generate(prototype('wurtzite'),'Ga',0,k=1,candidate_symbols=['Al'])
    a=export_configurations(r,tmp_path);b=export_configurations(r,tmp_path)
    assert a['directory']!=b['directory']
    archive=json.loads(Path(a['record_path']).read_text())
    cif=Path(a['directory'])/archive['cif_files'][0]['path'];host,_=load_cif(cif)
    assert host.composition.element_composition['Al']==1
    with pytest.raises(ValueError): export_configurations(r,Path('C:/outside-project'))


def test_local_import_path_errors(tmp_path):
    with pytest.raises(FileNotFoundError): load_cif(tmp_path/'missing.cif')
    with pytest.raises(ValueError): load_cif('https://example.com/x.cif')
    with pytest.raises(ValueError): load_cif('C:/outside-project/x.cif')
    path=tmp_path/'x.txt';path.write_text('invalid')
    with pytest.raises(ValueError): load_cif(path)


@pytest.mark.parametrize('payload',[{},[],{'host_id':'unknown'},{'host_id':'perovskite','cif_text':'x'},{'host_id':'perovskite','extra':1}])
def test_service_rejects_invalid_host_payload(generator,payload):
    with pytest.raises((ValueError,TypeError)): StructureService(generator.fusion).analyze(payload)


def test_service_provenance_and_export(generator,tmp_path):
    s=StructureService(generator.fusion,tmp_path);p={'host_id':'perovskite','target':'Ti','site_index':1,'k':1}
    a=s.analyze({'host_id':'perovskite'})
    assert a['provenance']['evidence_class']=='analytically_constructed_demonstration'
    result=s.generate(p)
    assert result['provenance']['input_geometry_sha256']==a['analysis']['structure_sha256']
    assert s.export(p)['saved']
    catalog=s.catalog();catalog['hosts'].clear();assert len(s.catalog()['hosts'])==3


def test_frozen_source_cif_and_generation(generator):
    s=StructureService(generator.fusion)
    a=s.analyze({'host_id':'aflow_zns'})
    assert a['analysis']['spacegroup']['number']==186
    assert all(x['nearest_shell_count']==4 for x in a['analysis']['sites'])
    assert a['provenance']['file_sha256']==a['provenance']['acquisition']['sha256']
    index=next(x['index'] for x in a['analysis']['sites'] if x['element']=='Zn')
    r=s.generate({'host_id':'aflow_zns','target':'Zn','site_index':index,'k':1})
    assert r['configurations'][0]['target_sublattice_fraction']==.5


def test_export_source_symmetry_labels_are_unique(generator,tmp_path):
    import warnings
    service=StructureService(generator.fusion)
    a=service.analyze({'host_id':'aflow_zns'})
    index=next(s['index'] for s in a['analysis']['sites'] if s['element']=='Zn')
    result=service.generate({'host_id':'aflow_zns','target':'Zn','site_index':index,'k':3})
    for c in result['configurations']:
        s=Structure.from_dict(c['structure'])
        assert len({x.label for x in s})==len(s)
    with warnings.catch_warnings():
        warnings.simplefilter('error',UserWarning)
        saved=export_configurations(result,tmp_path)
    assert saved['configurations']==3


def test_cli_analysis(capsys):
    from src.structures.cli import main
    main(['--host','perovskite'])
    assert json.loads(capsys.readouterr().out)['analysis']['site_count']==5


@pytest.mark.parametrize('args',[['--host','perovskite','--target','Ti'],['--host','perovskite','--export'],['--host','wurtzite','--target','Ga','--site','2']])
def test_cli_invalid(args):
    from src.structures.cli import main
    with pytest.raises(SystemExit) as exc:main(args)
    assert exc.value.code==2
