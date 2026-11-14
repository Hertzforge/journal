"""Rebuild every file in ../data from the studies' saved results.

Usage:
    python extract_data.py RESULTS_DIR

RESULTS_DIR may also be given in the environment variable MM_RESULTS. It must hold
the saved results of studies MM-X1 (x1/), MM-X2 (x2/), MM-X1c (x1c/) and MM-A1
(a1/variants_rv_bv_sv.pkl). Those results are not part of this bundle: this script
is the record of how the fig5 to fig11 data files were made from them.

The script reads pickles, so it needs numpy and scipy installed (the pickles hold
numpy arrays). It writes only small CSV files and checks each one against the
numbers printed in the study reports; a check that fails stops the script.

Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
import csv
import os
import pickle
import sys

import numpy as np
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')


def results_dir():
    if len(sys.argv) > 1:
        return sys.argv[1]
    if os.environ.get('MM_RESULTS'):
        return os.environ['MM_RESULTS']
    sys.exit('usage: python extract_data.py RESULTS_DIR  (the studies\' saved results; not in this bundle)')


def load(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


def write(name, header, rows):
    path = os.path.join(DATA, name)
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow([f'{v:.4f}' if isinstance(v, (float, np.floating)) else v for v in r])
    print(f'wrote data/{name} ({len(rows)} rows)')


def check(label, got, want, tol):
    ok = abs(got - want) <= tol
    print(f'  check {label}: {got:.3f} against report {want} ({"ok" if ok else "MISMATCH"})')
    if not ok:
        raise SystemExit(f'check failed: {label}')


def rig_class(ns, nc):
    if ns == nc:
        return 'equal'
    return 'more_shakers' if ns > nc else 'fewer_shakers'


def fig1(x1, x2):
    """Exact fit: control error against element stress error, by rig."""
    rows = []
    for r in x1:
        if r['test'] == 'LINE':
            rows.append(['random', r['seed'], r['pert'], r['ns'], r['nc'], rig_class(r['ns'], r['nc']),
                         float(r['c_b3_rms']), float(r['t_bias']), float(r['t_rms'])])
    for r in x2:
        if r['test'] == 'WAVEFORM':
            rows.append(['shock', r['seed'], r['pert'], r['ns'], r['nc'], rig_class(r['ns'], r['nc']),
                         float(r['c_srs12_rms']), float(r['t_bias']), float(r['t_rms'])])
    write('fig5_exact_fit.csv', ['study', 'seed', 'perturbation', 'shakers', 'controls', 'rig_class',
                                 'control_error_db', 'stress_bias_db', 'stress_rms_db'], rows)
    sq = [r for r in rows if r[0] == 'random' and r[5] == 'equal']
    check('random, equal counts, control 1/3-oct error (X1b CAP1000 0.09)', np.mean([r[6] for r in sq]), 0.09, 0.01)
    check('random, equal counts, stress bias (X1b CAP1000 +11.2)', np.mean([r[7] for r in sq]), 11.2, 0.05)
    m = [r for r in rows if r[0] == 'random' and r[5] == 'more_shakers' and r[2] == 1]
    check('random, 12 x 6, p = 1, stress bias (A1 +0.8)', np.mean([r[7] for r in m]), 0.76, 0.01)
    for ns in (6, 12):
        s = [r for r in rows if r[0] == 'shock' and r[3] == ns and r[4] == ns and r[2] == 1]
        want = {6: 9.32, 12: 7.97}[ns]
        check(f'shock, {ns} x {ns}, p = 1, peak stress bias (A1 variants)', np.mean([r[7] for r in s]), want, 0.01)


METRICS = [('line_rms', 'Line dB RMS'), ('b3_rms', '1/3-octave band dB RMS'),
           ('sum3_rms', 'Sum of autospectra, 1/3-octave'), ('ers10_rms', 'ERS Q = 10'),
           ('fds10_rms', 'FDS Q = 10, b = 8'), ('grms_rms', 'Overall RMS (grms)'),
           ('line_worst', 'Worst channel, line'), ('g527_rms', 'Annex C global error')]


def fig2(x1):
    """Rank correlation of each metric with element stress error, controls and held-out gauges."""
    lab = [r for r in x1 if r['test'] != 'S1']
    multi = [r for r in lab if not r['test'].startswith('SA')]
    groups = [('all_rigs', 'All multi-shaker cases', multi),
              ('unequal_counts', 'Shaker and control counts unequal', [r for r in multi if r['ns'] != r['nc']]),
              ('line_law_all_rigs', 'Line law only, all rigs', [r for r in lab if r['test'] == 'LINE'])]
    rows = []
    for gkey, glabel, rs in groups:
        y = [r['t_rms'] for r in rs]
        for mkey, mlabel in METRICS:
            for tag, gauge in (('c_', 'controls'), ('h_', 'held_out')):
                rho = spearmanr([r[tag + mkey] for r in rs], y)[0]
                rows.append([gkey, glabel, len(rs), mkey, mlabel, gauge, float(rho)])
    write('fig6_rank_correlation.csv', ['case_set', 'case_set_label', 'n_cases', 'metric', 'metric_label',
                                        'gauges', 'spearman_rho'], rows)
    look = {(r[0], r[3], r[5]): r[6] for r in rows}
    check('unequal counts, sum 1/3-oct, controls (A1-A3 0.81)', look[('unequal_counts', 'sum3_rms', 'controls')], 0.81, 0.005)
    check('unequal counts, sum 1/3-oct, held out (A1-A3 0.79)', look[('unequal_counts', 'sum3_rms', 'held_out')], 0.79, 0.005)
    check('line law, line dB RMS, controls (X1 -0.08)', look[('line_law_all_rigs', 'line_rms', 'controls')], -0.08, 0.005)
    check('line law, sum 1/3-oct, held out (X1 0.84)', look[('line_law_all_rigs', 'sum3_rms', 'held_out')], 0.84, 0.005)
    check('all multi-shaker, Annex C, held out (X1 0.43)', look[('all_rigs', 'g527_rms', 'held_out')], 0.43, 0.005)


def fig3(x1, x2):
    """The floor: a second unit in the same service environment.

    One row per seed and control set (6, 12 or 24 controls). The stress truth does not depend on
    the control set, so it repeats three times per seed, as in the study tables.
    """
    rows = []
    for r in x1:
        if r['test'] == 'S1' and r['pert'] in (1, 2):
            pct = 3 * r['pert']
            for q, v in (('control_line_rms', r['c_line_rms']), ('worst_control_line_rms', r['c_line_worst']),
                         ('control_band_third_octave_rms', r['c_b3_rms']), ('element_stress_rms', r['t_rms'])):
                rows.append(['random', pct, r['seed'], r['nc'], q, float(v)])
    for r in x2:
        if r['test'] == 'S1' and r['pert'] == 1:
            for q, v in (('control_srs_rms', r['c_srs12_rms']), ('element_peak_stress_rms', r['t_rms'])):
                rows.append(['shock', 3, r['seed'], r['nc'], q, float(v)])
    write('fig7_floor.csv', ['study', 'unit_scatter_percent', 'seed', 'controls', 'quantity', 'value_db'], rows)

    def mean(st, pct, q):
        return np.mean([r[5] for r in rows if r[0] == st and r[1] == pct and r[4] == q])
    check('3 %, control line RMS (X1 1.89)', mean('random', 3, 'control_line_rms'), 1.89, 0.005)
    check('3 %, worst control (X1 2.66)', mean('random', 3, 'worst_control_line_rms'), 2.66, 0.005)
    check('3 %, control 1/3-oct (X1 1.49)', mean('random', 3, 'control_band_third_octave_rms'), 1.49, 0.005)
    check('3 %, stress (X1 0.92)', mean('random', 3, 'element_stress_rms'), 0.92, 0.005)
    check('6 %, control line RMS (X1 3.53)', mean('random', 6, 'control_line_rms'), 3.53, 0.005)
    check('6 %, stress (X1 2.15)', mean('random', 6, 'element_stress_rms'), 2.15, 0.005)
    check('shock 3 %, control SRS (X2 0.78)', mean('shock', 3, 'control_srs_rms'), 0.78, 0.005)
    check('shock 3 %, peak stress (X2 0.75)', mean('shock', 3, 'element_peak_stress_rms'), 0.75, 0.005)


SA_ORDER = [('envelope', 'Envelope of the four mounts', 'ENV (study)', 'ENV max over mounts (study)'),
            ('mean', 'Mean of the four mounts', 'MEAN over mounts', 'MEAN over mounts'),
            ('true_one_axis', 'True mount-averaged motion, one axis at a time',
             'TRUE B, per axis, sequential', 'TRUE B, per axis, sequential'),
            ('true_three_axes', 'True motion, three axes at once',
             'TRUE B, 3 axes at once (rigid 3-DOF table)', 'TRUE B, 3 axes at once'),
            ('all_twelve', 'All twelve mount translations as in service',
             'EXACT B, all 12 mount dofs prescribed', 'EXACT B, 12 mount dofs prescribed')]


def fig4(variants):
    """Where the single-axis over-test comes from (audit A1-A1)."""
    rows = []
    for study, key, col in (('random', 'rv', 2), ('shock', 'sv', 3)):
        for rec in variants[key]:
            for item in SA_ORDER:
                s = rec['sa'][item[col]]
                rows.append([study, rec['seed'], item[0], item[1], float(s['t_rms']), float(s['t_bias']), float(s['t_p5'])])
    write('fig8_single_axis_decomposition.csv', ['study', 'seed', 'base_input', 'base_input_label',
                                                 'stress_rms_db', 'stress_bias_db', 'stress_p5_db'], rows)

    def mean(st, b, i):
        return np.mean([r[i] for r in rows if r[0] == st and r[2] == b])
    check('random envelope bias (A1 +9.41)', mean('random', 'envelope', 5), 9.41, 0.005)
    check('random true one axis bias (A1 -3.64)', mean('random', 'true_one_axis', 5), -3.64, 0.005)
    check('random all twelve RMS (A1 0.46)', mean('random', 'all_twelve', 4), 0.46, 0.005)
    check('shock envelope bias (A1 +5.38)', mean('shock', 'envelope', 5), 5.38, 0.005)
    check('shock true one axis p5 (A1 -11.41)', mean('shock', 'true_one_axis', 6), -11.41, 0.005)


def fig5(x1c):
    """Line law against the band law fitted in decibels: paired result, and the first shot."""
    idx = {(r['law'], r['model'], r['seed'], r['ns'], r['nc']): r for r in x1c}
    rows = []
    for (law, model, seed, ns, nc), r in sorted(idx.items()):
        if law == 'BANDLOG3' and model == 'true':
            ln = idx[('LINE', 'true', seed, ns, nc)]
            rows.append([seed, ns, nc, rig_class(ns, nc), float(ln['t_rms']), float(r['t_rms']),
                         float(r['t_rms'] - ln['t_rms'])])
    write('fig9a_line_vs_band_paired.csv', ['seed', 'shakers', 'controls', 'rig_class', 'line_stress_rms_db',
                                            'band_log_stress_rms_db', 'band_minus_line_db'], rows)
    nonsq = [r for r in rows if r[3] != 'equal']
    check('non-square paired change (X1c -0.47)', np.mean([r[6] for r in nonsq]), -0.47, 0.005)
    check('non-square share better (X1c 64 %)', 100 * np.mean([r[6] < 0 for r in nonsq]), 64, 0.5)
    check('3 x 24 paired change (X1c -1.80)', np.mean([r[6] for r in rows if (r[1], r[2]) == (3, 24)]), -1.80, 0.005)

    rows = []
    for law in ('LINE', 'BAND3', 'BANDLOG3'):
        for model in ('true', 'K+1%', 'K+3%', 'zeta/2'):
            for sq, cls in ((False, 'unequal'), (True, 'equal')):
                rs = [r for r in x1c if r['law'] == law and r['model'] == model and r['square'] == sq]
                v = [float(r['c_over_b3']) for r in rs]
                rows.append([law, model, cls, len(rs), float(np.mean(v)), float(np.max(v)),
                             float(np.mean([r['t_rms'] for r in rs]))])
    write('fig9b_first_shot.csv', ['law', 'model', 'counts', 'n_cases', 'worst_control_band_over_mean_db',
                                   'worst_control_band_over_max_db', 'stress_rms_mean_db'], rows)
    look = {(r[0], r[1], r[2]): r for r in rows}
    check('LINE +3 % non-square worst band (X1c 22.7)', look[('LINE', 'K+3%', 'unequal')][4], 22.7, 0.05)
    check('BANDLOG3 +1 % non-square worst band (X1c 12.9)', look[('BANDLOG3', 'K+1%', 'unequal')][4], 12.9, 0.05)
    check('BANDLOG3 +3 % square worst band (X1c 11.4)', look[('BANDLOG3', 'K+3%', 'equal')][4], 11.4, 0.05)
    check('LINE +3 % non-square worst case (X1c 33.9)', look[('LINE', 'K+3%', 'unequal')][5], 33.9, 0.05)


def fig6(x2):
    """Shock: spread of element peak stress among shots that match one spectrum."""
    syn = [r for r in x2 if r['test'] == 'SYNTH']
    cases = sorted({(r['seed'], r['pert'], r['ns'], r['nc']) for r in syn})
    rows = []
    for cs in cases:
        rs = [r for r in syn if (r['seed'], r['pert'], r['ns'], r['nc']) == cs]
        X = np.array([r['x'] for r in rs])
        sd = X.std(0)
        rows.append([cs[0], cs[1], cs[2], cs[3], len(rs), float(np.mean([r['c_srs12_rms'] for r in rs])),
                     float(np.median(sd)), float(np.percentile(sd, 90)), float(np.median(np.ptp(X, 0)))])
    write('fig10_shock_same_spectrum_spread.csv', ['seed', 'perturbation', 'shakers', 'controls', 'n_shots',
                                                  'control_srs_rms_mean_db', 'element_peak_stress_sd_median_db',
                                                  'element_peak_stress_sd_p90_db', 'element_peak_stress_range_median_db'], rows)
    for (ns, nc), sd, rng in (((6, 6), 1.69, 6.4), ((6, 12), 1.38, 5.4), ((3, 24), 1.39, 5.3)):
        a = [r for r in rows if (r[2], r[3]) == (ns, nc)]
        check(f'{ns} x {nc} per-element SD (X2 {sd})', np.mean([r[6] for r in a]), sd, 0.005)
        check(f'{ns} x {nc} per-element range (X2 {rng})', np.mean([r[8] for r in a]), rng, 0.05)


def fig7(x1c):
    """The coverage margin: rule P against the margin that truly covers 95 percent of elements."""
    rows = []
    for r in x1c:
        if r['model'] == 'true' and r['law'] in ('LINE', 'BANDLOG3'):
            x = r['x'].astype(float)
            truth = -np.percentile(x, 5)
            rule_p = -3 - np.percentile(r['h_E3'].ravel(), 10)
            rows.append([r['law'], r['seed'], r['ns'], r['nc'], rig_class(r['ns'], r['nc']),
                         float(rule_p), float(truth), float(rule_p - truth)])
    write('fig11_coverage_margin.csv', ['law', 'seed', 'shakers', 'controls', 'rig_class',
                                       'rule_p_margin_db', 'truth_cover95_margin_db', 'rule_minus_truth_db'], rows)
    for law, p, t, med in (('LINE', 5.37, 5.29, 2.08), ('BANDLOG3', 4.34, 5.15, 1.77)):
        a = [r for r in rows if r[0] == law and r[4] != 'equal']
        check(f'{law} non-square rule P margin (X1c {p})', np.mean([r[5] for r in a]), p, 0.005)
        check(f'{law} non-square truth margin (X1c {t})', np.mean([r[6] for r in a]), t, 0.005)
        check(f'{law} non-square per-test miss median (X1c {med})', np.median([abs(r[7]) for r in a]), med, 0.005)


def main():
    root = results_dir()
    print(f'reading saved results from {root}')
    x1 = load(os.path.join(root, 'x1', 'x1_results.pkl'))[0]
    x2 = load(os.path.join(root, 'x2', 'x2_results.pkl'))[0]
    x1c = load(os.path.join(root, 'x1c', 'x1c_results.pkl'))
    variants = load(os.path.join(root, 'a1', 'variants_rv_bv_sv.pkl'))
    os.makedirs(DATA, exist_ok=True)
    fig1(x1, x2)
    fig2(x1)
    fig3(x1, x2)
    fig4(variants)
    fig5(x1c)
    fig6(x2)
    fig7(x1c)
    print('all data files rebuilt; every check matched its report')


if __name__ == '__main__':
    main()
