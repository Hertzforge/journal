"""Read each classical target against Method 516.8's time-domain tolerance, as the suite's scorer
reads a pulse, with the target itself as the pulse: does the full-level reference of a problem
meet the tolerance it is judged by? Writes ../data/target_self_check.csv. Copyright 2026 Kevin
Cross. MIT license.

    python target_self_check.py SUITE_CODE PROBLEMS AUDIT_PROBLEMS

SUITE_CODE is the suite's `shock` folder (draft 0.2); its harness's `classical_band` is the
reading every run's classical pulse is scored by. This script imports it and nothing else.
"""
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')


def main(code, folder, audit_folder):
    sys.path.insert(0, os.path.abspath(code))
    import harness
    table = []
    for which, root in (('study', folder), ('audit', audit_folder)):
        for name in sorted(os.listdir(root)):
            p = json.load(open(os.path.join(root, name, 'problem.json')))
            s = p['structure']
            for kind in ('half_sine', 'sawtooth'):
                tg = json.load(open(os.path.join(root, name, f'target_{kind}.json')))
                ref = np.fromfile(os.path.join(root, name, tg['reference']['file']),
                                  '<f8').reshape(tg['reference']['shape'])
                c = harness.classical_band(ref, ref, tg, 1.0)
                post = max(c['post_slope_pct']) if 'post_slope_pct' in c else ''
                table.append([which, name, f"{s['controls']}x{s['drives']}", s['variant'] or 'none', kind,
                              round(max(c['compensation_pct']), 2), post])
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, 'target_self_check.csv'), 'w', newline='') as file:
        out = csv.writer(file, lineterminator='\n')
        out.writerow(['set', 'problem', 'cls', 'tier', 'kind', 'compensation_max_pct', 'post_slope_max_pct'])
        out.writerows(table)
    print('wrote target_self_check.csv', len(table), 'rows')


if __name__ == '__main__':
    main(*sys.argv[1:4])
