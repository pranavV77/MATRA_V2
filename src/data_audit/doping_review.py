"""Validate doping evidence identity and quantities, not doping predictions."""
from pathlib import Path
import hashlib
import math

from .validation import load_json, require

UNITS = {
    'stable_dopant_number_density': 'cm^-3',
    'radioactive_probe_peak_density': 'cm^-3',
    'implantation_fluence': 'cm^-2',
    'hole_number_density': 'cm^-3',
    'hall_mobility': 'cm^2 V^-1 s^-1',
    'interstitial_fit_fraction': '%',
    'c_axis_aligned_fit_fraction': '%',
}


def validate_quantity(quantity):
    """Preserve bounds/ranges and specimen identity; never silently convert units."""
    require(isinstance(quantity, dict), 'Quantity object required')
    kind = quantity.get('kind')
    require(kind in UNITS and quantity.get('unit') == UNITS[kind], 'Quantity kind/unit mismatch')
    require(quantity.get('specimen_relation') in ('same_experiment', 'similar_specimens'), 'Specimen identity required')
    require(quantity.get('relation') in ('=', '<', 'range'), 'Quantity relation required')
    values = quantity.get('values')
    require(isinstance(values, list) and len(values) == (2 if quantity['relation'] == 'range' else 1), 'Invalid quantity values')
    require(all(type(v) in (int, float) and math.isfinite(v) and v >= 0 for v in values), 'Quantity must be finite, nonnegative and not boolean')
    if quantity['relation'] == 'range': require(values[0] <= values[1], 'Reversed quantity range')
    if kind.endswith('fit_fraction'): require(all(v <= 100 for v in values), 'Fit fraction outside percent bounds')
    require(quantity.get('source_locator'), 'Quantity source locator required')


def validate_doping_review(review, root):
    root = Path(root).resolve()
    require(isinstance(review, dict) and review.get('version') == '1.0.0-doping-review', 'Wrong review version')
    artifacts = review.get('artifacts')
    require(isinstance(artifacts, list) and bool(artifacts), 'Evidence artifacts required')
    for artifact in artifacts:
        require(isinstance(artifact, dict) and isinstance(artifact.get('path'), str), 'Artifact path required')
        path = (root / artifact['path']).resolve()
        require(path.is_relative_to(root) and path.is_file(), 'Artifact missing or outside project')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == artifact.get('sha256'), 'Evidence checksum mismatch')
    parent = review.get('parent_benchmark')
    require(isinstance(parent, str) and any(a['path'] == parent for a in artifacts), 'Parent benchmark must be hash-protected')
    parent_data = load_json(root / parent)
    require(parent_data.get('version') == '2.2.0', 'Unexpected parent benchmark')
    leads = review.get('leads')
    require(isinstance(leads, list) and len(leads) == 3, 'Retain all three doping leads')
    require({lead.get('element') for lead in leads} == {'Si', 'Mg', 'Nb'}, 'Doping lead identity mismatch')
    for lead in leads:
        require(lead.get('full_doping_benchmark_eligible') is False, 'This review admits no full-context activation case')
        require(lead.get('label') == 'unknown' and lead.get('limitations'), 'Unverified role cannot receive success/failure label')
    mg = review.get('mg_site_study')
    require(isinstance(mg, dict) and mg.get('source_doi') == '10.1103/PhysRevLett.118.095501', 'Mg source identity mismatch')
    require(mg.get('archive_format') == 'web_tool_text_extraction_not_pdf', 'Archive format must be honest')
    require(mg.get('same_specimen_electrical_measurement') is False, 'Source reports no electrical characterization on study specimens')
    require(mg.get('activation_efficiency') is None, 'Activation efficiency unavailable')
    require(mg.get('fit_fractions_normalized') is False, 'Reported fitted fractions must not be renormalized')
    require(mg.get('held_out') is False and mg.get('independence_group') == 'GaN_family', 'Development-only host grouping required')
    artifact_path = mg.get('extraction_path')
    require(any(a['path'] == artifact_path for a in artifacts), 'Text extraction must be hash-protected')
    lines = (root / artifact_path).read_text(encoding='utf-8').splitlines()
    quantities = mg.get('quantities')
    require(isinstance(quantities, list) and len(quantities) == len(UNITS) and {q.get('kind') for q in quantities} == set(UNITS), 'Require distinct complete quantity identities')
    for quantity in quantities:
        validate_quantity(quantity)
        locator = quantity['source_locator']
        require(isinstance(locator, dict) and type(locator.get('line_start')) is int and type(locator.get('line_end')) is int, 'Invalid source line types')
        start, end = locator['line_start'], locator['line_end']
        require(1 <= start <= end <= len(lines), 'Source line range invalid')
        anchors = locator.get('anchors')
        require(isinstance(anchors, list) and bool(anchors), 'Quantity anchors required')
        selected = '\n'.join(lines[start-1:end])
        require(all(isinstance(a, str) and a and a in selected for a in anchors), 'Quantity passage absent')
        expected_relation = 'similar_specimens' if quantity['kind'] in ('hole_number_density', 'hall_mobility') else 'same_experiment'
        require(quantity['specimen_relation'] == expected_relation, 'Source specimen relationship changed')
    return {'leads_reviewed': 3, 'quantities_distinguished': len(quantities),
            'new_full_doping_cases': 0, 'new_held_out_cases': 0,
            'same_specimen_activation_measured': False}
