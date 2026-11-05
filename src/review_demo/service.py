"""Review-demo orchestration; source references never influence ranking scores."""
from datetime import datetime, timezone
from pathlib import Path
import csv
import json
import uuid

from pymatgen.core import Element
from src.fusion.fusion_engine import FusionEngine
from src.similarity_validation import PROJECT_ROOT

EXAMPLES = [
    {'label': 'Gallium oxide', 'host_formula': 'Ga2O3', 'target_element': 'Ga'},
    {'label': 'Molybdenum disulfide', 'host_formula': 'MoS2', 'target_element': 'Mo'},
    {'label': 'Bismuth telluride', 'host_formula': 'Bi2Te3', 'target_element': 'Te'},
    {'label': 'Gallium nitride', 'host_formula': 'GaN', 'target_element': 'Ga'},
    {'label': 'Strontium titanate', 'host_formula': 'SrTiO3', 'target_element': 'Ti'},
]


class DemoService:
    def __init__(self, engine=None, export_dir=None):
        self.engine = engine or FusionEngine()
        self.export_dir = Path(export_dir or PROJECT_ROOT / 'results/review_demo/exports').resolve()
        if not self.export_dir.is_relative_to(PROJECT_ROOT): raise ValueError('Exports must remain inside the project')
        self.reference = json.loads((PROJECT_ROOT / 'data/benchmark/v2_2_0/extended_evidence.json').read_text(encoding='utf-8'))
        self.sources = {s['source_id']: s for s in self.reference['sources']}
        legacy = json.loads((PROJECT_ROOT / 'data/benchmark/v2_0_0/benchmark_review.json').read_text(encoding='utf-8'))
        self.parent_formulas = {c['case_id']: c['legacy_record']['formula'] for group in ('substitution_cases','doping_cases') for c in legacy[group]}

    def status(self):
        atom = self.engine.engines['Atom2Vec']
        return {'version': 'review-0.1', 'common_pool_size': len(self.engine.common_candidates),
                'supported_targets': [{'symbol': s, 'name': Element(s).long_name} for s in self.engine.common_targets],
                'recognized_elements': 118, 'default_method': 'weighted_score', 'examples': EXAMPLES,
                'atom2vec_metadata_present': atom.cache_info.get('metadata_present', False),
                'atom2vec_corpus_verified': atom.cache_info.get('corpus_verified', False),
                'audited_development_references': sum(c['eligible'] for c in self.reference['reviewed_claims']),
                'held_out_cases': 0, 'scope': 'Element-level similarity screening; host membership only. Structural/property validation pending.'}

    def recommend(self, payload):
        if not isinstance(payload, dict): raise ValueError('Request must be a JSON object')
        allowed = {'target_element', 'host_formula', 'k', 'weights', 'fusion_method', 'rrf_k'}
        if set(payload)-allowed: raise ValueError('Unrecognized request fields')
        if 'target_element' not in payload: raise ValueError('target_element is required')
        result = self.engine.recommend(**payload)
        result['target_name'] = Element(result['target_element']).long_name
        candidates = {r['candidate_element'] for r in result['rankings']}
        for row in result['rankings']: row['candidate_name'] = Element(row['candidate_element']).long_name
        context_formula = result['host_context'].get('reduced_formula')
        # Annotation is after scoring. There is no evidence bonus or reference-label input.
        result['reference_notes'] = [
            {'candidate_element': c['candidate'], 'evidence_class': c['evidence_class'], 'scope': c['scope'],
             'source_url': self.sources[c['source_id']]['url'], 'claim_id': c['claim_id'],
             'reference_parent_formula': self.parent_formulas[c['related_legacy_case']],
             'requested_parent_formula_matches': context_formula == self.parent_formulas[c['related_legacy_case']] if context_formula else None,
             'current_request_validated': False, 'note': 'A scoped development reference, not validation of this request or property preservation.'}
            for c in self.reference['reviewed_claims'] if c['eligible'] and c['target'] == result['target_element'] and c['candidate'] in candidates]
        return result

    def evaluation(self):
        path = PROJECT_ROOT / 'results/stage_04/run_001/evaluation.json'
        if not path.is_file(): return {'available': False, 'note': 'Evaluation not run yet'}
        data = json.loads(path.read_text(encoding='utf-8'))
        return {'available': True, **{key: data[key] for key in ('scope', 'candidate_pool_size', 'held_out_cases', 'summary', 'reference_cases', 'ablations', 'limitations')},
                'timings': {method: {key: value for key,value in record.items() if key != 'raw_ms'} for method,record in data['timings'].items()}}

    def export(self, payload):
        result = self.recommend(payload)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        basename = 'recommendation_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ_') + uuid.uuid4().hex[:10]
        json_path, csv_path = self.export_dir / (basename+'.json'), self.export_dir / (basename+'.csv')
        archive = {'exported_at_utc': datetime.now(timezone.utc).isoformat(), 'demo_version': 'review-0.1', 'request': payload, 'result': result}
        with json_path.open('x', encoding='utf-8') as stream: json.dump(archive, stream, indent=2, ensure_ascii=False, allow_nan=False)
        with csv_path.open('x', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['rank','candidate','fusion_score','PN','Atom2Vec','Property','PN_contribution','Atom2Vec_contribution','Property_contribution','scope'])
            for row in result['rankings']:
                writer.writerow([row['rank'],row['candidate_element'],row['fusion_score'],*[row['method_scores'][m] for m in ('PN','Atom2Vec','Property')],
                                 *[row['contributions'][m] for m in ('PN','Atom2Vec','Property')],result['scope']])
        return {'saved': True, 'json_path': str(json_path), 'csv_path': str(csv_path), 'note': 'Saved inside the project, not the browser Downloads directory.'}
