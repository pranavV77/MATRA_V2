"""Prepare a versioned, source-traceable release without mutating legacy data.

The native table retains missing values. Radius regression is a separate,
explicitly estimated artifact. No unsupported Fr conductivity is generated.
"""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import numpy as np
import pandas as pd
from .schema import FEATURES, LEGACY_FEATURE_MAP, SOURCE_ESTIMATED_DENSITIES, SOURCE_URLS
from .validation import DataValidationError, require, load_json, validate_elements, validate_registry, validate_benchmark

REVIEW = {
 'BM-P01':('partial_support','Al-alloy paper is computational; does not by itself verify every Al/In experimental, concentration and site claim.'),
 'BM-P02':('review_source','Registered source is a III-nitride review, not extracted direct experimental evidence for each claimed condition.'),
 'BM-P03':('unresolved_identifier','DOI registry query returned HTTP 404. This does not prove the chemistry is false or that no correct paper exists.'),
 'BM-P04':('partial_support','Registered title concerns Se-containing MoS2, but the complete phase, site, authorship and concentration assertions need primary passage review.'),
 'BM-P05':('citation_mismatch','Registered paper is about PVDF pyroelectric detector arrays, not the stated BaTiO3 substitution study.'),
 'BM-P06':('unresolved_identifier','Book DOI did not resolve through the queried registry; exact supporting chapter and passage not established.'),
 'BM-P07':('citation_mismatch','DataCite DOI identifies Materials Data on KSnAs, not SrTiO3.'),
 'BM-P08':('citation_mismatch','DataCite DOI identifies Materials Data on KSnAs, not SrTiO3.'),
 'BM-P09':('unresolved_identifier','DOI did not resolve in the query. The recorded journal/case pairing needs re-identification and primary evidence.'),
 'BM-P10':('partial_support','Registered paper concerns Bi/Sb telluride alloys; this alone does not establish every full-range site-specific legacy assertion.'),
 'BM-P11':('unresolved_identifier','DataCite DOI query returned HTTP 404; actual supporting structure and experimental claim not verified.'),
 'BM-S01':('citation_mismatch','Registered DOI is a Cu2ZnSnS4 solar-cell etching paper, not Si doping in Ga2O3.'),
 'BM-S02':('citation_mismatch','Registered DOI is an electron-holography/MOSFET paper, not Sn doping in Ga2O3.'),
 'BM-S03':('partial_support','Registered source concerns InGaN quantum-well LEDs; Mg-on-Ga site, dilute level and activation assertions require an exact supporting passage or replacement primary study.'),
 'BM-S04':('citation_mismatch','Publisher and Crossref identify Order within disorder, about glass structure, not Nb doping in SrTiO3.'),
 'BM-S05':('unresolved_identifier','DOI registry query returned HTTP 404; Re-on-Mo evidence and concentration remain unverified.'),
}
SOURCES={
 'covalent_radius_cordero_pm':'mendeleev.Element.covalent_radius_cordero',
 'atomic_radius_slater_pm':'mendeleev.Element.atomic_radius',
 'first_ionization_energy_ev':'mendeleev.Element.ionenergies[1]',
 'dipole_polarizability_bohr3':'mendeleev.Element.dipole_polarizability',
 'valence_electrons':'mendeleev.Element.nvalence()',
}

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def prepare_release(snapshot,doi_lookup,legacy_benchmark,embedding_symbols):
    require(snapshot['versions']['mendeleev']=='1.2.0','Source version changed; re-audit conventions first')
    require(len(snapshot['source_registry'])==118,'Source registry incomplete')
    rows=[];provenance=[]
    for source in snapshot['elements_1_94']:
        z=source['atomic_number'];symbol=source['symbol'];vals=source['native_values']
        row={k:source[k] for k in ('atomic_number','symbol','name','period','group_id','block','mendeleev_number')}
        row['pn_normalized_118']=source['mendeleev_number']/118.0
        row.update(vals)
        row['native_feature_count']=sum(v is not None for v in vals.values())
        row['density_estimated_in_upstream_source']=symbol in SOURCE_ESTIMATED_DENSITIES
        rows.append(row)
        for feature,(unit,description) in FEATURES.items():
            value=vals[feature];origin='source_library_value'
            locator=source['selected_sources'].get(feature,SOURCES.get(feature,'project.parse_subshell_valence'))
            if feature.endswith('_valence_electrons'):origin='project_rule_derived'
            if feature=='atomic_molar_volume_cm3_mol_atoms':origin='derived_ratio';locator='mendeleev.atomic_weight / selected source density'
            if value is None:origin='missing'
            flags=[]
            if symbol in SOURCE_ESTIMATED_DENSITIES and feature in ('density_g_cm3','atomic_molar_volume_cm3_mol_atoms'):
                flags.append('upstream_density_is_theoretical_estimate')
            if locator.startswith('pymatgen'):flags.append('fallback_library')
            provenance.append({'atomic_number':z,'symbol':symbol,'feature':feature,'value':value,'unit':unit,
                'origin':origin,'project_imputed':False,'upstream_quality_flags':flags,
                'source_locator':locator,'source_snapshot_record':f'elements_1_94[atomic_number={z}]',
                'source_versions':snapshot['versions'],'conditions':'See captured propertymetadata; phase/temperature are not uniform across features.',
                'measurement_status':'not independently classified as experimental; library lineage only'})
    frame=pd.DataFrame(rows)
    registry=[];native={r['symbol']:r for r in rows};embedding_symbols=set(embedding_symbols)
    for s in snapshot['source_registry']:
        z=int(s['atomic_number']);symbol=s['symbol']
        registry.append({'atomic_number':z,'symbol':symbol,'name':s['name'],'recognized':True,
          'pn_source_available':s['mendeleev_number'] is not None,'source_mendeleev_number':s['mendeleev_number'],
          'native_feature_table_present':z<=94,'native_feature_count':native.get(symbol,{}).get('native_feature_count',0),
          'legacy_pn_target_supported':z<=94,'legacy_pn_candidate_supported':z<=94 and s['group_id']!=18,
          'legacy_property_supported':z<=94 and s['group_id']!=18,'legacy_atom2vec_supported':symbol in embedding_symbols,
          'scientific_substitution_validated':False,'site_validation_available':False,
          'note':'Recognition/source availability is not predictive or experimental validation.'})
    validate_registry(registry);native_check=validate_elements(frame,provenance,registry)
    # Radius fit uses only known source radii, never benchmark labels.
    training=frame.dropna(subset=['atomic_radius_slater_pm','covalent_radius_cordero_pm'])
    x=training.covalent_radius_cordero_pm.to_numpy(float);y=training.atomic_radius_slater_pm.to_numpy(float)
    slope,intercept=np.polyfit(x,y,1);pred=slope*x+intercept
    loo=[]
    for i in range(len(x)):
        mask=np.arange(len(x))!=i;a,b=np.polyfit(x[mask],y[mask],1);loo.append(float(a*x[i]+b-y[i]))
    estimates=[{'symbol':r.symbol,'atomic_number':int(r.atomic_number),'estimated_atomic_radius_slater_pm':round(float(slope*r.covalent_radius_cordero_pm+intercept),1),
                'origin':'project_regression_estimate','experimental':False,'written_into_native_table':False}
               for r in frame[frame.atomic_radius_slater_pm.isna()].itertuples()]
    radius={'method':'ordinary least squares: atomic_radius = slope*covalent_radius + intercept',
        'units':'pm','training_symbols':training.symbol.tolist(),'training_count':len(x),
        'slope':float(slope),'intercept_pm':float(intercept),'training_r2':float(1-np.sum((pred-y)**2)/np.sum((y-y.mean())**2)),
        'leave_one_element_out_mae_pm':float(np.mean(np.abs(loo))),
        'leave_one_element_out_rmse_pm':float(np.sqrt(np.mean(np.square(loo)))),
        'limits':'Cross-validation on observed elements does not establish error for missing/unstable elements; no prediction interval claimed.',
        'estimates':estimates,'fr_thermal_conductivity':'missing; legacy hardcoded 15.0 rejected as an unjustified project estimate'}
    release={'metadata':{'version':'2.0.0-audit','status':'scientific_evidence_review_incomplete',
         'purpose':'Legacy-preserving claim-level evidence review; not a newly certified benchmark',
         'admission_policy':'Only independently verified host/phase/site/concentration claims may earn quantitative credit.',
         'unknown_is_not_negative':True},'substitution_cases':[],'doping_cases':[]}
    for track,key in [('substitution','primary_cases'),('doping','secondary_doping_cases')]:
        for original in legacy_benchmark[key]:
            status,reason=REVIEW[original['case_id']];entry=doi_lookup.get(original['doi'],{'status':'not_queried'})
            candidates=original['known_substituents'] if track=='substitution' else [original['known_dopant']]
            claims=[]
            for candidate in candidates:
                claims.append({'claim_id':original['case_id']+':'+candidate,'candidate':candidate,
                    'label':'unknown','review_status':status,'review_reason':reason,
                    'eligible_for_quantitative_evaluation':False,'host_verified':False,'phase_verified':False,
                    'site_verified':False,'concentration_verified':False,'supporting_source_url':None,'source_locator':None,
                    'bibliographic_resolution':entry.get('status'),'resolved_titles':entry.get('titles',[]),
                    'legacy_doi':original['doi'],'registry_record_file':entry.get('local_file'),
                    'warning':'Citation status does not establish whether the chemical claim is true or false.'})
            release['substitution_cases' if track=='substitution' else 'doping_cases'].append({
                'case_id':original['case_id'],'track':track,'legacy_record':original,'claims':claims})
    benchmark_check=validate_benchmark(release)
    dictionary={feature:{'unit':unit,'description':description,'native_missing_policy':'Preserve missing source values; no implicit zero or project imputation'} for feature,(unit,description) in FEATURES.items()}
    metadata={'version':'2.0.0-audit','native_scope':'Z=1..94','registry_scope':'Z=1..118',
        'pn_convention':{'name':'Mendeleev library extended periodic-number ordering','source_field':'mendeleev_number',
            'full_library_range':[1,118],'retained_native_range':[int(frame.mendeleev_number.min()),int(frame.mendeleev_number.max())],
            'normalization':'PN/118, a derived convenience field unused by legacy engines',
            'source_citation_keys':'Pettifor1984,Villars2004; source metadata describes extension to all elements',
            'verification_limit':'Agreement with pinned library source established; full independent historical-scale reproduction not claimed'},
        'features':dictionary,'source_versions':snapshot['versions'],'captured_source_property_metadata':snapshot['property_metadata'],
        'source_urls':SOURCE_URLS,'quality_notes':['Source-provided does not mean experimentally measured.',
          'Upstream density estimates flagged separately from project imputation.',
          'Atomic volume ratio uses source density conditions; not uniformly condensed-solid molar volume.',
          'No new data supports element Z>94 feature vectors; registry recognition does not invent them.',
          'Legacy radius-imputed table and Fr value remain archived unchanged; new native table has genuine gaps.'],
        'validation':native_check,'benchmark_validation':benchmark_check}
    return {'elements':frame,'provenance':provenance,'registry':registry,'radius':radius,'metadata':metadata,'benchmark':release}

