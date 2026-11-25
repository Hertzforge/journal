"""Write the small files of ../data that the suite article's figures and numbers read. NumPy only.
Copyright 2026 Kevin Cross. MIT license.

    python suite_results.py RECORD PROBLEMS AUDIT_PROBLEMS

RECORD is the results record of the MIMO Shock suite study and its audit (its `experiments`
folder: the per-run tables of the study and the audit, and the effective-duration reruns). PROBLEMS and AUDIT_PROBLEMS are the suite's problem folders
(draft 0.2) and the held-back problem folders. Every figure is pooled over the five laws of the
companion article; no law is named here. It runs nothing and imports no study or scorer code.
"""
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
G = 9.80665
TARGETS = ('srs', 'half_sine', 'sawtooth')
READINGS = ('strict', 'ends', 'ends_pm3', 'level', 'exposure')
EXAMPLE = 'frame-6x6-realistic_s00'


def read_csv(path):
    with open(path, newline='') as file:
        return list(csv.DictReader(file))


def write_csv(name, header, table):
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, name), 'w', newline='') as file:
        out = csv.writer(file, lineterminator='\n')
        out.writerow(header)
        out.writerows(table)
    print('wrote', name, len(table), 'rows')


def truth(value):
    return value == 'True'


def r4(x):
    return '' if x is None or (isinstance(x, float) and not np.isfinite(x)) else round(float(x), 4)


def problems(folder, which):
    table = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name, 'problem.json')
        if not os.path.exists(path):
            continue
        p = json.load(open(path))
        s = p['structure']
        cls = f"{s['controls']}x{s['drives']}"
        tier = s['variant'] if s['variant'] else 'none'
        row = [which, name, cls, tier, s['seed'], s['modes'], r4(p['checks']['highest_reachable_hz'])]
        for t in TARGETS:
            c = p['checks']['by_target'][t]
            st = c.get('state_at_full_level') or {}
            soft = (st.get('change_softening_p10_p50_p90') or [None] * 3)[1]
            hard = (st.get('change_hardening_p10_p50_p90') or [None] * 3)[1]
            dev = json.load(open(os.path.join(folder, name, f'target_{t}.json')))['declared_deviation_db']
            err = c['ideal_drive_full_level_srs_error_db']
            row += [r4(p['targets'][t]['peak_g']), r4(st.get('peak_ratio_p50')), r4(soft), r4(hard),
                    r4(st.get('largest_drop')), r4(st.get('largest_rise')), r4(dev['rms']),
                    r4(dev['min']), r4(dev['max']), r4(err[0]), r4(err[1]),
                    'True' if c['finite_at_full_and_6db_over'] else 'False']
        table.append(row)
    return table


def example_targets(folder):
    """The three full-level waveforms at control 1 of the example problem, and its SRS target."""
    base = os.path.join(folder, EXAMPLE)
    p = json.load(open(os.path.join(base, 'problem.json')))
    n = p['grid']['n']
    fs = p['grid']['fs_hz']
    waves = {}
    for t in TARGETS:
        ref = json.load(open(os.path.join(base, f'target_{t}.json')))['reference']
        x = np.fromfile(os.path.join(base, ref['file']), '<f8').reshape(ref['shape'])
        assert x.shape[1] == n
        waves[t] = x[0] / G
    time = np.arange(n) / fs
    keep = (time >= 0.55) & (time <= 1.0)
    write_csv('example_waveforms.csv', ['time_s', 'srs_g', 'half_sine_g', 'sawtooth_g'],
              [[round(time[i], 6), r4(waves['srs'][i]), r4(waves['half_sine'][i]),
                r4(waves['sawtooth'][i])] for i in np.flatnonzero(keep)])
    target = json.load(open(os.path.join(base, 'target_srs.json')))
    write_csv('example_srs_target.csv', ['natural_hz', 'target_g'],
              [[r4(f), r4(a / G)] for f, a in zip(target['natural_hz'], target['points'][0])])


def pooled(runs, which):
    """Shares pooled over laws, per cell and per target; the best single law's share beside it."""
    table = []
    cells = sorted({(r['cls'], r['tier']) for r in runs})
    groups = [(c, t, 'all') for c, t in cells] + [('all', 'all', k) for k in ('all',) + TARGETS]
    for cls, tier, kind in groups:
        g = [r for r in runs if (cls == 'all' or r['cls'] == cls) and (tier == 'all' or r['tier'] == tier)
             and (kind == 'all' or r['kind'] == kind)]
        laws = sorted({r['law'] for r in g})
        row = [which, cls, tier, kind, len(g), len(laws)]
        for key in READINGS:
            row.append(r4(np.mean([truth(r[key]) for r in g])))
        row.append(r4(np.mean([r['end'] == 'completed' for r in g])))
        for key in ('ends', 'exposure'):
            per_law = [np.mean([truth(r[key]) for r in g if r['law'] == law]) for law in laws]
            row += [r4(max(per_law)), r4(min(per_law))]
        row.append(r4(np.median([float(r['seconds']) for r in g])))
        table.append(row)
    return table


