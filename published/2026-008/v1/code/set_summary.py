"""Facts about the whole staged set that the article quotes: how many problems, which seeds, how far the member
moves in service from seed to seed, the control levels, and the checks every folder carries.

    python set_summary.py PROBLEMS_ROOT

Reads problem.json and structure.json of every folder PROBLEMS_ROOT/frame-*_s<seed> (the release's problems/ folder).
The seeds are taken from the folder names; seeds 30 and 31 are the tuning seeds, every other seed a study seed. Writes ../data/set_summary.csv
(key, value). Needs NumPy only. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
TUNING = {30, 31}
G0 = 9.80665


def main(root):
    rows = []
    for d in sorted(glob.glob(os.path.join(root, 'frame-*_s*'))):
        m = re.match(r'frame-(\d+)x(\d+)(?:-(\w+))?_s(\d+)$', os.path.basename(d))
        if not m or not os.path.exists(os.path.join(d, 'problem.json')):
            continue
        pm = json.load(open(os.path.join(d, 'problem.json')))
        rows.append(dict(dir=d, controls=int(m.group(1)), drives=int(m.group(2)), variant=m.group(3) or 'linear',
                         seed=int(m.group(4)), pm=pm))
    study = [r for r in rows if r['seed'] not in TUNING]
    seeds = sorted({r['seed'] for r in study})
    out = dict(folders=len(rows), study_folders=len(study), study_seeds=len(seeds),
               study_seed_list=' '.join(str(s) for s in seeds),
               replacement_seeds=' '.join(str(s) for s in seeds if s >= 20) or 'none',
               rigs=len({(r['controls'], r['drives']) for r in rows}),
               variants=' '.join(sorted({r['variant'] for r in rows})))
    ch = {}
    for tier in ('realistic', 'strong'):
        v = [r['pm']['service_state']['member']['frequency_change'] for r in study
             if r['variant'] == tier and r['controls'] == 12 and r['drives'] == 6]
        ch[tier] = np.array(v)
        if v:
            out[f'service_member_{tier}_min_pct'] = 100 * min(v)
            out[f'service_member_{tier}_median_pct'] = 100 * float(np.median(v))
            out[f'service_member_{tier}_max_pct'] = 100 * max(v)
    g = []
    for r in study:
        if r['variant'] == 'linear' and r['controls'] == 12 and r['drives'] == 6:
            a = r['pm']['scoring']['service_a_psd']
            psd = np.fromfile(os.path.join(r['dir'], a['file']), a['dtype']).reshape(a['shape'])[:12]
            g.append(float(np.median(np.sqrt(psd.sum(1) * r['pm']['grid']['df_hz']) / G0)))
    if g:
        out.update(control_g_rms_median_min=min(g), control_g_rms_median_max=max(g), control_g_rms_median_median=float(np.median(g)))
    neg, lvl = 0, 0
    par, spar, smed, sp95, smax, fmax = [], [], [], [], [], []
    for r in rows:
        ck = r['pm']['provenance']['checks']
        par.append(ck['frf_parity']['value'])
        spar.append(ck['stress_frf_parity']['value'])
        if 'equalized_step_residual' in ck:
            e = ck['equalized_step_residual']
            smed.append(e['db_median']); sp95.append(e['db_p95']); smax.append(e['db_max'])
        if r['pm']['stage'] == 2:
            lvl += 1
            st = json.load(open(os.path.join(r['dir'], 'structure.json')))
            rise = np.array([mm['level']['rise'] for mm in st['modes']])
            k = int(np.argmax(rise))
            if rise[k] > 0 and st['level_targets']['frequency_change'][k] < 0:
                neg += 1
            f0 = np.array([mm['f_hz'] for mm in st['modes']])
            lv = st['modes']
            fmax.append(float(np.max(f0 * (1 + np.array([x['level']['rise'] * x['level']['rise_cap'] ** x['level']['rise_exponent'] for x in lv])))))
    out.update(level_folders=lvl, member_target_net_negative=neg, frf_parity_max=max(par), stress_parity_max=max(spar),
               step_residual_median_max=max(smed) if smed else float('nan'), step_residual_p95_min=min(sp95) if sp95 else float('nan'),
               step_residual_p95_max=max(sp95) if sp95 else float('nan'), step_residual_max_max=max(smax) if smax else float('nan'),
               highest_reachable_hz=max(fmax) if fmax else float('nan'),
               runner_case_equal_all=all(r['pm']['provenance']['checks'].get('runner_structure_equal', False) for r in rows))
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, 'set_summary.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['key', 'value'])
        for k, v in out.items():
            w.writerow([k, v])
    for k, v in out.items():
        print(f'{k}: {v}')


if __name__ == '__main__':
    main(sys.argv[1])
