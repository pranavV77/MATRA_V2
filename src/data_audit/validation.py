"""Fail-fast checks for versioned data, not a chemistry success classifier."""
from pathlib import Path
import json
import math
import numbers
import numpy as np
import pandas as pd
from .schema import FEATURES, SUBSHELL_BOUNDS, EXPECTED_NATIVE_MISSING

class DataValidationError(ValueError):
    """A versioned release violates its declared data contract."""

def require(condition,message):
    if not condition:raise DataValidationError(message)

def load_json(path):
    path=Path(path)
    require(path.is_file(),f'Required JSON file missing or not a file: {path}')
    try:
        with path.open(encoding='utf-8-sig') as f:
            return json.load(f,parse_constant=lambda x:(_ for _ in ()).throw(DataValidationError(f'Nonstandard JSON constant: {x}')))
    except (json.JSONDecodeError,UnicodeError) as exc:raise DataValidationError(f'Invalid JSON in {path}: {exc}') from exc

def validate_elements(frame,provenance,registry):
    require(isinstance(frame,pd.DataFrame),'Element data must be a DataFrame')
    required={'atomic_number','symbol','name','mendeleev_number','pn_normalized_118',*FEATURES}
    require(required.issubset(frame.columns),f'Missing columns: {sorted(required-set(frame.columns))}')
    require(len(frame)==94,'Native feature release must contain exactly Z=1..94')
    require(pd.api.types.is_integer_dtype(frame.atomic_number) and not pd.api.types.is_bool_dtype(frame.atomic_number),'Atomic numbers must be integers, not booleans or strings')
    require(frame.atomic_number.tolist()==list(range(1,95)),'Atomic numbers must be unique, sorted and cover Z=1..94')
    require(frame.symbol.notna().all() and frame.symbol.is_unique,'Element symbols must be present and unique')
    mapping={int(r['atomic_number']):r['symbol'] for r in registry}
    require(all(mapping.get(int(r.atomic_number))==r.symbol for r in frame.itertuples()),'Atomic number/symbol identity mismatch')
    require(pd.api.types.is_integer_dtype(frame.mendeleev_number),'PN must be integer-valued')
    require(frame.mendeleev_number.between(1,118).all() and frame.mendeleev_number.is_unique,'PN values must be unique in 1..118')
    require(np.allclose(frame.pn_normalized_118,frame.mendeleev_number/118.0,rtol=0,atol=1e-14),'PN normalization must be PN/118')
    require(isinstance(provenance,list),'Provenance must be a list')
    keys=[(r['symbol'],r['feature']) for r in provenance]
    require(len(keys)==94*len(FEATURES) and len(set(keys))==len(keys),'Require exactly one provenance record per element-feature cell')
    lookup={(r['symbol'],r['feature']):r for r in provenance}
    missing_cells={(r.symbol,f) for r in frame.itertuples() for f in FEATURES if pd.isna(getattr(r,f))}
    require(missing_cells==EXPECTED_NATIVE_MISSING,'Native missingness changed from the audited source release; explicit review required')
    for feature,(unit,_) in FEATURES.items():
        series=frame[feature]
        require(pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series),f'{feature}: numeric dtype required')
        nonmissing=series.dropna().to_numpy(dtype=float)
        require(np.isfinite(nonmissing).all(),f'{feature}: infinite or invalid values')
        require((nonmissing>=0).all(),f'{feature}: negative values are invalid')
        if feature not in SUBSHELL_BOUNDS:
            require((nonmissing>0).all(),f'{feature}: zero values are invalid')
        else:
            require((nonmissing<=SUBSHELL_BOUNDS[feature]).all(),f'{feature}: subshell count out of range')
            require(np.equal(nonmissing,np.floor(nonmissing)).all(),f'{feature}: electron counts must be integers')
        if feature=='valence_electrons':require(np.equal(nonmissing,np.floor(nonmissing)).all(),'Valence counts must be integers')
        for row in frame[['symbol',feature]].itertuples(index=False,name=None):
            symbol,value=row;record=lookup.get((symbol,feature))
            require(record is not None,f'Missing provenance: {symbol}/{feature}')
            require(record.get('unit')==unit,f'Unit mismatch: {symbol}/{feature}')
            require(record.get('source_locator') and record.get('origin'),f'Missing source lineage: {symbol}/{feature}')
            stored=record.get('value')
            require((pd.isna(value) and stored is None) or (stored is not None and isinstance(stored,numbers.Real) and not isinstance(stored,bool) and math.isfinite(float(stored)) and not pd.isna(value) and math.isclose(float(value),float(stored),rel_tol=0,abs_tol=1e-12)),f'Value/provenance mismatch: {symbol}/{feature}')
            require((record['origin']=='missing')==pd.isna(value),f'Missingness classification mismatch: {symbol}/{feature}')
            require(record.get('project_imputed') is False,'Native table cannot contain project-imputed values')
    require(frame.valence_electrons.dropna().between(1,18).all(),'Valence count out of project bounds')
    if 'native_feature_count' in frame:
        require(np.array_equal(frame.native_feature_count.to_numpy(),frame[list(FEATURES)].notna().sum(axis=1).to_numpy()),'Available-feature count mismatch')
    return {'rows':94,'features':len(FEATURES),'provenance_cells':len(provenance),'missing_cells':int(frame[list(FEATURES)].isna().sum().sum())}