def write_release(bundle,data_dir,benchmark_dir,root):
    root=Path(root).resolve();data_dir=Path(data_dir).resolve();benchmark_dir=Path(benchmark_dir).resolve()
    for directory in (data_dir,benchmark_dir):
        require(directory!=root and directory.is_relative_to(root),'Release output must be a child of the project root')
        require(not directory.exists() or (directory.is_dir() and not any(directory.iterdir())),f'Refusing to replace existing release contents: {directory}')
    for directory in (data_dir,benchmark_dir):directory.mkdir(parents=True,exist_ok=True)
    def write(path,obj):
        with path.open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False)
    bundle['elements'].to_parquet(data_dir/'elements_native.parquet',index=False)
    with (data_dir/'cell_provenance.jsonl').open('x',encoding='utf-8') as f:
        for record in bundle['provenance']:f.write(json.dumps(record,ensure_ascii=False,allow_nan=False)+'\n')
    write(data_dir/'element_registry.json',bundle['registry'])
    write(data_dir/'radius_estimates.json',bundle['radius'])
    write(data_dir/'feature_metadata.json',bundle['metadata'])
    write(benchmark_dir/'benchmark_review.json',bundle['benchmark'])
    files=list(data_dir.iterdir())+list(benchmark_dir.iterdir())
    write(data_dir/'release_manifest.json',{'release':'2.0.0-audit','created_at_utc':datetime.now(timezone.utc).isoformat(),
        'files':{str(p.relative_to(root)):digest(p) for p in files},
        'activation':'Not wired into legacy engines. Stage 3 must choose an explicit missing-data/support policy.'})

