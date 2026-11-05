"""Additive evidence review and site-occupancy bookkeeping, not structure prediction."""
from collections import Counter
from pathlib import Path
import hashlib
import math
import re

from .primary_evidence import validate_primary_evidence
from .validation import load_json, require


def weighted_site_composition(sites):
    """Sum multiplicity * occupancy; return counts and fractions on listed sites.

    These are crystallographic-model counts, not independent chemical analysis.
    No uncertainties are propagated without the refinement covariance matrix.
    """
    require(isinstance(sites, list) and bool(sites), 'Site table required')
    require(all(isinstance(s, dict) and isinstance(s.get('site'), str) and s['site'] for s in sites), 'Sites require identifiers')
    require(len({s['site'] for s in sites}) == len(sites), 'Duplicate sites')
    totals = Counter()
    total_multiplicity = 0
    for site in sites:
        multiplicity = site.get('multiplicity')
        require(type(multiplicity) is int and multiplicity > 0, 'Multiplicity must be a positive integer')
        occupancies = site.get('occupancies')
        require(isinstance(occupancies, dict) and bool(occupancies), 'Occupancies required')
        from pymatgen.core import Element
        require(all(isinstance(k, str) and Element.is_valid_symbol(k) for k in occupancies), 'Invalid occupancy element')
        require(all(type(v) in (int, float) and math.isfinite(v) and 0 <= v <= 1 for v in occupancies.values()), 'Invalid occupancy fraction')
        require(math.isclose(sum(occupancies.values()), 1, rel_tol=0, abs_tol=1e-6), 'Site occupancies must sum to one')
        total_multiplicity += multiplicity
        for element, value in occupancies.items():
            totals[element] += multiplicity * value
    return {'listed_site_count': total_multiplicity, 'counts': dict(totals),
            'fractions_on_listed_sites': {element: value / total_multiplicity for element, value in totals.items()},
            'origin': 'derived_from_reported_refinement_model', 'uncertainty_propagated': False}


def _artifact(record, root):
    require(isinstance(record, dict), 'Artifact object required')
    require(isinstance(record.get('path'), str) and record['path'], 'Artifact path required')
    path = (root / record['path']).resolve()
    require(path.is_relative_to(root) and path.is_file(), 'Artifact missing or outside project')
    require(hashlib.sha256(path.read_bytes()).hexdigest() == record.get('sha256'), 'Artifact checksum mismatch')
    return path


