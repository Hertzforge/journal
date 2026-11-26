"""Write the CSV files in ../data from the study's own output files.

Usage: python make_data.py <study folder>

The study folder holds `experiments/study_tables_output.json` (the study's tables: every run's scores,
structure by structure), `experiments/claims_study_output.json` (the 136 claims written by rule before
the held-back structures were run) and `audit/a1_verdicts.json` and `audit/A1_Audit_2026-11-26.md`
(the independent audit: the verdict of each claim on the held-back structures, and the runs made with
the controller's checks at their defaults). Nothing here computes a claim or a verdict; it copies them.

All four are published in the study's scorecards record (DOI 10.5281/zenodo.24563639) under the same names;
the rows of the report's defaults table are those of the record's cards.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
SYSTEMS = {'frame-12x6': '6 x 12', 'frame-6x6': '6 x 6'}
HELD_BACK = ('20', '21', '22', '23', '26')


def write(name, header, rows):
    with open(os.path.join(DATA, name), 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(header)
        for r in rows:
            w.writerow([round(x, 4) if isinstance(x, float) else x for x in r])
    print(name, len(rows), 'rows')


def main(study):
    tables = json.load(open(os.path.join(study, 'experiments', 'study_tables_output.json')))
    claims = json.load(open(os.path.join(study, 'experiments', 'claims_study_output.json')))['claims']
    verdicts = json.load(open(os.path.join(study, 'audit', 'a1_verdicts.json')))

    # 1. Stress error RMS of every run, structure by structure (the primary yardstick).
    rows = []
    for cell, by_label in tables['primary']['table'].items():
        system, size = cell.split('/')
        for label, each in by_label.items():
            for s, v in each.items():
                rows.append([SYSTEMS[system], size, int(s), label, v])
    rows.sort(key=lambda r: (r[0], r[1], r[3], r[2]))
    write('stress_by_structure.csv', ['system', 'size', 'structure', 'run', 'stress_error_rms_db'], rows)

    # 2. Median and quartiles of each score, by system, size and run.
    keep = ('stress_rms', 'stress_mean', 'held_out', 'band_controls', 'q50_tip_over', 'drive_worst',
            'line_dbfit', 'slope15', 'exposure')
    rows = []
    for cell, by_label in tables['arms'].items():
        system, size = cell.split('/')
        for label, a in by_label.items():
            for y in keep:
                st = a['yardsticks'].get(y)
                if st and st.get('n'):
                    rows.append([SYSTEMS[system], size, label, y, st['n'], st['median'], st['q1'], st['q3']])
    write('scores_by_run.csv', ['system', 'size', 'run', 'score', 'structures', 'median', 'q1', 'q3'], rows)

    # 3. The 136 claims with the audit's verdicts (d = first run minus second, dB, stress error RMS).
    vkey = {(v['system'], v['tier'], v['a'], v['b'], v['kind']): v for v in verdicts}
    rows = []
    for c in claims:
        v = vkey[(c['system'], c['tier'], c['a'], c['b'], c['kind'])]
        lo, hi = c['quartiles_db'] if c['kind'] == 'difference' else c['interval_db']
        rows.append([SYSTEMS[c['system']], c['tier'], c['a'], c['b'], c['kind'].replace('_', ' '), c['n'],
                     c['median_db'], lo, hi, c.get('on_side', ''), c.get('on_other', ''), v['audit_median']]
                    + [v['audit_d'][s] for s in HELD_BACK] + [v['verdict']])
    write('claims.csv', ['system', 'size', 'first', 'second', 'kind', 'structures', 'study_median_db',
                         'study_low_db', 'study_high_db', 'on_its_side', 'on_the_other', 'held_back_median_db']
          + ['held_back_d_' + s for s in HELD_BACK] + ['verdict'], rows)

    # 4. The line yardstick on the strong size (expectation E7).
    rows = []
    for key, e in tables['expectations']['E7'].items():
        system, label = key.split('/')
        s = e['stress_minus_A1']
        rows.append([SYSTEMS[system], 'strong', label, e['line_rms']['median'], e['line_in3']['median'],
                     e['line_over6']['median'], s['median'], s['q1'], s['q3'], s['n_above'], s['n']])
    write('line_yardstick.csv', ['system', 'size', 'run', 'line_rms_db', 'share_lines_within_3_db',
                                 'share_lines_over_6_db', 'stress_minus_band_control_db', 'q1', 'q3',
                                 'structures_worse', 'structures'], rows)

    # 5. The runs at the controller's default checks (the audit's defaults table, copied as printed).
    rows = []
    with open(os.path.join(study, 'audit', 'A1_Audit_2026-11-26.md')) as f:
        inside = False
        for line in f:
            if line.startswith('## Defaults Table'):
                inside = True
                continue
            if inside and line.startswith('## '):
                break
            if inside and line.startswith('| frame-'):
                p = [x.strip() for x in line.strip().strip('|').split('|')]
                rows.append([SYSTEMS[p[0]], p[1], int(p[2]), p[3], p[4], p[5], int(p[6]), p[7], p[8]])
    write('default_checks.csv', ['system', 'size', 'structure', 'run', 'at_defaults', 'stopped_at_loop',
                                 'full_level_loops', 'stress_rms_at_defaults_db', 'stress_rms_widened_db'], rows)


if __name__ == '__main__':
    main(sys.argv[1])
