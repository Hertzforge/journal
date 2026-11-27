"""Every data file and every number of the article, read from the suite's problem folders, the
study's run folders, the claims file and the agreement records. Copyright 2026 Kevin Cross. MIT
license.

    python3 suite_results.py STUDY_RUNS PROBLEMS HELDOUT_PROBLEMS AGREEMENT_DIR

STUDY_RUNS holds the run sets (study, study_py, study_defaults, study_py_defaults,
study_repeat_*, study_py_repeat_*) and claims/ (readings.csv, claims.json). PROBLEMS and
HELDOUT_PROBLEMS are the problem folders of the study's and the held-back structures; only their
problem and test files are read. AGREEMENT_DIR holds the four pair files and the agreement output
of the comparison of the two versions. Nothing of the audit's runs is read.

Writes into ../data: problems.csv, example_reference.csv, schedules.csv, pooled.csv, effects.csv,
levels.csv, agreement.csv, defaults.csv, repeats.csv and numbers.csv (key, value, text, source):
the text of every number as the article writes it.
"""
import csv
import glob
import hashlib
import json
import math
import os
import re
import statistics
import sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
NUMBERS = []


def note(key, value, text, source):
    NUMBERS.append({'key': key, 'value': value, 'text': text, 'source': source})


def pct(x, nd=0):
    return f'{100 * x:.{nd}f}'


def comma(n):
    return f'{int(n):,}'


def write(name, fields, rows):
    with open(os.path.join(DATA, name), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in fields})
    print('wrote', name, len(rows), 'rows')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def kind_of(name):
    """frame-12x6-realistic_soft_s03 -> ('12x6', 'realistic_soft', 3)."""
    m = re.match(r'frame-(\d+x\d+)(?:-([a-z_]+))?_s(\d+)$', name)
    return m.group(1), m.group(2) or 'linear', int(m.group(3))


