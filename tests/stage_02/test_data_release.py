"""Executed data-contract and preservation tests; no chemistry results fabricated."""
from pathlib import Path
import copy
import json
import numpy as np
import pandas as pd
import pytest
from src.data_audit.release import prepare_release,write_release,digest
from src.data_audit.validation import DataValidationError,load_json,validate_elements,validate_registry,validate_benchmark
from src.data_audit.schema import FEATURES,EXPECTED_NATIVE_MISSING

ROOT=Path(__file__).resolve().parents[2]

@pytest.fixture(scope='module')
def source():return load_json(ROOT/'data/raw/stage_02_sources/source_snapshot.json')

@pytest.fixture(scope='module')
def bundle(source):
    lookup=load_json(ROOT/'data/raw/stage_02_sources/doi_lookup.json')
    legacy=load_json(ROOT/'data/benchmark/benchmark_cases.json')
    with np.load(ROOT/'data/processed/atom2vec_embeddings_d20.npz',allow_pickle=False) as f:symbols=f['common_symbols'].tolist()
    return prepare_release(source,lookup,legacy,symbols)

def check(frame,bundle,prov=None):return validate_elements(frame,prov if prov is not None else bundle['provenance'],bundle['registry'])

def test_native_release_valid(bundle):
    assert check(bundle['elements'],bundle)=={'rows':94,'features':14,'provenance_cells':1316,'missing_cells':9}

def test_source_values_and_missingness_preserved(bundle,source):
    frame=bundle['elements'].set_index('symbol')
    for record in source['elements_1_94']:
        for feature,value in record['native_values'].items():
            actual=frame.loc[record['symbol'],feature]
            assert pd.isna(actual) if value is None else actual==value

def test_explicit_units_and_pn(bundle):
    f=bundle['elements'].set_index('symbol')
    assert f.loc['Ga','dipole_polarizability_bohr3']==50.0
    assert f.loc['H','pn_normalized_118']==105/118
    assert f.pn_normalized_118.between(0,1).all()
    assert bundle['metadata']['features']['dipole_polarizability_bohr3']['unit']=='bohr^3'

def test_no_fr_conductivity_invention(bundle):
    assert pd.isna(bundle['elements'].set_index('symbol').loc['Fr','thermal_conductivity_w_mk'])
    assert all(not r['project_imputed'] for r in bundle['provenance'])

def test_radius_estimates_separate_and_reproducible(bundle):
    f=bundle['elements'];fit=bundle['radius'];train=f.dropna(subset=['atomic_radius_slater_pm'])
    a,b=np.polyfit(train.covalent_radius_cordero_pm,train.atomic_radius_slater_pm,1)
    assert np.isclose(a,fit['slope']) and np.isclose(b,fit['intercept_pm'])
    assert fit['training_count']==89
    assert {r['symbol'] for r in fit['estimates']}=={'Kr','Xe','At','Rn','Fr'}
    assert all(not r['experimental'] and not r['written_into_native_table'] for r in fit['estimates'])

def test_source_estimates_different_from_project_imputation(bundle):
    density=[r for r in bundle['provenance'] if r['feature']=='density_g_cm3' and r['symbol'] in ['At','Fr']]
    assert all('upstream_density_is_theoretical_estimate' in r['upstream_quality_flags'] and not r['project_imputed'] for r in density)

def test_registry_recognizes_not_invents(bundle):
    assert validate_registry(bundle['registry'])=={'recognized':118,'feature_table_elements':94}
    assert all(r['native_feature_count']==0 for r in bundle['registry'] if r['atomic_number']>94)
    assert all(not r['scientific_substitution_validated'] for r in bundle['registry'])

@pytest.mark.parametrize('kind',['empty','duplicate','missing_column','negative_density','infinity','new_nan','string_type','bad_atomic_number','wrong_symbol','bad_pn','bad_normalization','fractional_electrons','count_mismatch'])
def test_corrupt_native_data_rejected(bundle,kind):
    f=bundle['elements'].copy(deep=True)
    if kind=='empty':f=f.iloc[:0]
    elif kind=='duplicate':f=pd.concat([f.iloc[:-1],f.iloc[[0]]],ignore_index=True)
    elif kind=='missing_column':f=f.drop(columns=['density_g_cm3'])
    elif kind=='negative_density':f.loc[0,'density_g_cm3']=-1
    elif kind=='infinity':f.loc[0,'density_g_cm3']=np.inf
    elif kind=='new_nan':f.loc[0,'density_g_cm3']=np.nan
    elif kind=='string_type':f['density_g_cm3']=f.density_g_cm3.astype(str)
    elif kind=='bad_atomic_number':f['atomic_number']=f.atomic_number.astype(str)
    elif kind=='wrong_symbol':f.loc[0,'symbol']='Xx'
    elif kind=='bad_pn':f.loc[0,'mendeleev_number']=119
    elif kind=='bad_normalization':f.loc[0,'pn_normalized_118']=105/103
    elif kind=='fractional_electrons':f['s_valence_electrons']=f.s_valence_electrons.astype(float);f.loc[0,'s_valence_electrons']=1.5
    elif kind=='count_mismatch':f.loc[0,'native_feature_count']=0
    with pytest.raises(DataValidationError):check(f,bundle)

@pytest.mark.parametrize('kind',['duplicate','missing','wrong_unit','wrong_value','imputed','missing_source'])
def test_bad_provenance_rejected(bundle,kind):
    prov=copy.deepcopy(bundle['provenance'])
    if kind=='duplicate':prov[-1]=prov[0]
    elif kind=='missing':prov.pop()
    elif kind=='wrong_unit':prov[0]['unit']='fake'
    elif kind=='wrong_value':prov[0]['value']=999
    elif kind=='imputed':prov[0]['project_imputed']=True
    elif kind=='missing_source':prov[0]['source_locator']=''
    with pytest.raises(DataValidationError):check(bundle['elements'],bundle,prov)