def validate_extended_review(release, root):
    """Keep the frozen v2.1 admission policy; add development-only evidence notes."""
    root = Path(root).resolve()
    require(isinstance(release, dict) and release.get('version') == '2.2.0', 'Expected extension version 2.2.0')
    parent = load_json(_artifact(release.get('parent_release'), root))
    legacy = load_json(_artifact(release.get('legacy_release'), root))
    # v2.1.0 remains unchanged. Projection reuses its full contextual policy.
    counts = validate_primary_evidence({'version': '2.1.0', 'sources': release.get('sources'),
                                        'reviewed_claims': release.get('reviewed_claims')}, root)
    claims = release['reviewed_claims']
    by_id = {claim['claim_id']: claim for claim in claims}
    for old in parent['reviewed_claims']:
        require(old['claim_id'] in by_id, 'Inherited claim removed')
        require({k: by_id[old['claim_id']].get(k) for k in old} == old, 'Inherited scientific decision changed')
    for claim in claims:
        require(isinstance(claim.get('independence_group'), str) and claim['independence_group'], 'Host-family group required')
        require(claim.get('split_role') == 'development_reference_only' and claim.get('held_out') is False, 'Curated development cases cannot be called held-out tests')
    expected = {(case['case_id'], claim['candidate']): (case['track'], case['legacy_record']['target_element'])
                for group in ('substitution_cases', 'doping_cases') for case in legacy[group] for claim in case['claims']}
    family = {case['case_id']: case['legacy_record']['formula'] + '_family'
              for group in ('substitution_cases', 'doping_cases') for case in legacy[group]}
    for claim in claims:
        key = (claim.get('related_legacy_case'), claim['candidate'])
        require(key in expected and (claim['track'], claim['target']) == expected[key], 'Scoped claim does not match legacy identity')
        require(claim['independence_group'] == family[claim['related_legacy_case']], 'Host-family grouping mismatch')
    decisions = release.get('legacy_decisions')
    require(isinstance(decisions, list), 'Legacy decisions required')
    require(len(decisions) == len(expected) and len({(d['case_id'], d['candidate']) for d in decisions}) == len(expected), 'Legacy decisions must cover each original assertion exactly once')
    for decision in decisions:
        key = (decision['case_id'], decision['candidate'])
        require(key in expected, 'Invented legacy assertion')
        require((decision.get('track'), decision.get('target')) == expected[key], 'Legacy identity or track mismatch')
        require(decision.get('status') == 'withheld' and decision.get('label') == 'unknown', 'Broad legacy assertions remain unvalidated')
        require(decision.get('reason') and decision.get('next_evidence_needed'), 'Hold reason and action required')
        for cid in decision.get('related_scoped_claims', []):
            require(cid in by_id, 'Unknown related claim')
            related = by_id[cid]
            require(related['related_legacy_case'] == decision['case_id'] and related['candidate'] == decision['candidate'] and related['target'] == decision['target'], 'Narrow claim linked to wrong assertion')
    source_by_id = {s['source_id']: s for s in release['sources']}
    observations = release.get('unscored_observations')
    require(isinstance(observations, list) and bool(observations), 'Unscored observations required')
    require(all(isinstance(o, dict) and o.get('observation_id') for o in observations), 'Observation IDs required')
    require(len({o['observation_id'] for o in observations}) == len(observations), 'Duplicate observation IDs')
    for observation in observations:
        require(observation.get('eligible_for_quantitative_evaluation') is False, 'Unscored observation cannot earn credit')
        require(observation.get('property_preservation_validated') is False, 'No property-preservation validation')
        require(observation.get('limitations') and observation.get('scope') and observation.get('kind'), 'Observation scope and limitations required')
        require(observation['kind'] in ('site_preference', 'electrical_activation_caution', 'source_internal_inconsistency'), 'Unknown observation kind')
        if observation['kind'] == 'electrical_activation_caution':
            for field, unit in (('reported_sn_number_density', 'atoms cm^-3'), ('resistivity_bound', 'ohm cm'), ('carrier_density_bound', 'cm^-3')):
                quantity = observation.get(field)
                require(isinstance(quantity, dict), 'Observed quantity required')
                value = quantity.get('value')
                require(type(value) in (int, float) and math.isfinite(value) and value > 0 and quantity.get('unit') == unit, 'Invalid observed value or unit')
            require(observation['resistivity_bound'].get('relation') == '>' and observation['carrier_density_bound'].get('relation') == '<=', 'Detection-limit relation changed')
            require(observation['carrier_density_bound'].get('assumption'), 'Conditional bound requires its assumption')
            require('activation_efficiency' not in observation, 'Detection bounds are not an activation-efficiency point estimate')
        source = source_by_id.get(observation.get('source_id'))
        require(source is not None and source['access'] == 'full_text', 'Observation needs reviewed full text')
        lines = (root / source['text']['path']).read_text(encoding='utf-8').splitlines()
        passages = observation.get('passages')
        require(isinstance(passages, list) and bool(passages), 'Observation passages required')
        for passage in passages:
            start, end = passage.get('line_start'), passage.get('line_end')
            require(type(start) is int and type(end) is int and 1 <= start <= end <= len(lines), 'Invalid observation locator')
            anchors = passage.get('anchors')
            require(isinstance(anchors, list) and bool(anchors), 'Observation anchors required')
            selected = '\n'.join(lines[start-1:end])
            require(all(isinstance(a, str) and a and a in selected for a in anchors), 'Observation anchor absent')
    occupancy = release.get('site_occupancy_check')
    require(isinstance(occupancy, dict), 'Occupancy check required')
    recomputed = weighted_site_composition(occupancy.get('sites'))
    require(recomputed == occupancy.get('derived'), 'Occupancy derivation mismatch')
    require(occupancy.get('source_id') in source_by_id and occupancy.get('source_locator'), 'Occupancy source required')
    source = source_by_id[occupancy['source_id']]
    source_lines = (root / source['text']['path']).read_text(encoding='utf-8').splitlines()
    for site in occupancy['sites']:
        rows = site.get('source_rows', {})
        require(isinstance(rows, dict), 'Occupancy source rows must be an object')
        require(set(rows) == set(site['occupancies']), 'Every occupancy needs a source-table row')
        for element, row in rows.items():
            require(isinstance(row, str) and row in source_lines, 'Occupancy source row absent')
            cells = row.split()
            require(len(cells) >= 3 and cells[0].startswith(element), 'Occupancy species mismatch')
            multiplicity_match = re.match(r'\d+', cells[1])
            require(cells[1] == site['site'] and multiplicity_match is not None and int(multiplicity_match.group()) == site['multiplicity'], 'Wyckoff multiplicity mismatch')
            value = float(cells[2].split('(')[0])
            require(value == site['occupancies'][element], 'Occupancy differs from source table')
    counts.update(legacy_assertions_reviewed=len(decisions), unscored_observations=len(observations),
                  eligible_substitution=sum(c['eligible'] and c['track'] == 'substitution' for c in claims),
                  eligible_doping=sum(c['eligible'] and c['track'] == 'doping' for c in claims),
                  eligible_host_family_groups=len({c['independence_group'] for c in claims if c['eligible']}),
                  held_out_cases=0)
    return counts
