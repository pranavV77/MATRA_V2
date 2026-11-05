"""Stateless structure-lab orchestration shared by CLI and local HTTP demo."""
from copy import deepcopy
import json
from src.similarity_validation import PROJECT_ROOT
from src.structures.hosts import analyze_sites, diagonal_supercell, parse_cif, structure_fingerprint, load_cif
from src.structures.candidates import CandidateGenerator, export_configurations
from src.structures.prototypes import PROTOTYPES, prototype

SOURCED_HOST = {'id': 'aflow_zns', 'name': 'AFLOW wurtzite ZnS CIF', 'formula': 'ZnS',
               'evidence_class': 'database_prototype_geometry', 'expected_spacegroup': 186,
               'source_url': 'https://aflow.org/p/AB_hP4_186_b_b-001/',
               'note': 'Original AFLOW CIF; database prototype geometry, not independently refined or a substitution benchmark.'}


class StructureService:
    def __init__(self, fusion=None, export_dir=None):
        self.generator = CandidateGenerator(fusion)
        self.export_dir = export_dir

    def catalog(self):
        return {'hosts': [{'id': key, **deepcopy(value)} for key,value in PROTOTYPES.items()]+[deepcopy(SOURCED_HOST)],
                'scope': 'Ordered, fully periodic CIF or idealized demonstration prototype; no relaxation or property prediction',
                'maximum_sites': 256, 'supercell_factor_range': [1,4]}

    def _host(self, payload, extra=()):
        if not isinstance(payload,dict): raise ValueError('Request must be an object')
        allowed = {'host_id','cif_text','supercell','symprec'} | set(extra)
        if set(payload)-allowed: raise ValueError('Unrecognized structure request fields')
        if ('host_id' in payload) == ('cif_text' in payload):
            raise ValueError('Provide exactly one of host_id or cif_text')
        if 'host_id' in payload:
            if payload['host_id'] == 'aflow_zns':
                host, provenance = load_cif('data/raw/stage_05_hosts/aflow_wurtzite_ZnS.cif')
                if provenance['file_sha256'] != '9750d42d4842270bf7a18d08c66304b5d84676fd4e6d6fa9797fb93c9f5fba3b':
                    raise ValueError('AFLOW host differs from the frozen acquisition hash')
                acquisition = json.loads((PROJECT_ROOT/'data/raw/stage_05_hosts/acquisition.json').read_text())
                provenance.update(deepcopy(SOURCED_HOST))
                provenance['acquisition'] = acquisition
            else:
                host = prototype(payload['host_id'])
                provenance = {'host_id': payload['host_id'], **deepcopy(PROTOTYPES[payload['host_id']])}
        else:
            host, provenance = parse_cif(payload['cif_text'])
            provenance['evidence_class'] = 'user_supplied_unverified_CIF'
            provenance['note'] = 'Input geometry parsed; external source identity and experimental validity not independently verified.'
        provenance['input_geometry_sha256'] = structure_fingerprint(host)
        return host,provenance

    def analyze(self, payload):
        host, provenance = self._host(payload)
        expanded = diagonal_supercell(host,payload.get('supercell',[1,1,1]))
        return {'provenance': provenance, 'analysis': analyze_sites(expanded,symprec=payload.get('symprec',0.01)),
                'supercell': payload.get('supercell',[1,1,1])}

    def generate(self, payload):
        keys = ('target','site_index','k','mode','candidate_symbols','candidate_oxidation_states')
        host, provenance = self._host(payload, keys)
        if 'target' not in payload or 'site_index' not in payload:
            raise ValueError('target and site_index are required')
        result = self.generator.generate(host,**{k:v for k,v in payload.items() if k in keys or k in ('supercell','symprec')})
        result['provenance'] = provenance
        return result

    def export(self, payload):
        # Recompute from validated inputs; never trust client-supplied trial geometries/scores.
        return export_configurations(self.generate(payload),self.export_dir)
