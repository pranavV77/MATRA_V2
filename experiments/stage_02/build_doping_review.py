"""Create a conservative doping-source supplement, without prediction labels."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.data_audit.doping_review import validate_doping_review

RAW = ROOT / 'data/raw/stage_02_doping_sources'
PARENT = ROOT / 'data/benchmark/v2_2_0/extended_evidence.json'
OUTPUT = ROOT / 'data/benchmark/doping_review_v1_0_0'


def artifact(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def build_review():
    extraction = RAW / 'Mg_GaN_web_extraction.txt'
    lines = extraction.read_text(encoding='utf-8').splitlines()

    def quantity(kind, values, unit, relation, line_start, line_end, anchors, specimen='same_experiment'):
        first = next(i for i, line in enumerate(lines, 1) if line.startswith(f'L{line_start}@'))
        last = next(i for i, line in enumerate(lines, 1) if line.startswith(f'L{line_end}@'))
        return {'kind': kind, 'values': values, 'unit': unit, 'relation': relation,
                'specimen_relation': specimen, 'source_locator': {'line_start': first, 'line_end': last, 'anchors': anchors,
                                                               'paper_location': f'Publisher PDF extraction L{line_start}–L{line_end}'}}

    quantities = [
        quantity('stable_dopant_number_density', [2e19], 'cm^-3', '=', 110, 111, ['2 × 1019']),
        quantity('radioactive_probe_peak_density', [3e14], 'cm^-3', '<', 124, 128, ['below 3 × 1014']),
        quantity('implantation_fluence', [1.1e11], 'cm^-2', '=', 143, 147, ['total fluence 1.1 × 1011']),
        quantity('hole_number_density', [1e17, 2e17], 'cm^-3', 'range', 115, 118, ['no electrical char', '1–2 × 1017'], 'similar_specimens'),
        quantity('hall_mobility', [10, 15], 'cm^2 V^-1 s^-1', 'range', 115, 118, ['10–15 cm2=Vs'], 'similar_specimens'),
        quantity('interstitial_fit_fraction', [31], '%', '=', 161, 163, ['31% of Mg on interstitial sites']),
        quantity('c_axis_aligned_fit_fraction', [72], '%', '=', 161, 163, ['72% aligned with the c'])]
    leads = [
        {'element': 'Mg', 'host': 'GaN', 'related_legacy_case': 'BM-S03', 'doi': '10.1103/PhysRevLett.118.095501',
         'access': 'primary_text_partially_archived_via_web_tool', 'label': 'unknown', 'full_doping_benchmark_eligible': False,
         'limitations': 'Probe site observations are direct evidence; same study specimens were not electrically characterized. Probe density, stable Mg density and Hall results on similar specimens cannot be merged.'},
        {'element': 'Si', 'host': 'beta-Ga2O3', 'related_legacy_case': 'BM-S01', 'doi': '10.1063/1.3578195',
         'access': 'metadata_and_primary_abstract', 'label': 'unknown', 'full_doping_benchmark_eligible': False,
         'limitations': 'STM abstract supports a substitutional-donor lead; full methods, exact concentration and Ga-site assignment were not archived. Do not assign the octahedral site from similarity or a different dopant.'},
        {'element': 'Nb', 'host': 'SrTiO3', 'related_legacy_case': 'BM-S04', 'doi': '10.1021/nn401101y',
         'access': 'metadata_and_primary_abstract', 'label': 'unknown', 'full_doping_benchmark_eligible': False,
         'limitations': 'Primary abstract contrasts active bulk substitution with inactive interstitial-containing films; full sample concentrations and synthesis/context details still required. Not a universal negative Nb label.'}]
    return {'version': '1.0.0-doping-review', 'purpose': 'Doping evidence supplement; no new quantitative recommendation or activation benchmark admission',
            'parent_benchmark': PARENT.relative_to(ROOT).as_posix(),
            'artifacts': [artifact(PARENT)] + [artifact(p) for p in sorted(RAW.iterdir()) if p.is_file()],
            'leads': leads,
            'mg_site_study': {'source_doi': '10.1103/PhysRevLett.118.095501',
                              'source_url': 'https://harvest.aps.org/v2/journals/articles/10.1103/PhysRevLett.118.095501/fulltext',
                              'archive_format': 'web_tool_text_extraction_not_pdf',
                              'archive_coverage': 'Publisher extraction lines 0–396, pages 1–5 partially; references/end matter not completely archived. Direct download returned 401.',
                              'extraction_path': extraction.relative_to(ROOT).as_posix(),
                              'host_phase': 'Wurtzite single-crystal GaN epilayers, growth description in PDF page 2',
                              'experiment_scope': '27Mg probe implanted into stable-Mg-predoped GaN; Figure 2 uses 200 degrees C and 0.20 pA',
                              'same_specimen_electrical_measurement': False, 'activation_efficiency': None,
                              'fit_fractions_normalized': False, 'independence_group': 'GaN_family', 'held_out': False,
                              'quantities': quantities,
                              'limitations': ['72% aligned with c axis is not by itself a unique Ga-site assignment; off-axis patterns are required.',
                                              'Reported 31% and 72% fit values are retained; no normalization to 100% or fabricated uncertainties.',
                                              'No tracer-to-stable-Mg population transfer and no Hall activation efficiency inferred.',
                                              'Single technical reviewer; independent scientific adjudication pending.']}}


def main():
    review = build_review()
    result = validate_doping_review(review, ROOT)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    outputs = [(OUTPUT / 'doping_evidence.json', review), (ROOT / 'results/stage_02/run_004/review_counts.json', result)]
    if any(path.exists() for path, _ in outputs): raise FileExistsError('Outputs exist; use new version/run')
    for path, value in outputs:
        with path.open('x', encoding='utf-8') as stream: json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
    print(json.dumps(result))


if __name__ == '__main__': main()