def med(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return statistics.median(xs) if xs else float('nan')


def quart(xs):
    xs = [x for x in xs if x is not None and not math.isnan(x)]
    if not xs:
        return float('nan'), float('nan')
    q = np.percentile(xs, [25, 75])
    return float(q[0]), float(q[1])


# ----------------------------------------------------------------------------------- problems
def problem_rows(root, which):
    rows = []
    for folder in sorted(glob.glob(os.path.join(root, 'frame-*'))):
        name = os.path.basename(folder)
        system, kind, seed = kind_of(name)
        p = json.load(open(os.path.join(folder, 'problem.json')))
        t3 = json.load(open(os.path.join(folder, 'test_T3.json')))
        t4 = json.load(open(os.path.join(folder, 'test_T4.json')))
        l1 = os.path.join(folder, 'test_L1.json')
        l1 = json.load(open(l1)) if os.path.exists(l1) else None
        fl, ref, ch = p['full_level'], p['reference'], p['checks']
        st = ch['state'].get('full_level', {})
        st6 = ch['state'].get('6db_over', {})
        res = t4['resonance']
        at = res.get('at_full_level') or {}
        rows.append({
            'set': which, 'problem': name, 'system': system, 'kind': kind, 'seed': seed,
            'modes': p['structure']['modes'], 'sizing': fl['sizing']['rule'],
            'spec_g_pk': fl['spec_amplitude_g_pk'],
            'random_median_change': fl['sizing'].get('random_median_change', ''),
            'ideal_drive_peak_v': ch['engine']['ideal_drive_peak_v'],
            'declared_rms_db': ref['declared_deviation']['amplitude_db_rms'],
            'declared_min_db': ref['declared_deviation']['amplitude_db_min'],
            'declared_share_under_6db': ref['declared_deviation']['share_under_minus_6_db'],
            'declared_share_under_20db': ref['declared_deviation']['share_under_minus_20_db'],
            'condition_median': ref['condition']['median'], 'condition_max': ref['condition']['max'],
            'state_median_abs_change': st.get('median_abs_change', ''),
            'state_largest_drop': st.get('largest_drop', ''),
            'state_largest_rise': st.get('largest_rise', ''),
            'state6_median_abs_change': st6.get('median_abs_change', ''),
            'play_control_peak_over_spec': ch['play']['full_level']['control_peak_over_spec'],
            'play_dwell_peak_over_spec': ch['play']['full_level']['dwell_control_peak_over_spec'],
            'highest_reachable_hz': ch['highest_reachable_hz'],
            't3_step_s': t3['step_s'], 't3_seconds': t3['seconds'], 't3_steps': len(t3['frequencies_hz']),
            't4_dwell_hz': t4['dwell_hz'], 't4_seconds': t4['seconds'],
            't4_mode_zeta': res['mode_zeta'], 't4_prominence_db': res['prominence_db'],
            't4_change': at.get('change', ''),
            't4_offset_bandwidths': at.get('offset_in_bandwidths', ''),
            'l1_gap_db': l1['limit']['gap_db'] if l1 else '',
            'l1_bite_db': l1['limit']['bite_db'] if l1 else '',
        })
    return rows


def generation_end(log):
    last = [ln for ln in open(log) if ln.startswith('GENERATION END')][-1]
    m = re.match(r'GENERATION END: (\d+) made, (\d+) refused, of (\d+)', last)
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def problems_part(problems, heldout):
    study = problem_rows(problems, 'study')
    held = problem_rows(heldout, 'heldout')
    rows = study + held
    write('problems.csv', list(rows[0].keys()), rows)
    made, refused, of = generation_end(os.path.join(problems, 'make_problems.log'))
    note('problems_made', made, comma(made), 'make_problems.log')
    note('problems_refused', refused, f'{refused}', 'make_problems.log')
    hm, hr, _ = generation_end(os.path.join(heldout, '..', 'problems.make.log'))
    note('heldout_made', hm, comma(hm), 'heldout problems.make.log')
    note('heldout_refused', hr, f'{hr}', 'heldout problems.make.log')
    assert made == len(study) and hm == len(held)
    seeds = json.load(open(os.path.join(heldout, '..', 'heldout_seeds.json')))
    note('heldout_seeds', seeds['seeds'], ', '.join(str(s) for s in seeds['seeds']), 'heldout_seeds.json')
    note('heldout_dropped', seeds['dropped'], ' and '.join(str(s) for s in seeds['dropped']),
         'heldout_seeds.json')
    note('study_seeds', sorted({r['seed'] for r in study}),
         ', '.join(str(s) for s in sorted({r['seed'] for r in study})), 'problems.csv')
    # The modes and the band
    note('modes_first', study[0]['modes'], f"{study[0]['modes']}", 'problem.json structure.modes, first problem')
    counts = [int(r['modes']) for r in study]
    note('modes_min', min(counts), f'{min(counts)}', 'problems.csv modes, study')
    note('modes_max', max(counts), f'{max(counts)}', 'problems.csv modes, study')

    def by(rs, key, f):
        out = defaultdict(list)
        for r in rs:
            out[f(r)].append(r[key])
        return out

    # Full level: spec amplitude
    spec = [r['spec_g_pk'] for r in study]
    note('spec_g_min', min(spec), f'{min(spec):.2f}', 'problems.csv spec_g_pk')
    note('spec_g_max', max(spec), f'{max(spec):.1f}', 'problems.csv spec_g_pk')
    note('spec_g_median', med(spec), f'{med(spec):.2f}', 'problems.csv spec_g_pk')
    for tier in ('realistic', 'strong'):
        xs = [r['state_median_abs_change'] for r in study if r['kind'] == tier]
        note(f'state_change_{tier}', med(xs), pct(med(xs), 2), 'problems.csv state_median_abs_change')
        xs6 = [r['state6_median_abs_change'] for r in study if r['kind'] == tier]
        note(f'state6_change_{tier}', med(xs6), pct(med(xs6), 2), 'problems.csv state6_median_abs_change')
        xs = [r['state_largest_drop'] for r in study if r['kind'] == tier]
        note(f'state_drop_{tier}', med(xs), pct(-med(xs), 1), 'problems.csv state_largest_drop')
        xs = [r['state_largest_rise'] for r in study if r['kind'] == tier]
        note(f'state_rise_{tier}', med(xs), pct(med(xs), 1), 'problems.csv state_largest_rise')
    sized = Counter(r['sizing'] for r in study)
    for k, v in sized.items():
        note(f'sizing_{k}', v, comma(v), 'problems.csv sizing')
    # The ideal drive in engine volts before the gain
    v = [r['ideal_drive_peak_v'] for r in study]
    note('ideal_v_median', med(v), f'{med(v):.2f}', 'problems.csv ideal_drive_peak_v')
    note('ideal_v_min', min(v), f'{min(v):.2f}', 'problems.csv ideal_drive_peak_v')
    note('ideal_v_max', max(v), f'{max(v):.1f}', 'problems.csv ideal_drive_peak_v')
    n10 = sum(x >= 10 for x in v)
    note('ideal_v_over_10', n10, f'{n10}', 'problems.csv ideal_drive_peak_v >= 10')
    n9 = sum(x * 10 ** (6 / 20) > 9 for x in v)
    note('ideal_v_6db_over_9', n9, f'{n9}', 'problems.csv ideal_drive_peak_v x 6 dB > 9 V')
    hv = [r['ideal_drive_peak_v'] for r in held]
    note('held_ideal_v_over_10', sum(x >= 10 for x in hv), f'{sum(x >= 10 for x in hv)}',
         'problems.csv heldout ideal_drive_peak_v >= 10')
    # Declared deviation by system
    for system in ('12x3', '12x6', '24x12', '6x6', '12x12'):
        xs = [r['declared_rms_db'] for r in study if r['system'] == system]
        note(f'declared_rms_{system}', med(xs), f'{med(xs):.2f}', 'problems.csv declared_rms_db')
        xs = [r['declared_share_under_6db'] for r in study if r['system'] == system]
        note(f'declared_under6_{system}', med(xs), pct(med(xs), 1), 'problems.csv declared_share_under_6db')
        xs = [r['declared_min_db'] for r in study if r['system'] == system]
        note(f'declared_min_{system}', min(xs), f'{min(xs):.1f}', 'problems.csv declared_min_db (least)')
    sq = [r['declared_rms_db'] for r in study if r['system'] in ('6x6', '12x12')]
    note('declared_rms_square_max', max(sq), f'{max(sq):.2f}', 'problems.csv declared_rms_db square')
    # The play of the ideal drive through the structure, at 8 octaves a minute
    for tier in ('linear', 'realistic', 'strong'):
        xs = [20 * math.log10(r['play_control_peak_over_spec']) for r in study if r['kind'] == tier]
        note(f'play_db_{tier}', med(xs), f'{med(xs):.1f}', 'problems.csv play_control_peak_over_spec (dB)')
        note(f'play_db_{tier}_max', max(xs), f'{max(xs):.1f}', 'problems.csv play_control_peak_over_spec (dB)')
        xs = [20 * math.log10(r['play_dwell_peak_over_spec']) for r in study if r['kind'] == tier]
        note(f'play_dwell_db_{tier}', med(xs), f'{med(xs):.1f}', 'problems.csv play_dwell_peak_over_spec (dB)')
    hz = max(r['highest_reachable_hz'] for r in study + held)
    note('highest_reachable_max', hz, f'{hz:.0f}', 'problems.csv highest_reachable_hz')
    # The stepped test and the dwell
    xs = [r['t3_step_s'] for r in study]
    note('t3_step_s_min', min(xs), f'{min(xs):.2f}', 'problems.csv t3_step_s')
    note('t3_step_s_median', med(xs), f'{med(xs):.2f}', 'problems.csv t3_step_s')
    note('t3_step_s_max', max(xs), f'{max(xs):.2f}', 'problems.csv t3_step_s')
    xs = [r['t3_seconds'] for r in study]
    note('t3_seconds_median', med(xs), f'{med(xs):.0f}', 'problems.csv t3_seconds')
    note('t3_seconds_max', max(xs), f'{max(xs):.0f}', 'problems.csv t3_seconds')
    note('t3_steps', study[0]['t3_steps'], f"{study[0]['t3_steps']}", 'test_T3.json frequencies_hz')
    xs = [r['t4_dwell_hz'] for r in study]
    note('t4_hz_min', min(xs), f'{min(xs):.1f}', 'problems.csv t4_dwell_hz')
    note('t4_hz_max', max(xs), f'{max(xs):.1f}', 'problems.csv t4_dwell_hz')
    xs = [r['t4_seconds'] for r in study]
    note('t4_seconds_median', med(xs), f'{med(xs):.1f}', 'problems.csv t4_seconds')
    note('t4_seconds_max', max(xs), f'{max(xs):.1f}', 'problems.csv t4_seconds')
    n10s = sum(x < 10.5 for x in xs)
    note('t4_at_floor_share', n10s / len(xs), pct(n10s / len(xs)), 'problems.csv t4_seconds < 10.5 s')
    for tier in ('linear', 'realistic', 'strong'):
        xs = [abs(r['t4_offset_bandwidths']) for r in study if r['kind'] == tier
              and r['t4_offset_bandwidths'] != '']
        if not xs:
            continue
        note(f't4_offset_{tier}', med(xs), f'{med(xs):.2f}', 'problems.csv |t4_offset_bandwidths|')
        n1 = sum(x > 1 for x in xs)
        note(f't4_offset_over1_{tier}', n1 / len(xs), pct(n1 / len(xs)), 'problems.csv |t4_offset| > 1')
    xs = [r['l1_gap_db'] for r in study if r['l1_gap_db'] != '']
    note('l1_gap_median', med(xs), f'{med(xs):.1f}', 'problems.csv l1_gap_db')
    note('l1_problems', len(xs), f'{len(xs)}', 'problems.csv l1_gap_db')
    xs = [r['l1_bite_db'] for r in study if r['l1_bite_db'] != '']
    note('l1_bite_median', med(xs), f'{med(xs):.1f}', 'problems.csv l1_bite_db')
    return study, held


def example_part(problems):
    """The reference of one 6 x 12 problem at its first control, and the ideal drive."""
    folder = os.path.join(problems, 'frame-12x6-realistic_s00')
    p = json.load(open(os.path.join(folder, 'problem.json')))
    hz = np.fromfile(os.path.join(folder, 'reference_hz.f8'), '<f8')
    shape = p['files']['reference_amplitude']['shape']
    amp = np.fromfile(os.path.join(folder, 'reference_amplitude.f8'), '<f8').reshape(shape)
    drive = np.fromfile(os.path.join(folder, 'ideal_drive.c16'), '<c16').reshape(
        p['files']['ideal_drive']['shape'])
    spec = p['full_level']['spec_amplitude_mps2_pk']
    gain = p['checks']['engine']['ideal_drive_peak_v']
    rows = []
    for i in range(len(hz)):
        ratio = amp[i] / spec
        rows.append({'hz': f'{hz[i]:.6g}',
                     'ref_over_spec_db_min': f'{20 * np.log10(ratio.min()):.4f}',
                     'ref_over_spec_db_median': f'{20 * np.log10(np.median(ratio)):.4f}',
                     'ref_over_spec_db_max': f'{20 * np.log10(ratio.max()):.4f}',
                     'ideal_drive_max_engine_v': f'{np.abs(drive[i]).max() / gain:.6f}'})
    write('example_reference.csv', list(rows[0].keys()), rows)
    note('example_points', len(hz), comma(len(hz)), 'reference_hz.f8 of frame-12x6-realistic_s00')
    note('example_spec_g', p['full_level']['spec_amplitude_g_pk'],
         f"{p['full_level']['spec_amplitude_g_pk']:.2f}", 'problem.json frame-12x6-realistic_s00')
    note('example_gain', gain, f'{gain:.2f}', 'problem.json frame-12x6-realistic_s00 ideal_drive_peak_v')
    note('fs_hz', p['fs_hz'], f"{p['fs_hz']:.0f}", 'problem.json fs_hz')
    note('band_lo', p['band_hz'][0], f"{p['band_hz'][0]:.0f}", 'problem.json band_hz')
    note('band_hi', p['band_hz'][1], f"{p['band_hz'][1]:.0f}", 'problem.json band_hz')


def schedules_part(problems):
    """Each test's schedule on one problem: frequency against time, as the test file states it."""
    folder = os.path.join(problems, 'frame-12x6-realistic_s00')
    rows = []
    for test in ('T1', 'T2', 'T5', 'T3', 'T4'):
        t = json.load(open(os.path.join(folder, f'test_{test}.json')))
        lo, hi = t['band_hz']
        if t['kind'] == 'sweep':
            octaves = math.log2(hi / lo)
            seconds = t['seconds']
            for k in range(201):
                s = seconds * k / 200
                o = octaves * k / 200
                f = lo * 2 ** o if t['direction'] == 'up' else hi * 2 ** -o
                rows.append({'test': test, 'seconds': f'{s:.4f}', 'hz': f'{f:.4f}'})
        elif t['kind'] == 'stepped':
            for k, f in enumerate(t['frequencies_hz']):
                rows.append({'test': test, 'seconds': f"{k * t['step_s']:.4f}", 'hz': f'{f:.4f}'})
                rows.append({'test': test, 'seconds': f"{(k + 1) * t['step_s']:.4f}", 'hz': f'{f:.4f}'})
        else:
            rows.append({'test': test, 'seconds': '0', 'hz': f"{t['dwell_hz']:.4f}"})
            rows.append({'test': test, 'seconds': f"{t['seconds']:.4f}", 'hz': f"{t['dwell_hz']:.4f}"})
        if test == 'T1':
            note('t1_seconds', t['seconds'], f"{t['seconds']:.1f}", 'test_T1.json seconds')
            note('t1_rate', t['rate_oct_per_min'], f"{t['rate_oct_per_min']:.0f}", 'test_T1.json')
            ld = t['ladder']
            note('ladder', ld['table_db'], ', '.join(f'{x:.0f}' for x in ld['table_db'][:-1]) +
                 f" and {ld['table_db'][-1]:.0f}", 'test_T1.json ladder.table_db')
            note('rung_s', ld['per_rung']['seconds'], f"{ld['per_rung']['seconds']:.0f}",
                 'test_T1.json ladder.per_rung')
            note('sysid_db', ld['sysid_level_db'], f"{ld['sysid_level_db']:.0f}", 'test_T1.json ladder')
            note('noise_rel', t['noise']['relative'], f"{t['noise']['relative']:.0e}".replace('e-0', 'e-'),
                 'test_T1.json noise.relative')
        if test == 'T2':
            note('t2_seconds', t['seconds'], f"{t['seconds']:.1f}", 'test_T2.json seconds')
            note('t2_rate', t['rate_oct_per_min'], f"{t['rate_oct_per_min']:.0f}", 'test_T2.json')
        if test == 'T3':
            note('t3_per_octave', t['steps_per_octave'], f"{t['steps_per_octave']}", 'test_T3.json')
    write('schedules.csv', ['test', 'seconds', 'hz'], rows)


# ----------------------------------------------------------------------------------- readings
def readings_part(claims_dir):
    path = os.path.join(claims_dir, 'readings.csv')
    rs = list(csv.DictReader(open(path)))
    note('readings_rows', len(rs), comma(len(rs)), 'readings.csv')
    note('readings_sha', sha256(path), sha256(path), 'readings.csv')
    for r in rs:
        for k in ('iec_share', 'worst_over_db', 'completion'):
            r[k] = float(r[k]) if r[k] != '' else float('nan')
    by_version = Counter(r['version'] for r in rs)
    for v, n in by_version.items():
        note(f'runs_{v}', n, comma(n), 'readings.csv')
    held = [r for r in rs if r['outcome'] == 'held_by_identification']
    note('held_runs', len(held), f'{len(held)}', 'readings.csv outcome held_by_identification')
    note('held_problems', len({r['structure'] for r in held}), f"{len({r['structure'] for r in held})}",
         'readings.csv, distinct problem folders (system, kind and structure)')
    note('held_t4', sum(r['test'] == 'T4' for r in held), f"{sum(r['test'] == 'T4' for r in held)}",
         'readings.csv')
    hf = [r for r in rs if r['version'] == 'hertzforge']
    note('hf_completed', sum(r['outcome'] == 'completed' for r in hf),
         comma(sum(r['outcome'] == 'completed' for r in hf)), 'readings.csv')
    note('hf_done', len(hf) - len(held), comma(len(hf) - len(held)), 'readings.csv')
    laws_per = defaultdict(set)
    for r in rs:
        laws_per[(r['version'], r['test'])].add(r['law'])
    # The law both versions run on the sweeps: its completed runs, version by version
    shared = set.intersection(*[{r['law'] for r in rs if r['version'] == v and r['test'] == 'T1'}
                                for v in ('hertzforge', 'python')])
    for v in ('hertzforge', 'python'):
        for k in ('linear', 'realistic', 'strong'):
            for t in ('T1', 'T2', 'T5'):
                g = [r for r in rs if r['version'] == v and r['law'] in shared and r['kind'] == k
                     and r['test'] == t]
                if g:
                    c = sum(r['outcome'] == 'completed' for r in g)
                    note(f'shared_{v}_{k}_{t}_done', c, f'{c}', 'readings.csv, the law both versions run')
                    note(f'shared_{v}_{k}_{t}_n', len(g), f'{len(g)}', 'readings.csv, the law both versions run')
    # Pooled cells: version x system x kind x test, and version x kind x test over the systems
    groups = defaultdict(list)
    for r in rs:
        groups[(r['version'], r['system'], r['kind'], r['test'])].append(r)
        groups[(r['version'], 'all', r['kind'], r['test'])].append(r)
        groups[(r['version'], 'all', 'all', r['test'])].append(r)
    rows = []
    for (v, s, k, t), g in sorted(groups.items()):
        q1, q3 = quart([x['iec_share'] for x in g])
        rows.append({
            'version': v, 'system': s, 'kind': k, 'test': t, 'runs': len(g),
            'laws': len({x['law'] for x in g}),
            'completed_share': f"{sum(x['outcome'] == 'completed' for x in g) / len(g):.4f}",
            'held_share': f"{sum(x['outcome'] == 'held_by_identification' for x in g) / len(g):.4f}",
            'iec_share_median': f"{med([x['iec_share'] for x in g]):.4f}",
            'iec_share_q1': f'{q1:.4f}', 'iec_share_q3': f'{q3:.4f}',
            'completion_median': f"{med([x['completion'] for x in g]):.4f}",
            'worst_over_db_median': f"{med([x['worst_over_db'] for x in g]):.3f}",
            'scored_share': f"{sum(x['scored'] == '1' for x in g) / len(g):.4f}",
        })
    write('pooled.csv', list(rows[0].keys()), rows)
    pooled = {(r['version'], r['system'], r['kind'], r['test']): r for r in rows}
    for v in ('hertzforge', 'python'):
        for k in ('linear', 'realistic', 'strong', 'realistic_soft', 'realistic_hard', 'strong_soft',
                  'strong_hard'):
            for t in ('T1', 'T2', 'T3', 'T4', 'T5', 'L1'):
                r = pooled.get((v, 'all', k, t))
                if not r:
                    continue
                note(f'done_{v}_{k}_{t}', float(r['completed_share']), pct(float(r['completed_share'])),
                     'pooled.csv completed_share')
                note(f'iec_{v}_{k}_{t}', float(r['iec_share_median']), pct(float(r['iec_share_median'])),
                     'pooled.csv iec_share_median')
                note(f'over_{v}_{k}_{t}', float(r['worst_over_db_median']),
                     f"{float(r['worst_over_db_median']):.1f}", 'pooled.csv worst_over_db_median')
    for v in ('hertzforge', 'python'):
        for t in ('T1', 'T2', 'T3', 'T4', 'T5', 'L1'):
            if (v, t) in laws_per:
                note(f'laws_{v}_{t}', len(laws_per[(v, t)]), f'{len(laws_per[(v, t)])}', 'readings.csv')
    # Stepped tests: the largest completed share of any cell
    t3 = [r for r in rows if r['test'] == 'T3' and r['system'] != 'all' and r['version'] == 'hertzforge']
    top = max(float(r['completed_share']) for r in t3)
    note('t3_cell_done_max', top, pct(top), 'pooled.csv T3 cells')
    # Share of the stepped test's runs inside the band at every judged point: the excursion
    for t in ('T1', 'T2', 'T3', 'T4', 'T5'):
        g = [r for r in hf if r['test'] == t and r['outcome'] == 'completed']
        ex = [float(r['excursion_iec_check_point']) for r in g if r['excursion_iec_check_point'] != '']
        n0 = sum(x <= 0 for x in ex)
        note(f'inside_all_{t}', n0 / len(g) if g else 0, pct(n0 / len(g)) if g else '0',
             'readings.csv completed runs with excursion_iec_check_point <= 0')
    return rs


# ----------------------------------------------------------------------------------- claims
def claims_part(claims_dir):
    path = os.path.join(claims_dir, 'claims.json')
    c = json.load(open(path))
    note('claims_sha', sha256(path), sha256(path), 'claims.json')
    cl = c['claims']
    note('claims_n', len(cl), comma(len(cl)), 'claims.json')
    kinds = Counter(x['kind'] for x in cl)
    for k, n in kinds.items():
        note(f'claims_{k}', n, comma(n), 'claims.json')
    for k, v in c['rule']['thresholds'].items():
        note(f'threshold_{k}', v, f'{v}', 'claims.json rule.thresholds')
    # Effects: no law named; the number of laws pooled is kept
    eff = [x for x in cl if x['kind'] == 'effect']
    rows = []
    for x in eff:
        s = x['study']
        rows.append({'id': x['id'], 'version': x['version'], 'system': x['system'],
                     'kind': x['structure_kind'], 'against': x['against'], 'test': x['test'],
                     'reading': x['reading'], 'side': x['side'], 'median': s['median'],
                     'q1': s['q1'], 'q3': s['q3'], 'n': s['n'], 'laws': s['laws'],
                     'higher': s['higher'], 'lower': s['lower']})
    write('effects.csv', list(rows[0].keys()), rows)
    eff_tests = Counter(x['test'] for x in eff)
    for t in ('T1', 'T2', 'T3', 'T4', 'T5', 'L1'):
        note(f'effects_{t}', eff_tests.get(t, 0), f'{eff_tests.get(t, 0)}', 'claims.json effect claims')
    # Levels: law replaced by nothing; the claim id names it in claims.json
    lev = [x for x in cl if x['kind'] == 'level']
    rows = []
    for x in lev:
        s = x['study']
        rows.append({'id': x['id'], 'version': x['version'], 'system': x['system'],
                     'kind': x['structure_kind'], 'test': x['test'], 'line': x['line'],
                     'side': x['side'], 'median_db': s['median'], 'q1_db': s['q1'], 'q3_db': s['q3'],
                     'n': s['n'], 'unscored': s['unscored'], 'median_iec_share': s['median_iec_share'],
                     'median_completion': s['median_completion']})
    write('levels.csv', list(rows[0].keys()), rows)
    out = Counter((x['version'], x['test'], x['line'], x['side']) for x in lev)
    for v in ('hertzforge', 'python'):
        for t in ('T1', 'T2', 'T3', 'T4', 'T5', 'L1'):
            for line in ('iec_check_point', 'iec_reference_point', 'mil_composite'):
                for side in ('inside', 'outside'):
                    n = out.get((v, t, line, side), 0)
                    note(f'level_{v}_{t}_{line}_{side}', n, f'{n}', 'levels.csv')
    # Sweeps and steps: any inside at the check point?
    sweeps = [x for x in lev if x['line'] == 'iec_check_point' and x['test'] != 'T4']
    n_in = sum(x['side'] == 'inside' for x in sweeps)
    note('level_nondwell_check_n', len(sweeps), comma(len(sweeps)), 'levels.csv')
    note('level_nondwell_check_inside', n_in, f'{n_in}', 'levels.csv')
    dw = [x for x in lev if x['line'] == 'iec_check_point' and x['test'] == 'T4']
    note('level_dwell_check_n', len(dw), f'{len(dw)}', 'levels.csv')
    note('level_dwell_check_inside', sum(x['side'] == 'inside' for x in dw),
         f"{sum(x['side'] == 'inside' for x in dw)}", 'levels.csv')
    for v in ('hertzforge', 'python'):
        for line in ('iec_check_point', 'iec_reference_point', 'mil_composite'):
            g = [x for x in lev if x['version'] == v and x['line'] == line and x['test'] != 'T4']
            n_in = sum(x['side'] == 'inside' for x in g)
            note(f'nondwell_{v}_{line}_inside', n_in, f'{n_in}', 'levels.csv')
            note(f'nondwell_{v}_{line}_n', len(g), f'{len(g)}', 'levels.csv')
            if line != 'iec_check_point':
                g3 = [x for x in g if x['test'] == 'T3']
                note(f'stepped_{v}_{line}_inside', sum(x['side'] == 'inside' for x in g3),
                     f"{sum(x['side'] == 'inside' for x in g3)}", 'levels.csv')
    for k, v in c['rule']['thresholds'].items():
        if k != 'worst_over_db':
            note(f'threshold_{k}_points', v * 100, f'{v * 100:.0f}', 'claims.json rule.thresholds, in points')
    # Dwell inside on every structure kind?
    kinds_in = sorted({x['structure_kind'] for x in dw if x['side'] == 'inside'})
    kinds_all = sorted({x['structure_kind'] for x in dw})
    note('dwell_kinds_inside', len(kinds_in), f'{len(kinds_in)}', 'levels.csv')
    note('dwell_kinds_all', len(kinds_all), f'{len(kinds_all)}', 'levels.csv')
    # Dwell cells (system, kind) where at least one law's median is inside
    cells = defaultdict(list)
    for x in dw:
        cells[(x['system'], x['structure_kind'])].append(x['side'])
    n_cells_in = sum('inside' in v for v in cells.values())
    note('dwell_cells_n', len(cells), f'{len(cells)}', 'levels.csv')
    note('dwell_cells_inside', n_cells_in, f'{n_cells_in}', 'levels.csv')
    return c


# ----------------------------------------------------------------------------------- agreement
def agreement_part(adir):
    out = json.load(open(os.path.join(adir, 'agreement_f_output.json')))
    sets = {'a': ('pairs_hf_ideal__py_mguard_p.json', 'pairs_hf_ideal_g__py_mguard_pg.json'),
            'b': ('pairs_hf_own__py_given_p.json', 'pairs_hf_own_g__py_given_pg.json')}
    rows = []
    for s, (main, guard) in sets.items():
        m = json.load(open(os.path.join(adir, main)))['rows']
        g = {r['case']: r for r in json.load(open(os.path.join(adir, guard)))['rows']}
        merged = [g[r['case']] if r.get('outcome_agrees') is None else r for r in m]
        assert all(r['outcome_agrees'] is not None for r in merged)
        per = defaultdict(lambda: [0, 0, 0])
        for r in merged:
            for t in (r['test'], 'all'):
                per[t][0] += 1
                per[t][1] += bool(r['outcome_agrees'])
                per[t][2] += bool(r['outcome_agrees'] and r['readings_agree'])
        assert per['all'] == [out[s]['pairs'], out[s]['outcome_agrees'], out[s]['both_agree']], s
        for t in ('T1', 'T2', 'T3', 'T4', 'T5', 'all'):
            n, o, b = per[t]
            rows.append({'set': s, 'test': t, 'pairs': n, 'outcome_agrees': o, 'both_agree': b})
            note(f'agree_{s}_{t}_pairs', n, f'{n}', 'agreement.csv')
            note(f'agree_{s}_{t}_outcome', o, f'{o}', 'agreement.csv')
            note(f'agree_{s}_{t}_both', b, f'{b}', 'agreement.csv')
        under = Counter()
        for r in merged:
            if r['outcome_agrees']:
                for b in r.get('beyond') or []:
                    under[b['key']] += 1
        note(f'agree_{s}_worst_under', under['amplitude.error_db.worst_under'],
             f"{under['amplitude.error_db.worst_under']}", 'pair files, beyond')
    write('agreement.csv', ['set', 'test', 'pairs', 'outcome_agrees', 'both_agree'], rows)
    lag = json.load(open(os.path.join(adir, 'lag_check_output.json')))
    return lag


# ----------------------------------------------------------------------------------- run sets
def card_reading(folder):
    c = json.load(open(os.path.join(folder, 'card.json')))
    comp = c.get('completion') or {}
    outcome = comp.get('outcome')
    scored = bool(c.get('scored'))
    if scored:
        cov = 1.0 if outcome == 'completed' else (comp.get('coverage') or 0.0)
        iec = c['amplitude']['iec_check_point']['share_inside'] * cov
        over = c['resonances']['worst_db']
        ex = c['amplitude']['iec_check_point']['worst_excursion_db']
    else:
        iec, over, ex, cov = 0.0, float('nan'), float('nan'), comp.get('coverage') or 0.0
    return {'outcome': outcome, 'iec_share': iec, 'worst_over_db': over, 'excursion': ex,
            'completion': 1.0 if outcome == 'completed' else cov}


def sets_part(runs, readings):
    index = {(r['version'], r['structure'], r['test'], r['law']): r for r in readings}
    # The default check: the engine's default protections and the 9 V ceiling
    rows = []
    for setname, version in (('study_defaults', 'hertzforge'), ('study_py_defaults', 'python')):
        for folder in sorted(glob.glob(os.path.join(runs, setname, 'frame-*', '*__*'))):
            if not os.path.exists(os.path.join(folder, 'card.json')):
                continue
            problem = os.path.basename(os.path.dirname(folder))
            test, law = os.path.basename(folder).split('__')
            system, kind, seed = kind_of(problem)
            d = card_reading(folder)
            s = index[(version, problem, test, law)]
            rows.append({'version': version, 'problem': problem, 'system': system, 'kind': kind,
                         'test': test, 'outcome_defaults': d['outcome'], 'outcome_study': s['outcome'],
                         'iec_defaults': f"{d['iec_share']:.4f}", 'iec_study': f"{s['iec_share']:.4f}",
                         'completion_defaults': f"{d['completion']:.4f}",
                         'completion_study': f"{s['completion']:.4f}"})
    write('defaults.csv', list(rows[0].keys()), rows)
    for v in ('hertzforge', 'python'):
        g = [r for r in rows if r['version'] == v]
        note(f'defaults_{v}_n', len(g), f'{len(g)}', 'defaults.csv')
        dc = sum(r['outcome_defaults'] == 'completed' for r in g)
        sc = sum(r['outcome_study'] == 'completed' for r in g)
        note(f'defaults_{v}_done', dc / len(g), pct(dc / len(g)), 'defaults.csv')
        note(f'defaults_{v}_study_done', sc / len(g), pct(sc / len(g)), 'defaults.csv')
        lower = sum(float(r['iec_defaults']) < float(r['iec_study']) - 0.05 for r in g)
        higher = sum(float(r['iec_defaults']) > float(r['iec_study']) + 0.05 for r in g)
        note(f'defaults_{v}_lower', lower, f'{lower}', 'defaults.csv iec more than 0.05 lower')
        note(f'defaults_{v}_higher', higher, f'{higher}', 'defaults.csv iec more than 0.05 higher')
        t4 = [r for r in g if r['test'] == 'T4']
        note(f'defaults_{v}_t4_n', len(t4), f'{len(t4)}', 'defaults.csv')
        note(f'defaults_{v}_t4_done', sum(r['outcome_defaults'] == 'completed' for r in t4),
             f"{sum(r['outcome_defaults'] == 'completed' for r in t4)}", 'defaults.csv')
        other = [r for r in g if r['test'] != 'T4']
        note(f'defaults_{v}_other_done', sum(r['outcome_defaults'] == 'completed' for r in other),
             f"{sum(r['outcome_defaults'] == 'completed' for r in other)}", 'defaults.csv')
        note(f'defaults_{v}_other_n', len(other), f'{len(other)}', 'defaults.csv')
        same = sum(r['outcome_defaults'] == r['outcome_study'] for r in g)
        note(f'defaults_{v}_same_outcome', same, f'{same}', 'defaults.csv')
    # Repeats: each with its own noise seed (and, in the Hertzforge version, identification seed)
    rows = []
    for version, pattern in (('hertzforge', 'study_repeat_*'), ('python', 'study_py_repeat_*')):
        for setdir in sorted(glob.glob(os.path.join(runs, pattern))):
            rep = setdir.rsplit('_', 1)[1]
            for folder in sorted(glob.glob(os.path.join(setdir, 'frame-*', '*__*'))):
                if not os.path.exists(os.path.join(folder, 'card.json')):
                    continue
                problem = os.path.basename(os.path.dirname(folder))
                test, law = os.path.basename(folder).split('__')
                d = card_reading(folder)
                s = index.get((version, problem, test, law))
                rows.append({'version': version, 'problem': problem, 'test': test, 'law': law,
                             'repeat': rep, 'outcome': d['outcome'], 'iec_share': f"{d['iec_share']:.4f}",
                             'outcome_study': s['outcome'] if s else '',
                             'iec_study': f"{s['iec_share']:.4f}" if s else ''})
    # A unit names a run without its law: the laws of each problem and test numbered in order
    laws = defaultdict(set)
    for r in rows:
        laws[(r['version'], r['problem'], r['test'])].add(r['law'])
    for r in rows:
        k = sorted(laws[(r['version'], r['problem'], r['test'])]).index(r.pop('law')) + 1
        r['unit'] = f"{r['problem']}/{r['test']}/{k}"
    write('repeats.csv', ['version', 'problem', 'test', 'unit', 'repeat', 'outcome', 'iec_share',
                          'outcome_study', 'iec_study'], rows)
    return rows


def repeats_summary(rows):
    units = defaultdict(list)
    for r in rows:
        units[(r['version'], r['unit'])].append(r)
    for v in ('hertzforge', 'python'):
        spans, same, n_paired = [], 0, 0
        for (vv, _), g in units.items():
            if vv != v or g[0]['iec_study'] == '':
                continue
            xs = [float(x['iec_share']) for x in g] + [float(g[0]['iec_study'])]
            spans.append(max(xs) - min(xs))
            n_paired += 1
            same += len({x['outcome'] for x in g} | {g[0]['outcome_study']}) == 1
        note(f'repeat_{v}_units', n_paired, f'{n_paired}', 'repeats.csv')
        note(f'repeat_{v}_same_outcome', same, f'{same}', 'repeats.csv')
        note(f'repeat_{v}_span_median', med(spans), pct(med(spans), 1), 'repeats.csv iec span')
        note(f'repeat_{v}_span_max', max(spans), pct(max(spans), 1), 'repeats.csv iec span')
        over = sum(s > 0.05 for s in spans)
        note(f'repeat_{v}_span_over_threshold', over, f'{over}', 'repeats.csv iec span > 0.05')


def effects_summary(claims, readings):
    """Each effect of the structure by version, test, comparison and reading: how many systems
    carry a claim, of how many where both kinds ran, the range of the medians and the ids."""
    ran = defaultdict(set)
    for r in readings:
        ran[(r['version'], r['test'], r['kind'])].add(r['system'])
    eff = [x for x in claims['claims'] if x['kind'] == 'effect']
    groups = defaultdict(list)
    for x in eff:
        groups[(x['version'], x['test'], x['structure_kind'], x['against'], x['reading'])].append(x)
    note('effects_against_harder', sum((x['reading'] == 'worst_over_db') == (x['side'] == 'higher')
                                       for x in eff), f'{len(eff)}', 'claims.json effect sides')
    assert all((x['reading'] == 'worst_over_db') == (x['side'] == 'higher') for x in eff)
    for v in ('hertzforge', 'python'):
        for t in ('T1', 'T2', 'T3', 'T4', 'T5', 'L1'):
            for k, a in (('realistic', 'linear'), ('strong', 'realistic'), ('strong', 'linear')):
                tested = ran[(v, t, k)] & ran[(v, t, a)]
                if not tested:
                    continue
                key = f'eff_{v}_{t}_{k}_{a}'
                note(key + '_cells', len(tested), f'{len(tested)}', 'readings.csv systems with both kinds')
                for reading in ('iec_share', 'worst_over_db', 'completion'):
                    g = sorted(groups.get((v, t, k, a, reading), []), key=lambda x: x['id'])
                    rk = {'iec_share': 'iec', 'worst_over_db': 'over', 'completion': 'done'}[reading]
                    note(f'{key}_{rk}_n', len(g), f'{len(g)}', 'claims.json effect claims')
                    if not g:
                        continue
                    ms = [abs(x['study']['median']) for x in g]
                    if reading == 'worst_over_db':
                        lo, hi = f'{min(ms):.1f}', f'{max(ms):.1f}'
                    else:
                        lo, hi = pct(min(ms)), pct(max(ms))
                    note(f'{key}_{rk}_min', min(ms), lo, 'claims.json effect study.median')
                    note(f'{key}_{rk}_max', max(ms), hi, 'claims.json effect study.median')
                    note(f'{key}_{rk}_ids', [x['id'] for x in g], ', '.join(x['id'] for x in g),
                         'claims.json effect ids')
    # The dwell's levels at the check point, by structure kind
    lev = [x for x in claims['claims'] if x['kind'] == 'level' and x['line'] == 'iec_check_point']
    for k in ('linear', 'realistic', 'strong', 'realistic_soft', 'realistic_hard', 'strong_soft',
              'strong_hard'):
        g = sorted([x for x in lev if x['test'] == 'T4' and x['structure_kind'] == k], key=lambda x: x['id'])
        ins = [x for x in g if x['side'] == 'inside']
        note(f'dwell_in_{k}', len(ins), f'{len(ins)}', 'levels.csv T4 check point inside')
        note(f'dwell_all_{k}', len(g), f'{len(g)}', 'levels.csv T4 check point')
        note(f'dwell_in_{k}_id', ins[0]['id'], ins[0]['id'], 'levels.csv first inside T4 claim')
    for t in ('T1', 'T2', 'T3', 'T5', 'L1'):
        g = sorted([x for x in lev if x['test'] == t], key=lambda x: x['id'])
        note(f'level_check_{t}_first_id', g[0]['id'], g[0]['id'], 'levels.csv first check-point claim')
        ms = [x['study']['median'] for x in g if x['study']['median'] is not None]
        note(f'level_check_{t}_none', len(g) - len(ms), f'{len(g) - len(ms)}', 'levels.csv median None')
        note(f'level_check_{t}_least', min(ms), f'{min(ms):.1f}', 'levels.csv least median excursion')


def cases_part(problems, heldout, runs):
    """The case files of the study's and the held-back problems, and the rescore's record."""
    for which, root in (('study', problems), ('heldout', heldout)):
        cases = [os.path.basename(c)[:-5] for c in glob.glob(os.path.join(root, 'frame-*', 'cases', '*.json'))]
        note(f'cases_{which}', len(cases), comma(len(cases)), f'{which} problem folders, cases/')
        sweeps = sum(c.split('__')[0] in ('T1', 'T2', 'T5', 'L1') and c.endswith('__matrix') for c in cases)
        note(f'cases_{which}_python', 2 * sweeps, comma(2 * sweeps),
             f'{which} cases: matrix on T1, T2, T5 and L1, each run by two laws in the Python version')
    for v in ('hertzforge', 'python'):
        r = json.load(open(os.path.join(runs, 'rescore', f'report_{v}.json')))
        r = {k: len(x) if isinstance(x, list) else x for k, x in r.items()}
        for k in ('equal', 'new', 'differs'):
            note(f'rescore_{v}_{k}', r[k], comma(r[k]), f'rescore/report_{v}.json')
        n = r['equal'] + r['new'] + r['differs'] + r['error']
        note(f'rescore_{v}_n', n, comma(n), f'rescore/report_{v}.json')
    reps = glob.glob(os.path.join(runs, 'study_repeat_*'))
    note('repeat_sets', len(reps), f'{len(reps)}', 'study_repeat_* folders')


def constants_part(problems, runs, adir):
    """The suite's fixed values, read from its own code as shipped in a problem folder, and the
    run settings and the pipeline as the run files record them."""
    import importlib.util
    folder = os.path.join(problems, 'frame-12x6-realistic_s00')
    spec = importlib.util.spec_from_file_location('sine_model_shipped', os.path.join(folder, 'sine_model.py'))
    sm = importlib.util.module_from_spec(spec)
    sys.path.insert(0, folder)
    spec.loader.exec_module(sm)
    sys.path.pop(0)
    src = 'sine_model.py of the problem folder'
    note('grid_per_octave', sm.REF_PER_OCTAVE, f'{sm.REF_PER_OCTAVE}', src)
    note('size_per_octave', sm.SIZE_PER_OCTAVE, f'{sm.SIZE_PER_OCTAVE:,}', src)
    note('tikhonov', sm.LAM_REL, '1e-3', src)
    note('headroom_db', sm.DRIVE_HEADROOM_DB, f'{sm.DRIVE_HEADROOM_DB:.0f}', src)
    note('ceiling_v', 10 ** (sm.DRIVE_HEADROOM_DB / 20), f'{10 ** (sm.DRIVE_HEADROOM_DB / 20):.2f}', src)
    note('engine_v', sm.ENGINE_MAX_DRIVE_VPK, f'{sm.ENGINE_MAX_DRIVE_VPK:.0f}', src)
    note('engine_controls', sm.ENGINE_MAX_CONTROLS, f'{sm.ENGINE_MAX_CONTROLS}', src)
    note('engine_drives', sm.ENGINE_MAX_DRIVES, f'{sm.ENGINE_MAX_DRIVES}', src)
    note('step_settle_tau', sm.STEP_SETTLE_TAU, f'{sm.STEP_SETTLE_TAU:.0f}', src)
    note('step_judge_tau', sm.STEP_JUDGE_TAU, f'{sm.STEP_JUDGE_TAU:.0f}', src)
    note('step_tau', sm.STEP_SETTLE_TAU + sm.STEP_JUDGE_TAU, f'{sm.STEP_SETTLE_TAU + sm.STEP_JUDGE_TAU:.0f}', src)
    note('step_min_cycles', sm.STEP_MIN_CYCLES, f'{sm.STEP_MIN_CYCLES}', src)
    note('dwell_settle_tau', sm.DWELL_SETTLE_TAU, f'{sm.DWELL_SETTLE_TAU:.0f}', src)
    note('dwell_tau', sm.DWELL_SETTLE_TAU + sm.DWELL_JUDGE_TAU, f'{sm.DWELL_SETTLE_TAU + sm.DWELL_JUDGE_TAU:.0f}', src)
    note('dwell_min_s', sm.DWELL_MIN_S, f'{sm.DWELL_MIN_S:.0f}', src)
    note('ratio_points', sm.R_GRID.size, f'{sm.R_GRID.size:,}', src)
    note('ratio_lo', sm.R_GRID[0], '1e-5', src)
    note('ratio_hi', sm.R_GRID[-1], '1e3', src)
    tol = sm.TOL
    note('tol_check_lo', 1 - tol['iec_check_point']['below_500'][0], pct(1 - tol['iec_check_point']['below_500'][0]), src)
    note('tol_check_hi', 1 - tol['iec_check_point']['above_500'][0], pct(1 - tol['iec_check_point']['above_500'][0]), src)
    note('tol_split_hz', 500, '500', src + ' (keys below_500, above_500)')
    note('tol_ref', 1 - tol['iec_reference_point']['all'][0], pct(1 - tol['iec_reference_point']['all'][0]), src)
    note('tol_mil', 1 - tol['mil_composite']['all'][0], pct(1 - tol['mil_composite']['all'][0]), src)
    note('tol_maxi_hi', tol['mil_maxi_individual']['below_500'][1] - 1,
         pct(tol['mil_maxi_individual']['below_500'][1] - 1), src)
    note('tol_rate', sm.RATE_TOL['fraction'], pct(sm.RATE_TOL['fraction']), src)
    note('tol_duration', sm.DURATION_TOL['fraction'], pct(sm.DURATION_TOL['fraction']), src)
    note('tol_freq_text', sm.FREQ_TOL['iec_sweep']['what'], '1 Hz from 5 to 50 Hz, 2 % above 50 Hz', src)
    note('tol_freq_fixed', 2, '2', src + " FREQ_TOL['iec_fixed']")
    note('tol_freq_mil', 0.1, '0.1', src + " FREQ_TOL['mil']")
    note('phase_analogy', sm.PHASE_ANALOGY_DEG, f'{sm.PHASE_ANALOGY_DEG:.0f}', src)
    note('g0', sm.G0, f'{sm.G0}', src)
    # Run settings, as the run files record them
    rec = json.load(open(os.path.join(runs, 'study', 'frame-6x6-realistic_s00', 'T1__matrix', 'run.json')))
    st = rec['settings']
    note('abort_db', st['abort_db'], f"{st['abort_db']:.0f}", 'study run.json settings')
    note('abort_ticks', st['abort_ticks'], f"{st['abort_ticks']}", 'study run.json settings')
    note('divergence_s', st['divergence_s'], f"{st['divergence_s']:.0f}", 'study run.json settings')
    note('max_step_db', st['max_step_db'], f"{st['max_step_db']:.0f}", 'study run.json settings')
    note('ceiling_exact', st['ceiling_vpk'][0], f"{st['ceiling_vpk'][0]}", 'study run.json settings')
    note('abort_vpk', st['abort_vpk'][0], f"{st['abort_vpk'][0]:.0f}", 'study run.json settings')
    note('id_lines_hz', rec['identification']['line_spacing_hz'], f"{rec['identification']['line_spacing_hz']}",
         'study run.json identification')
    note('frames_ahead', rec['identification']['frames_ahead'], f"{rec['identification']['frames_ahead']}",
         'study run.json identification')
    d = json.load(open(os.path.join(runs, 'study_defaults', 'frame-6x6-realistic_s00', 'T1__matrix', 'run.json')))
    sd = d['settings']
    note('default_abort_db', sd['abort_db'], f"{sd['abort_db']:.0f}", 'study_defaults run.json settings')
    note('default_abort_ticks', sd['abort_ticks'], f"{sd['abort_ticks']}", 'study_defaults run.json settings')
    note('default_divergence_s', sd['divergence_s'], f"{sd['divergence_s']:.0f}", 'study_defaults run.json settings')
    note('default_ceiling', sd['ceiling_vpk'][0], f"{sd['ceiling_vpk'][0]:.0f}", 'study_defaults run.json settings')
    py = json.load(open(os.path.join(runs, 'study_py', 'frame-6x6-realistic_s00', 'T1__matrix', 'run.json')))
    pipe = py['identification']['pipeline']
    note('pipeline_frames', pipe['pipeline_frames'], f"{pipe['pipeline_frames']}", 'study_py run.json pipeline')
    note('sim_block', pipe['pipeline_frames'] - rec['identification']['frames_ahead'],
         f"{pipe['pipeline_frames'] - rec['identification']['frames_ahead']}", 'pipeline less frames ahead')
    note('pipeline_ms', pipe['pipeline_frames'] / sm.FS * 1000, f"{pipe['pipeline_frames'] / sm.FS * 1000:.1f}",
         'pipeline frames over fs')
    lag = json.load(open(os.path.join(adir, 'lag_check_output.json')))
    same = sum(r['runner'] == r['restated'] for r in lag)
    note('lag_same', same, f'{same}', 'lag_check_output.json')
    note('lag_n', len(lag), f'{len(lag)}', 'lag_check_output.json')


def main():
    runs, problems, heldout, adir = sys.argv[1:5]
    assert 'audit_runs' not in os.path.abspath(runs)
    os.makedirs(DATA, exist_ok=True)
    problems_part(problems, heldout)
    cases_part(problems, heldout, runs)
    constants_part(problems, runs, adir)
    example_part(problems)
    schedules_part(problems)
    readings = readings_part(os.path.join(runs, 'claims'))
    claims = claims_part(os.path.join(runs, 'claims'))
    effects_summary(claims, readings)
    agreement_part(adir)
    rows = sets_part(runs, readings)
    repeats_summary(rows)
    write('numbers.csv', ['key', 'value', 'text', 'source'],
          [{**n, 'value': json.dumps(n['value']) if isinstance(n['value'], list) else n['value']}
           for n in NUMBERS])


if __name__ == '__main__':
    main()
