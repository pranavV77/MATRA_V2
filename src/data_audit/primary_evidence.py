"""Validate locally reviewed evidence, without inferring chemistry from text.

The validator checks provenance and admission policy. Human scientific review
is still required: matching a passage cannot prove its interpretation correct.
"""
from pathlib import Path
import hashlib
import math

from .validation import DataValidationError, require


CONDITIONS = ('host', 'phase', 'site', 'concentration')


def validate_primary_evidence(release, root):
    """Return counts after validating files, passage locators and scoped gates."""
    root = Path(root).resolve()
    require(isinstance(release, dict), 'Evidence release must be an object')
    require(release.get('version') == '2.1.0', 'Unsupported evidence version')
    sources = release.get('sources')
    claims = release.get('reviewed_claims')
    require(isinstance(sources, list) and bool(sources), 'Sources required')
    require(isinstance(claims, list) and bool(claims), 'Reviewed claims required')
    require(all(isinstance(s, dict) and isinstance(s.get('source_id'), str) and s['source_id'] for s in sources), 'Source objects require IDs')
    require(all(isinstance(c, dict) and isinstance(c.get('claim_id'), str) and c['claim_id'] for c in claims), 'Claim objects require IDs')
    require(len({s['source_id'] for s in sources}) == len(sources), 'Duplicate source IDs')
    require(len({c['claim_id'] for c in claims}) == len(claims), 'Duplicate claim IDs')
    lookup = {s['source_id']: s for s in sources}
    texts = {}
    for source in sources:
        require(isinstance(source.get('url'), str) and source['url'].startswith('https://'), 'HTTPS source URL required')
        require(source.get('access') in ('full_text', 'acquired_unreviewed', 'metadata_only', 'blocked', 'unavailable'), 'Invalid access category')
        if source['access'] != 'full_text':
            continue
        require(source.get('identity_verified') is True, 'Full-text identity must be reviewed')
        require(isinstance(source.get('verified_doi'), str) and source['verified_doi'].startswith('10.'), 'Verified DOI required')
        for key in ('text', 'document'):
            artifact = source.get(key)
            require(isinstance(artifact, dict), 'Full text requires document and extraction')
            require(isinstance(artifact.get('path'), str) and artifact['path'], 'Artifact path required')
            path = (root / artifact.get('path', '')).resolve()
            require(path.is_relative_to(root), 'Source path escapes project')
            require(path.is_file(), 'Source artifact missing')
            require(hashlib.sha256(path.read_bytes()).hexdigest() == artifact.get('sha256'), 'Source checksum mismatch')
        text = (root / source['text']['path']).read_text(encoding='utf-8')
        require(len(text) > 1000, 'Full text cannot be an abstract or short error page')
        require(not any(x in text[:1500].lower() for x in ('client challenge', 'checking your browser', 'recaptcha')), 'Challenge is not paper text')
        texts[source['source_id']] = text.splitlines()
    counts = {'reviewed_claims': len(claims), 'eligible_experimental': 0, 'eligible_computational': 0, 'held': 0}
    for claim in claims:
        require(claim.get('track') in ('substitution', 'doping'), 'Invalid track')
        from pymatgen.core import Element
        require(all(isinstance(claim.get(k), str) and Element.is_valid_symbol(claim[k]) for k in ('target', 'candidate')), 'Invalid element identity')
        require(claim['target'] != claim['candidate'], 'Self-substitution is not a recommendation')
        require(claim.get('evidence_class') in ('experimental', 'computational'), 'Evidence class required')
        require(claim.get('label') in ('documented_positive', 'unknown', 'conflicting', 'documented_negative'), 'Invalid label')
        require(type(claim.get('eligible')) is bool, 'Eligibility must be boolean')
        require(claim.get('source_id') in lookup, 'Unknown source reference')
        require(claim.get('scope') and claim.get('limitations'), 'Scope and limitations required')
        conditions = claim.get('conditions', {})
        require(isinstance(conditions, dict), 'Conditions must be an object')
        require(set(conditions) == set(CONDITIONS), 'Require all contextual conditions')
        for condition in conditions.values():
            require(isinstance(condition, dict), 'Condition must be an object')
            require(condition.get('status') in ('verified', 'unverified'), 'Explicit condition status required')
            require(condition.get('description'), 'Condition description required')
            if condition['status'] == 'verified':
                lines = texts.get(claim['source_id'])
                require(lines is not None, 'Metadata or inaccessible source cannot verify conditions')
                start, end = condition.get('line_start'), condition.get('line_end')
                require(type(start) is int and type(end) is int and 1 <= start <= end <= len(lines), 'Invalid source line range')
                selected = '\n'.join(lines[start-1:end])
                anchors = condition.get('anchors')
                require(isinstance(anchors, list) and bool(anchors), 'Passage anchors required')
                require(all(isinstance(a, str) and a and a in selected for a in anchors), 'Passage anchor absent')
        concentration = claim.get('reported_concentration', {})
        require(isinstance(concentration, dict), 'Concentration must be an object')
        value = concentration.get('value')
        require(type(value) in (int, float) and math.isfinite(value) and value > 0, 'Invalid concentration')
        require(concentration.get('unit') and concentration.get('basis') and concentration.get('kind') in ('nominal', 'observed', 'model'), 'Concentration convention required')
        require(concentration['unit'] in ('fraction', 'at% as reported', 'wt%'), 'Unknown concentration unit')
        require(value <= (1 if concentration['unit'] == 'fraction' else 100), 'Concentration outside unit bounds')
        # Version 2.1 intentionally has no labels for preserved properties.
        require(claim.get('property_preservation_validated') is False, 'No property-preservation evidence curated in this release')
        if claim['eligible']:
            require(claim['label'] in ('documented_positive', 'documented_negative'), 'Unknown cannot earn credit')
            require(all(c['status'] == 'verified' for c in conditions.values()), 'Context incomplete')
            counts['eligible_' + claim['evidence_class']] += 1
        else:
            counts['held'] += 1
    return counts