@pytest.mark.parametrize('kind',['missing_element','duplicate_symbol','claims_validation','fake_features','boolean_z','boolean_feature_count'])
def test_registry_errors_rejected(bundle,kind):
    r=copy.deepcopy(bundle['registry'])
    if kind=='missing_element':r.pop()
    elif kind=='duplicate_symbol':r[-1]['symbol']=r[0]['symbol']
    elif kind=='claims_validation':r[0]['scientific_substitution_validated']=True
    elif kind=='fake_features':r[-1]['native_feature_count']=14
    elif kind=='boolean_z':r[0]['atomic_number']=True
    elif kind=='boolean_feature_count':r[0]['native_feature_count']=True
    with pytest.raises(DataValidationError):validate_registry(r)

def test_legacy_cases_preserved_but_not_certified(bundle):
    release=bundle['benchmark'];result=validate_benchmark(release)
    assert result=={'cases':16,'claims':23,'eligible_claims':0}
    old=load_json(ROOT/'data/benchmark/benchmark_cases.json')
    assert [c['legacy_record'] for c in release['substitution_cases']]==old['primary_cases']
    assert [c['legacy_record'] for c in release['doping_cases']]==old['secondary_doping_cases']
    assert all(c['label']=='unknown' for case in release['substitution_cases']+release['doping_cases'] for c in case['claims'])

@pytest.mark.parametrize('kind',['unknown_credit','missing_locator','missing_scientific_class','missing_conditions','duplicate_case','track_mix','unknown_candidate','invalid_target'])
def test_invalid_benchmark_admission_rejected(bundle,kind):
    release=copy.deepcopy(bundle['benchmark']);c=release['substitution_cases'][0]['claims'][0]
    if kind=='unknown_credit':c['eligible_for_quantitative_evaluation']=True
    elif kind in ['missing_locator','missing_scientific_class','missing_conditions']:
        c.update(label='documented_positive',eligible_for_quantitative_evaluation=True)
        if kind!='missing_locator':c.update(supporting_source_url='https://example.invalid/test-fixture',source_locator='synthetic software fixture only')
        if kind=='missing_conditions':c['evidence_class']='experimental'
    elif kind=='duplicate_case':release['substitution_cases'][-1]['case_id']=release['substitution_cases'][0]['case_id']
    elif kind=='track_mix':release['doping_cases'][0]['track']='substitution'
    elif kind=='unknown_candidate':c['candidate']='Xx'
    elif kind=='invalid_target':release['substitution_cases'][0]['legacy_record']['target_element']='Xx'
    with pytest.raises(DataValidationError):validate_benchmark(release)

def test_registry_metadata_not_chemical_evidence(bundle):
    cases={c['case_id']:c for c in bundle['benchmark']['substitution_cases']+bundle['benchmark']['doping_cases']}
    assert cases['BM-P07']['claims'][0]['review_status']=='citation_mismatch'
    assert 'KSnAs' in cases['BM-P07']['claims'][0]['resolved_titles'][0]
    assert cases['BM-S04']['claims'][0]['label']=='unknown'

def test_json_errors_reported(tmp_path):
    with pytest.raises(DataValidationError):load_json(tmp_path/'missing.json')
    path=tmp_path/'bad.json';path.write_text('{broken',encoding='utf-8')
    with pytest.raises(DataValidationError):load_json(path)
    path.write_text('{"x": NaN}',encoding='utf-8')
    with pytest.raises(DataValidationError):load_json(path)

def test_release_refuses_overwrite_and_preserves_files(bundle,tmp_path):
    data=tmp_path/'data';benchmark=tmp_path/'benchmark'
    write_release(bundle,data,benchmark,ROOT)
    before={p.name:digest(p) for p in data.iterdir()}
    with pytest.raises(DataValidationError):write_release(bundle,data,benchmark,ROOT)
    assert before=={p.name:digest(p) for p in data.iterdir()}

def test_outside_project_output_refused(bundle,tmp_path):
    with pytest.raises(DataValidationError):write_release(bundle,ROOT.parent/'forbidden-stage2-test',tmp_path/'benchmark',ROOT)
    assert not (ROOT.parent/'forbidden-stage2-test').exists()

def test_same_snapshot_build_identical(bundle,source):
    other=prepare_release(source,load_json(ROOT/'data/raw/stage_02_sources/doi_lookup.json'),load_json(ROOT/'data/benchmark/benchmark_cases.json'),[r['symbol'] for r in bundle['registry'] if r['legacy_atom2vec_supported']])
    pd.testing.assert_frame_equal(bundle['elements'],other['elements'])
    assert bundle['provenance']==other['provenance'] and bundle['benchmark']==other['benchmark'] and bundle['radius']==other['radius']

def test_persisted_release_matches_current_builder(bundle):
    data=ROOT/'data/processed/v2_0_0'
    pd.testing.assert_frame_equal(pd.read_parquet(data/'elements_native.parquet'),bundle['elements'])
    assert load_json(ROOT/'data/benchmark/v2_0_0/benchmark_review.json')==bundle['benchmark']
    assert load_json(data/'element_registry.json')==bundle['registry']
    assert load_json(data/'radius_estimates.json')==bundle['radius']
    prov=[json.loads(line) for line in (data/'cell_provenance.jsonl').read_text(encoding='utf-8').splitlines()]
    assert prov==bundle['provenance']
