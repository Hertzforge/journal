"""The tuning runs of the three laws: every setting tried, on the eight tuning cases (structures 30
and 31, the 6 x 12 and 6 x 6 systems, the linear stage and the strong size of the level-dependent
one, checks widened). Writes ../data/tuning_points.csv from the scorecards. It runs nothing.

    PYTHONDONTWRITEBYTECODE=1 python3 tuning_results.py [--out NAME.csv] LAW[,LAW]=CARDS [LAW=CARDS ...]

Each argument names the laws to take from a folder of tuning scorecards. `--out` names the file
written (default tuning_points.csv); tuning_points_first_commit.csv is the independent drive law's
tuning on the first commit, where its default still had the weighting by the target (the setting
written `solve_weighting = none` there is the second commit's default). A row is one setting of
one law on one system: the mean over its four cases of the error at the held-out gauges, the error
at the control gauges and the stress error, the mean, the smallest and the largest level error of
the four, the mean of the size of the level error, and the largest over-test.

The rule that chooses the tuned setting, fixed before the tuning runs and the same as the earlier
study's: the lowest mean error at the held-out gauges; among the settings within 0.10 dB of it, the
one with the smallest mean size of the level error. The column `chosen` marks it.

Copyright 2026 Kevin Cross and Norman Hunter. MIT license.
"""
import csv
import glob
import json
import os
import sys
from collections import defaultdict

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
ORDER = ['independent', 'nearly_independent', 'broyden_congruence']
SYSTEMS = {'6x12': '6 x 12', '6x6': '6 x 6'}
TIE = 0.10


def label(params):
    if not params:
        return 'defaults'
    def text(v):
        return ('on' if v else 'off') if isinstance(v, bool) else str(v)
    return ', '.join(f'{k} = {text(v)}' for k, v in sorted(params.items()))


def main():
    acc = defaultdict(list)
    index = {}
    args, name = sys.argv[1:], 'tuning_points.csv'
    if args[:1] == ['--out']:
        name, args = args[1], args[2:]
    for a in args:
        if '=' not in a:
            sys.exit(__doc__)
        names, folder = a.split('=', 1)
        laws = names.split(',')
        files = sorted(glob.glob(os.path.join(folder, '*.json')))
        if not files:
            sys.exit(f'no scorecards in {folder}')
        for p in files:
            d = json.load(open(p))
            j = d['job']
            if j['law'] not in laws or j['rig'] not in SYSTEMS:
                continue
            if not (d['outcome']['completed'] and d.get('scored')):
                sys.exit(f'{os.path.basename(p)} is not scored: every tuning case must be')
            key = (j['law'], j['rig'], label(d['run']['law_parameters'] or {}))
            acc[key].append(d)
            index[key] = int(j['setting'][1:])        # the setting's place in the list that was tried
    if not acc:
        sys.exit(__doc__)
    rows = []
    for law in ORDER:
        for system in SYSTEMS:
            keys = sorted((k for k in acc if k[0] == law and k[1] == system), key=lambda k: index[k])
            if not keys:
                continue
            stat = {}
            for k in keys:
                ds = acc[k]
                if len(ds) != 4:
                    sys.exit(f'{k}: {len(ds)} cases, not 4')
                lv = [d['card']['level_mean'] for d in ds]
                stat[k] = dict(held=sum(d['card']['h_b3_rms'] for d in ds) / 4, control=sum(d['card']['c_b3_rms'] for d in ds) / 4,
                               stress=sum(d['stress']['rms'] for d in ds) / 4, mean=sum(lv) / 4, lo=min(lv), hi=max(lv),
                               size=sum(abs(x) for x in lv) / 4, over=max(d['card']['worst_over_b3'] for d in ds))
            best = min(s['held'] for s in stat.values())
            near = [k for k in keys if stat[k]['held'] <= best + TIE]
            chosen = min(near, key=lambda k: stat[k]['size'])
            for k in keys:
                s = stat[k]
                rows.append([law, SYSTEMS[system], k[2], 4, f"{s['held']:.2f}", f"{s['control']:.2f}", f"{s['mean']:+.2f}", f"{s['lo']:+.2f}", f"{s['hi']:+.2f}",
                             f"{s['size']:.2f}", f"{s['stress']:.2f}", f"{s['over']:.2f}", 'yes' if k == chosen else ''])
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['law', 'system', 'setting', 'cases', 'held_out_db', 'control_db', 'level_mean_db', 'level_min_db', 'level_max_db', 'level_size_db',
                    'stress_db', 'worst_over_test_db', 'chosen'])
        w.writerows(rows)
    print('wrote', name, len(rows), 'rows;', 'chosen:', '; '.join(f'{r[0]} {r[1]}: {r[2]}' for r in rows if r[-1]))


if __name__ == '__main__':
    main()
