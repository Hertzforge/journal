"""Write the small files of ../data that the controls article's figures and numbers read. NumPy only.
Copyright 2026 Kevin Cross. MIT license.

    python law_results.py RECORD STUDY_RUNS AUDIT_RUNS

RECORD is the results record of the MIMO Shock suite study and its audit (its `experiments`
folder). STUDY_RUNS and AUDIT_RUNS are the folders of run files the record's tables were made
from (one JSON a run; for followed and followed-hold the runs of the Rust law math, for the
other three the runs of their ports); they are read only for the classical pulses' time-domain
criteria, which the record's tables give as one combined share. It runs nothing and imports no
study or scorer code.
"""
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
LAWS = ['followed', 'followed-hold', 'inverse', 'shape', 'paired']
SETS = {'study': ('study_v02_rust', 'study_v02_te'), 'audit': ('audit_rust', 'audit_te')}


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


def r4(x):
    return '' if x is None or (isinstance(x, float) and not np.isfinite(x)) else round(float(x), 4)


def main(record, study_runs, audit_runs):
    conclusions = json.load(open(os.path.join(record, 'study_v02_rust', 'conclusions_tables.json')))
    te = json.load(open(os.path.join(record, 'study_v02_te', 'te_tables.json')))
    te_all = {'study': te['study_v02_te']['all_targets_ends_with_te'],
              'audit': te['audit_te']['all_targets_ends_with_te']}
    readings, cells, targets, safety, misses, te_srs = [], [], [], [], [], []
    for which, (name, te_name) in SETS.items():
        rd = read_csv(os.path.join(record, name, f'{name}_readings.csv'))
        each = read_csv(os.path.join(record, name, f'{name}_runs.csv'))
        tables = conclusions[name]
        for law in LAWS:
            a = [r for r in rd if r['law'] == law and r['cls'] == 'all' and r['kind'] == 'all'][0]
            readings.append([which, law, a['runs'], a['strict'], a['ends'], r4(te_all[which][law]),
                             a['ends_pm3'], a['level'], a['exposure']])
            for r in rd:
                if r['law'] == law and r['cls'] != 'all' and r['tier'] != 'all' and r['kind'] == 'all':
                    t = tables[law][f"{r['cls']}/{r['tier']}"]
                    cells.append([which, law, r['cls'], r['tier'], r['runs'], r['ends'], r['exposure'],
                                  t['over_6db_at_or_above_minus3']])
            for kind in ('half_sine', 'sawtooth', 'srs'):
                t = tables[law][f'target/{kind}']
                targets.append([which, law, kind, t['runs'], t['ends'], t['exposure']])
            t = tables[law]['all/all']
            em = t['exposure_miss_db'] or {'n': 0, 'median': None, 'max': None}
            safety.append([which, law, t['runs'], t['over_3db'], t['over_3db_at_or_above_minus3'],
                           t['over_6db'], t['over_6db_at_or_above_minus3'], em['n'], r4(em['median']),
                           r4(em['max'])])
            none = {'n': 0, 'median': None, 'max': None}
            ex = t['ends_miss_excess_db'] or none
            hi = t['ends_miss_no_full_level_highest_db'] or none
            lv = t['level_miss_abs_mean_db'] or none
            passes = sum(r['law'] == law and r['ends'] == 'True' for r in each)
            misses.append([which, law, t['runs'], passes, t['ends_miss_no_full_level'],
                           t['ends_miss_never_past_probes'], ex['n'], r4(ex['median']), r4(ex['max']),
                           r4(hi['median']), lv['n'], r4(lv['median']), r4(lv['max'])])
            s = te[te_name]['tables'][law]['all/all']
            far = s['miss_at_full_level_furthest_ratio'] or {}
            te_srs.append([which, law, s['runs'], s['ends'], s['te'], s['ends_and_te'], s['te_of_full_level'],
                           s['ratio_median'], far.get('n', ''), r4(far.get('median')), r4(far.get('largest'))])
    write_csv('law_readings.csv', ['set', 'law', 'runs', 'strict', 'ends', 'ends_with_te_on_srs',
                                   'ends_pm3', 'level', 'exposure'], readings)
    write_csv('law_cells.csv', ['set', 'law', 'cls', 'tier', 'runs', 'ends', 'exposure',
                                'over_6db_at_or_near_full'], cells)
    write_csv('law_targets.csv', ['set', 'law', 'kind', 'runs', 'ends', 'exposure'], targets)
    write_csv('law_safety.csv', ['set', 'law', 'runs', 'over_3db', 'over_3db_at_or_near_full', 'over_6db',
                                 'over_6db_at_or_near_full', 'over_3db_runs', 'largest_exposure_median_db',
                                 'largest_exposure_max_db'], safety)
    write_csv('law_misses.csv', ['set', 'law', 'runs', 'ends_passes', 'misses_no_full_level',
                                 'misses_never_past_probes', 'misses_at_full_level', 'excess_median_db',
                                 'excess_max_db', 'highest_level_median_db', 'level_misses',
                                 'level_miss_mean_median_db', 'level_miss_mean_max_db'], misses)
    write_csv('law_te_srs.csv', ['set', 'law', 'runs', 'ends', 'te', 'ends_and_te', 'te_of_full_level',
                                 'ratio_median', 'te_misses_at_full', 'furthest_ratio_median',
                                 'furthest_ratio_largest'], te_srs)
    port = json.load(open(os.path.join(record, 'study_v02_rust', 'port_vs_rust.json')))
    table = []
    for which, key in (('study', 'study_v02'), ('audit', 'audit')):
        for law in ('followed', 'followed-hold'):
            p = port[key][law]['all/all']
            cell_moves = [abs(v['ends_rust'] - v['ends_port']) for c, v in port[key][law].items()
                          if c != 'all/all']
            table.append([which, law, p['runs'], p['ends_port'], p['ends_rust'], p['exposure_port'],
                          p['exposure_rust'], p['strict_port'], p['strict_rust'],
                          p['ends_port_pass_rust_miss'], p['ends_port_miss_rust_pass'],
                          p['runs_identical_exposure'], p['exposure_change_db']['median_abs'],
                          p['exposure_change_db']['max_up'], p['exposure_change_db']['max_down'],
                          r4(max(cell_moves))])
    write_csv('law_port_rust.csv', ['set', 'law', 'runs', 'ends_port', 'ends_rust', 'exposure_port',
                                    'exposure_rust', 'strict_port', 'strict_rust', 'ends_pass_to_miss',
                                    'ends_miss_to_pass', 'runs_same_exposure', 'exposure_change_median_abs_db',
                                    'exposure_change_max_up_db', 'exposure_change_max_down_db',
                                    'largest_cell_change_ends'], table)
    screen = read_csv(os.path.join(record, 'screen', 'screen_readings.csv'))
    write_csv('screen.csv', ['law', 'runs', 'strict', 'ends', 'level', 'exposure', 'seconds_median'],
              [[r['law'], r['runs'], r['strict'], r['ends'], r['level'], r['exposure'], r['seconds_median']]
               for r in screen if r['cls'] == 'all' and r['kind'] == 'all'])
    # The share inside the whole time-domain tolerance is given both of the runs with a last
    # full-level pulse ('all') and of every run, a run without a full-level pulse counted outside
    # ('all_of_runs').
    table = []
    for which, folder in (('study', study_runs), ('audit', audit_runs)):
        acc, total = {}, {}
        for name in sorted(os.listdir(folder)):
            if '__half_sine__' not in name and '__sawtooth__' not in name:
                continue
            d = json.load(open(os.path.join(folder, name)))
            law, kind = d['job']['law'], d['job']['kind']
            rows_, cols_ = d['job']['problem'].split('-')[1].split('_')[0].split('x')
            group = 'square' if rows_ == cols_ else 'more gauges'
            total[(law, kind, group)] = total.get((law, kind, group), 0) + 1
            c = d['card'].get('classical')
            if not c:
                continue
            keys = ['share_in_band_20pct', 'share_duration_10pct', 'share_velocity_20pct',
                    'share_compensation_20pct', 'share_post_slope_10pct', 'share_all_516']
            acc.setdefault((law, kind, group), []).append([c[k] == 1.0 if c[k] is not None else None for k in keys])
        for (law, kind, group), g in sorted(acc.items()):
            col = list(zip(*g))
            n = total[(law, kind, group)]
            table.append([which, law, kind, group, len(g)] + [
                '' if col[i][0] is None else r4(np.mean(col[i])) for i in range(6)] + [
                n, r4(sum(col[5]) / n)])
    write_csv('law_classical_time.csv', ['set', 'law', 'kind', 'systems', 'runs_at_full_level', 'peak_band',
                                         'duration', 'velocity', 'compensation', 'post_slope', 'all', 'runs',
                                         'all_of_runs'], table)


if __name__ == '__main__':
    main(*sys.argv[1:4])