def te_definition(old_runs, new_runs, which):
    """On SRS targets, the runs with a last full-level pulse: effective duration within 0.8 to 1.2
    on every control by the earlier 10 % threshold and by Method 516.8 Annex A (peak over 3)."""
    old = {(r['problem'], r['law']): r for r in old_runs if r['kind'] == 'srs'}
    table = []
    for group in ('none', 'realistic', 'strong', 'one effect', 'all'):
        n = old_ok = new_ok = 0
        for r in new_runs:
            if r['kind'] != 'srs' or r['te_ratio'] == '':
                continue
            tier = r['tier']
            in_group = (group == 'all' or tier == group
                        or (group == 'one effect' and tier.endswith(('_soft', '_hard'))))
            if not in_group:
                continue
            o = old[(r['problem'], r['law'])]
            assert o['te_share'] != '', (r['problem'], r['law'])
            n += 1
            old_ok += float(o['te_share']) == 1.0
            new_ok += truth(r['te'])
        table.append([which, group, n, r4(old_ok / n), r4(new_ok / n)])
    return table


def classical_time(runs, which):
    """Classical targets, runs with a last full-level pulse: every control inside Method 516.8's
    time-domain tolerance (peak band, duration, velocity, compensation, sawtooth post-slope), on
    the square systems and on the systems with more control gauges than shakers."""
    table = []
    for group in ('square', 'more gauges'):
        for kind in ('half_sine', 'sawtooth'):
            g = [r for r in runs if r['kind'] == kind and r['classical_516'] != ''
                 and (r['cls'] in ('6x6', '12x12')) == (group == 'square')]
            table.append([which, group, kind, len(g),
                          r4(np.mean([float(r['classical_516']) == 1.0 for r in g])),
                          r4(np.mean([float(r['classical_516']) for r in g]))])
    return table


def main(record, folder, audit_folder):
    head = ['set', 'problem', 'cls', 'tier', 'structure', 'modes', 'highest_reachable_hz']
    for t in TARGETS:
        head += [f'{t}_{k}' for k in ('peak_g', 'peak_ratio_p50', 'soft_p50', 'hard_p50', 'largest_drop',
                                       'largest_rise', 'dev_rms_db', 'dev_min_db', 'dev_max_db',
                                       'ideal_err_min_db', 'ideal_err_max_db', 'finite')]
    write_csv('problems.csv', head, problems(folder, 'study') + problems(audit_folder, 'audit'))
    example_targets(folder)
    study = read_csv(os.path.join(record, 'study_v02_rust', 'study_v02_rust_runs.csv'))
    audit = read_csv(os.path.join(record, 'audit_rust', 'audit_rust_runs.csv'))
    head = ['set', 'cls', 'tier', 'kind', 'runs', 'laws'] + list(READINGS) + [
        'completed', 'ends_best_law', 'ends_worst_law', 'exposure_best_law', 'exposure_worst_law',
        'seconds_median']
    write_csv('pooled_cells.csv', head, pooled(study, 'study') + pooled(audit, 'audit'))
    te_study = read_csv(os.path.join(record, 'study_v02_te', 'study_v02_te_runs.csv'))
    te_audit = read_csv(os.path.join(record, 'audit_te', 'audit_te_runs.csv'))
    write_csv('te_definition.csv', ['set', 'tier', 'runs_at_full_level', 'te_ok_10pct', 'te_ok_516'],
              te_definition(study, te_study, 'study') + te_definition(audit, te_audit, 'audit'))
    write_csv('classical_time.csv', ['set', 'systems', 'kind', 'runs_at_full_level', 'all_controls_inside',
                                     'mean_share_of_controls'],
              classical_time(study, 'study') + classical_time(audit, 'audit'))
    conclusions = json.load(open(os.path.join(record, 'study_v02_rust', 'conclusions_tables.json')))
    safety = []
    for which, name in (('study', 'study_v02_rust'), ('audit', 'audit_rust')):
        tables = [law['all/all'] for law in conclusions[name].values()]
        safety.append([which, sum(t['runs'] for t in tables)] + [
            sum(t[k] for t in tables) for k in ('over_3db', 'over_3db_at_or_above_minus3', 'over_6db',
                                               'over_6db_at_or_above_minus3')])
    write_csv('pooled_safety.csv', ['set', 'runs', 'over_3db', 'over_3db_at_or_near_full', 'over_6db',
                                    'over_6db_at_or_near_full'], safety)
    sign = json.load(open(os.path.join(record, 'audit_rust', 'audit_vs_study.json')))
    te_sign = json.load(open(os.path.join(record, 'study_v02_te', 'te_tables.json')))['audit_sign']
    write_csv('audit_sign.csv', ['what', 'value'],
              [['run score, law pairs per cell, same sign', sign['same_sign']],
               ['run score, decided at the study size, same sign', sign['decided_same_sign']],
               ['effective-duration share, law pairs per cell, same sign', te_sign['same_sign']]])


if __name__ == '__main__':
    main(*sys.argv[1:4])
