"""The article's analysis by setup, from ../data/runs_of_record.csv (written by collect_runs.py).

    PYTHONDONTWRITEBYTECODE=1 python setup_analysis.py > ../data/setup_analysis.txt

Every number in the article's results is printed here. Spread is over structures: median [first quartile, third
quartile], the count of structures that moved up or down by more than 0.2 dB, and the structure with the largest
value. Paired differences are taken on the same structure, law, stage and setting. Differences under 0.2 dB are
not claimed. Also writes the tables behind the figures and the article's tables into ../data/.

Needs NumPy and SciPy. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os
from collections import defaultdict

import numpy as np
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
LAWS = ['pinv_closed', 'pinv_open', 'buzz_match', 'min_drive', 'shape_svd', 'band_average']
STAGES = [('none', 'linear'), ('realistic', 'realistic'), ('strong', 'strong')]
NUM = ['control_band_rms', 'control_summed_rms', 'held_band_rms', 'held_summed_rms', 'level_mean_all', 'worst_band_over',
       'share_bands_over6', 'condition_median', 'stress_rms', 'stress_mean', 'stress_p95', 'stress_in3', 'tip_q10_mean',
       'control_mean', 'held_mean', 'declared_rms', 'law_error_rms']

rows = list(csv.DictReader(open(os.path.join(DATA, 'runs_of_record.csv'))))
for r in rows:
    for k in NUM:
        r[k] = float(r[k]) if r[k] != '' else None
    r['seed'] = int(r['seed'])
IDX = {(r['seed'], r['setup'], r['stage_variant'], r['law'], r['setting'], r['frf']): r for r in rows}


def get(seed, setup, variant, law, setting='default', frf='hold'):
    return IDX.get((seed, setup, variant, law, setting, frf))


def spread(x, seeds=None):
    x = np.asarray(x, float)
    q1, med, q3 = np.percentile(x, [25, 50, 75])
    s = f'{med:+.2f} [{q1:+.2f}, {q3:+.2f}], {int((x > 0.2).sum())} up, {int((x < -0.2).sum())} down of {x.size}'
    if seeds is not None:
        i = int(np.argmax(np.abs(x)))
        s += f'; largest structure {seeds[i]} ({x[i]:+.2f})'
    return s


def paired(a_key, b_key, laws, variant, seeds=None, setting_a='default', setting_b='default', frf_a='hold', frf_b='hold', writer=None, tag=''):
    """a minus b for the control-gauge band error, the held-out band error and the stress RMS error."""
    out = {}
    for law in laws:
        P = []
        for r in rows:
            if r['law'] != law or r['setup'] != a_key or r['stage_variant'] != variant or r['setting'] != setting_a or r['frf'] != frf_a:
                continue
            if seeds is not None and r['seed'] not in seeds:
                continue
            b = get(r['seed'], b_key, variant, law, setting_b, frf_b)
            if b:
                P.append((r['seed'], r, b))
        if not P:
            continue
        S = [p[0] for p in P]
        d = {m: [p[1][m] - p[2][m] for p in P] for m in ('control_band_rms', 'held_band_rms', 'stress_rms', 'stress_mean')}
        out[law] = (S, d)
        print(f'  {law:13s} control {spread(d["control_band_rms"], S)}')
        print(f'  {"":13s} held-out {spread(d["held_band_rms"], S)}')
        print(f'  {"":13s} stress RMS {spread(d["stress_rms"], S)}')
        print(f'  {"":13s} stress mean {spread(d["stress_mean"])}')
        if writer:
            for i, s in enumerate(S):
                writer.writerow(dict(comparison=tag, stage=variant, law=law, seed=s, a=a_key, b=b_key,
                                     control_change=f'{d["control_band_rms"][i]:.4f}', held_change=f'{d["held_band_rms"][i]:.4f}',
                                     stress_change=f'{d["stress_rms"][i]:.4f}', stress_mean_change=f'{d["stress_mean"][i]:.4f}'))
    return out


def sel(variant, same, law=None, setting='default', frf='hold'):
    return [r for r in rows if r['stage_variant'] == variant and int(r['same_count']) == same and r['setting'] == setting
            and r['frf'] == frf and (law is None or r['law'] == law)]


fp = open(os.path.join(DATA, 'paired_changes.csv'), 'w', newline='')
W = csv.DictWriter(fp, fieldnames=['comparison', 'stage', 'law', 'seed', 'a', 'b', 'control_change', 'held_change', 'stress_change', 'stress_mean_change'])
W.writeheader()

print('RESULTS OF RECORD')
for v, name in STAGES:
    n = [r for r in rows if r['stage_variant'] == v and r['setting'] == 'default' and r['frf'] == 'hold']
    print(f'  {name}, default settings, measured response kept: {len(n)} cases, checks widened {sum(r["checks"] == "widened" for r in n)}, '
          f'completed at default checks {sum(r["checks"] == "default" for r in n)}; structures {len({r["seed"] for r in n})}')

print('\nBASELINE: linear, default settings, by setup, median [quartiles] over structures, pooled over laws then by law')
base = open(os.path.join(DATA, 'by_setup_linear.csv'), 'w', newline='')
bw = csv.writer(base)
bw.writerow(['setup', 'law', 'runs', 'control_band_median', 'held_band_median', 'stress_rms_median', 'stress_mean_median', 'stress_rms_q1', 'stress_rms_q3'])
for setup in ('3x12', '6x12', '12x24', '6x6', '12x12'):
    for law in LAWS:
        R = [r for r in rows if r['setup'] == setup and r['stage_variant'] == 'none' and r['setting'] == 'default' and r['frf'] == 'hold' and r['law'] == law]
        c, h, s, m = (np.array([r[k] for r in R]) for k in ('control_band_rms', 'held_band_rms', 'stress_rms', 'stress_mean'))
        bw.writerow([setup, law, len(R), f'{np.median(c):.3f}', f'{np.median(h):.3f}', f'{np.median(s):.3f}', f'{np.median(m):.3f}',
                     f'{np.percentile(s, 25):.3f}', f'{np.percentile(s, 75):.3f}'])
        print(f'  {setup:6s} {law:13s} n {len(R):2d} control {np.median(c):5.2f} held-out {np.median(h):5.2f} stress RMS {np.median(s):5.2f} '
              f'[{np.percentile(s, 25):5.2f}, {np.percentile(s, 75):5.2f}] mean {np.median(m):+5.2f}')
base.close()

for v, name in STAGES:
    print(f'\nS1 ({name}). Six shakers: six control gauges minus twelve (6x6 minus 6x12), same structure and law, default settings')
    paired('6x6', '6x12', LAWS, v, writer=W, tag='S1_6')
    print(f'S1b ({name}). Twelve shakers: twelve control gauges minus twenty-four (12x12 minus 12x24)')
    paired('12x12', '12x24', LAWS, v, writer=W, tag='S1_12')

for v, name in STAGES:
    print(f'\nS1c ({name}), not one of the claims fixed in advance. The same twelve control gauges, twelve shakers minus six '
          f'(12x12 minus 6x12; the six shakers of 6x12 are the first six of 12x12 on every structure)')
    paired('12x12', '6x12', LAWS, v, writer=W, tag='S1c_12_vs_6_shakers')
    print(f'S1d ({name}). The same twelve control gauges, six shakers minus three (6x12 minus 3x12)')
    paired('6x12', '3x12', LAWS, v, writer=W, tag='S1d_6_vs_3_shakers')

for v, name in STAGES:
    print(f'\nS2 ({name}). Setup 6x6, tuned minus default, same structure and law (structures 0 to 9)')
    paired('6x6', '6x6', LAWS, v, setting_a='tuned', writer=W, tag='S2_6x6')
    print(f'S2 on 6x12 ({name}), for comparison')
    paired('6x12', '6x12', LAWS, v, setting_a='tuned', writer=W, tag='S2_6x12')

print('\nS3. Spearman rank correlation with stress RMS error over runs, default settings, six laws')
cw = open(os.path.join(DATA, 's3_correlations.csv'), 'w', newline='')
cwr = csv.writer(cw)
cwr.writerow(['stage', 'setups', 'runs', 'control_band', 'held_band', 'control_summed', 'held_summed', 'level_all', 'tip_q10_mean'])
for v, name in STAGES:
    for same, label in ((1, 'same count'), (0, 'more control gauges')):
        R = sel(v, same)
        s = [r['stress_rms'] for r in R]
        vals = [spearmanr([r[k] for r in R], s)[0] for k in ('control_band_rms', 'held_band_rms', 'control_summed_rms', 'held_summed_rms')]
        lv = spearmanr([abs(r['level_mean_all']) for r in R], s)[0]
        tp = spearmanr([abs(r['tip_q10_mean']) for r in R], s)[0]
        cwr.writerow([name, label, len(R)] + [f'{x:.3f}' for x in vals + [lv, tp]])
        print(f'  {name:9s} {label:20s} n {len(R)}: per-channel control {vals[0]:+.2f} held-out {vals[1]:+.2f}; summed control {vals[2]:+.2f} '
              f'held-out {vals[3]:+.2f}; |level, all gauges| {lv:+.2f}; |tip response spectrum mean| {tp:+.2f}')
cw.close()
print('  S3 within one law, linear, same count (per-channel control, held-out), n:')
for law in LAWS:
    R = sel('none', 1, law)
    s = [r['stress_rms'] for r in R]
    print(f'    {law:13s} n {len(R)} control {spearmanr([r["control_band_rms"] for r in R], s)[0]:+.2f} held-out {spearmanr([r["held_band_rms"] for r in R], s)[0]:+.2f}')
print('  S3 within one setup, linear, six laws pooled:')
for setup in ('6x6', '12x12', '3x12', '6x12', '12x24'):
    R = [r for r in sel('none', int(setup in ('6x6', '12x12'))) if r['setup'] == setup]
    s = [r['stress_rms'] for r in R]
    print(f'    {setup:6s} n {len(R)} control {spearmanr([r["control_band_rms"] for r in R], s)[0]:+.2f} held-out {spearmanr([r["held_band_rms"] for r in R], s)[0]:+.2f}')

print('\nS4. Report card lines as the scorer applies them, default settings')
for v, name in STAGES:
    for same, label in ((1, 'same count'), (0, 'more control gauges')):
        R = sel(v, same)
        n = len(R)
        print(f'  {name:9s} {label:20s} n {n}: exact-fit flag {sum(r["exact_fit_flag"] == "1" for r in R)}; '
              f'control pattern A or B {sum(r["control_grade"] in ("A", "B") for r in R)}; held-out pattern A or B {sum(r["held_grade"] in ("A", "B") for r in R)}; '
              f'level within 1.5 dB {sum(r["level_within"] == "1" for r in R)}; over-test alarm {sum(r["alarm"] == "1" for r in R)}; '
              f'stress within 3 dB RMS {sum(r["stress_rms"] <= 3 for r in R)}')
R = sel('none', 1)
cb = np.array([r['control_band_rms'] for r in R])
cs = np.array([r['control_summed_rms'] for r in R])
print(f'  linear, same count: per-channel control band error min {cb.min():.2f}, median {np.median(cb):.2f}; runs under 0.5 dB {(cb < 0.5).sum()}, '
      f'under 1 dB {(cb < 1).sum()}, under 2 dB {(cb < 2).sum()}, under 3 dB {(cb < 3).sum()} of {cb.size}; summed control error min {cs.min():.2f}, median {np.median(cs):.2f}')
low = [r for r in R if r['control_band_rms'] < 1]
for r in low:
    print(f'    flagged or under 1 dB: {r["run_id"]} control {r["control_band_rms"]:.2f} stress {r["stress_rms"]:.2f}')
A = [r for v, _ in STAGES for r in rows if r['stage_variant'] == v and r['setting'] == 'default' and r['frf'] == 'hold']
wb = np.array([r['worst_band_over'] for r in A])
print(f'  alarm over all stages and setups: {sum(r["alarm"] == "1" for r in A)} of {len(A)}; worst band over target min {wb.min():.1f} dB, median {np.median(wb):.1f}')
for same in (1, 0):
    R = sel('none', same)
    print(f'  linear same_count={same}: share of bands over +6 dB, median {np.median([r["share_bands_over6"] for r in R]) * 100:.1f} %; '
          f'runs with stress within 3 dB RMS that still alarm {sum(r["alarm"] == "1" and r["stress_rms"] <= 3 for r in R)} of {sum(r["stress_rms"] <= 3 for r in R)}')

print('\nMEASURED AGAIN DURING THE TEST minus MEASURED ONCE AND KEPT (structures 0 to 9, setups 6x6 and 6x12)')
for v, name in STAGES[1:]:
    for setup in ('6x6', '6x12'):
        print(f' {name}, {setup}')
        paired(setup, setup, LAWS, v, frf_a='update', writer=W, tag=f'update_{setup}')
fp.close()

print('\nWHICH MEASUREMENT WARNS: linear, default settings. Over-test = stress mean over elements more than +3 dB.')
signs = [('control pattern graded C or worse (summed control error > 4.5 dB)', lambda r: r['control_summed_rms'] > 4.5),
         ('held-out pattern graded C or worse (summed held-out error > 4.5 dB)', lambda r: r['held_summed_rms'] > 4.5),
         ('level line outside 1.5 dB (all gauges)', lambda r: abs(r['level_mean_all']) > 1.5),
         ('control gauges read more than 1.5 dB high on average', lambda r: r['control_mean'] > 1.5),
         ('held-out gauges read more than 1.5 dB high on average', lambda r: r['held_mean'] > 1.5),
         ('component tips, response spectrum Q 10, more than 1.5 dB high on average', lambda r: r['tip_q10_mean'] > 1.5),
         ('over-test alarm (any band of any gauge more than 6 dB over)', lambda r: r['alarm'] == '1')]
ww = open(os.path.join(DATA, 'warning_signs.csv'), 'w', newline='')
wwr = csv.writer(ww)
wwr.writerow(['setups', 'sign', 'over_tests_caught', 'over_tests', 'others_flagged', 'others'])
for same, label in ((1, 'same count'), (0, 'more control gauges')):
    R = sel('none', same)
    bad = [r for r in R if r['stress_mean'] > 3]
    ok = [r for r in R if r['stress_mean'] <= 3]
    print(f' {label}: {len(bad)} of {len(R)} runs over-test by more than 3 dB on average')
    for text, f in signs:
        a, b = sum(f(r) for r in bad), sum(f(r) for r in ok)
        wwr.writerow([label, text, a, len(bad), b, len(ok)])
        print(f'   {text}: catches {a} of {len(bad)}; also flags {b} of {len(ok)} others')
    for k in ('control_mean', 'held_mean', 'tip_q10_mean', 'level_mean_all'):
        print(f'   Spearman of signed {k} with signed stress mean: {spearmanr([r[k] for r in R], [r["stress_mean"] for r in R])[0]:+.2f}')
ww.close()

print('\nFIGURE DATA')
with open(os.path.join(DATA, 'fig_paired_setups.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['law', 'seed', 'setup', 'control_band_rms', 'held_band_rms', 'stress_rms', 'stress_mean'])
    for law in LAWS:
        for r in rows:
            if r['law'] == law and r['stage_variant'] == 'none' and r['setting'] == 'default' and r['frf'] == 'hold':
                if all(get(r['seed'], s, 'none', law) for s in ('3x12', '6x12', '12x12', '6x6')):
                    w.writerow([law, r['seed'], r['setup'], f'{r["control_band_rms"]:.4f}', f'{r["held_band_rms"]:.4f}', f'{r["stress_rms"]:.4f}', f'{r["stress_mean"]:.4f}'])
with open(os.path.join(DATA, 'fig_what_tracks.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['setup', 'same_count', 'law', 'seed', 'control_band_rms', 'held_band_rms', 'stress_rms'])
    for same in (1, 0):
        for r in sel('none', same):
            w.writerow([r['setup'], same, r['law'], r['seed'], f'{r["control_band_rms"]:.4f}', f'{r["held_band_rms"]:.4f}', f'{r["stress_rms"]:.4f}'])
print('  written')