def main():
    root=Path(__file__).resolve().parents[2]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-output',default='data/processed/v2_0_0')
    parser.add_argument('--benchmark-output',default='data/benchmark/v2_0_0')
    args=parser.parse_args()
    snapshot_path=root/'data/raw/stage_02_sources/source_snapshot.json'
    snapshot=load_json(snapshot_path)
    lookup=load_json(root/'data/raw/stage_02_sources/doi_lookup.json')
    legacy=load_json(root/'data/benchmark/benchmark_cases.json')
    with np.load(root/'data/processed/atom2vec_embeddings_d20.npz',allow_pickle=False) as cache:symbols=cache['common_symbols'].tolist()
    bundle=prepare_release(snapshot,lookup,legacy,symbols)
    bundle['metadata']['source_snapshot_sha256']=digest(snapshot_path)
    bundle['metadata']['legacy_master_sha256']=digest(root/'data/processed/elements_master.parquet')
    write_release(bundle,root/args.data_output,root/args.benchmark_output,root)
    print(json.dumps({'native':bundle['metadata']['validation'],'benchmark':bundle['metadata']['benchmark_validation'],
       'radius_fit':{k:bundle['radius'][k] for k in ('training_count','slope','intercept_pm','training_r2','leave_one_element_out_mae_pm')},
       'production_engines_changed':False},indent=2))

if __name__=='__main__':main()