def validate_registry(registry):
    require(isinstance(registry,list) and len(registry)==118,'Registry must contain 118 elements')
    require([r['atomic_number'] for r in registry]==list(range(1,119)),'Registry must cover unique sorted Z=1..118')
    require(all(type(r['atomic_number']) is int for r in registry),'Registry atomic numbers must be integers, not booleans')
    require(len({r['symbol'] for r in registry})==118,'Registry symbols must be unique')
    require(all(r.get('recognized') is True for r in registry),'All registry entries must be recognized')
    require(all(r.get('scientific_substitution_validated') is False for r in registry),'Registry cannot assert chemical validation from coverage')
    for r in registry:
        require(type(r.get('native_feature_table_present')) is bool,'Feature availability must be a boolean')
        require(type(r.get('native_feature_count')) is int and 0<=r['native_feature_count']<=len(FEATURES),'Invalid available-feature count')
        require(r.get('native_feature_table_present')==(r['atomic_number']<=94),'Feature-table scope mismatch')
        if r['atomic_number']>94:require(r['native_feature_count']==0,'No unsupported synthetic features allowed')
    return {'recognized':118,'feature_table_elements':sum(r['native_feature_table_present'] for r in registry)}

def validate_benchmark(release):
    from pymatgen.core import Element
    require(isinstance(release,dict),'Benchmark release must be an object')
    cases=release.get('substitution_cases',[])+release.get('doping_cases',[])
    require(len(cases)==16,'Audit release must retain all 16 legacy cases')
    require(len({r['case_id'] for r in cases})==16,'Duplicate case IDs')
    count=0;admitted=0
    for case in cases:
        require(case.get('legacy_record') and case.get('claims'),'Original record and claim review required')
        require(case['track'] in ('substitution','doping'),'Unknown track')
        require((case['track']=='doping')==case['case_id'].startswith('BM-S'),'Substitution/doping track mix-up')
        require(len({c['candidate'] for c in case['claims']})==len(case['claims']),'Duplicate candidate claim')
        target=case['legacy_record'].get('target_element')
        require(isinstance(target,str) and Element.is_valid_symbol(target),'Invalid benchmark target element')
        expected=case['legacy_record'].get('known_substituents') if case['track']=='substitution' else [case['legacy_record'].get('known_dopant')]
        require({c['candidate'] for c in case['claims']}==set(expected),'Candidate claims must retain the legacy assertion identities')
        for claim in case['claims']:
            count+=1
            require(claim['candidate']!=case['legacy_record']['target_element'],'Target cannot be own candidate')
            require(isinstance(claim['candidate'],str) and Element.is_valid_symbol(claim['candidate']),'Invalid benchmark candidate element')
            require(claim['label'] in ('unknown','documented_positive','documented_negative','conflicting'),'Invalid label')
            require(isinstance(claim['eligible_for_quantitative_evaluation'],bool),'Eligibility must be explicit boolean')
            require(claim.get('review_reason'),'Review reason required')
            if claim['eligible_for_quantitative_evaluation']:
                admitted+=1
                require(claim['label'] in ('documented_positive','documented_negative'),'Unknown claims cannot earn accuracy credit')
                require(claim.get('supporting_source_url') and claim.get('source_locator'),'Admitted claim requires traceable passage locator')
                require(claim.get('evidence_class') in ('experimental','computational'),'Admitted claim requires scientific evidence class; DOI metadata alone is insufficient')
                require(all(claim.get(k) is True for k in ('host_verified','phase_verified','site_verified','concentration_verified')),'Admitted contextual claim requires verified conditions')
    require(count==23,'Retain 18 substitution and 5 doping candidate claims')
    return {'cases':16,'claims':count,'eligible_claims':admitted}
