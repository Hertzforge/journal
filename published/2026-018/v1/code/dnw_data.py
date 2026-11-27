"""Write every file in ../data and every number the article quotes (../data/numbers.csv) from the
record of the MIMO Sine benchmark: the problems, the two screens' run tables and run files, the
study's cards and claims, the modal-fit records and the record's markdown files. Reads only; writes
only ../data. Copyright 2026 Kevin Cross. MIT license.

    python dnw_data.py --effort <MIMO_Sine_Benchmark> --research <MIMO_Sine> \
        --problems <problems> --g-runs <g_screen/runs> --j-runs <j_predictive/runs> \
        --study <study_runs> --fits <modal-fit out/C>

Nothing under the audit's run folder is read: the study folder is read only for its `study` set and
its claims file.
"""
import argparse
import csv
import glob
import json
import math
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
NUMBERS = []          # key, text, value, source, how
SYSTEMS = ['frame-6x6', 'frame-12x6']
TIERS = ['linear', 'realistic', 'strong']
SEEDS = [0, 1, 2]
# The record names the candidate laws by the effort's codes (its run tables, run folders, claims and
# notes); the data files and the article use their names. ../data/README.md maps the two.
RECORD_ARM = {'k2f': 'family_inverse', 'k3': 'followed_poles', 'k3_m9d': 'followed_poles_m9d',
              'k4': 'level_ladder', 'k4_sw': 'level_ladder_sw', 'k5': 'rls_dither',
              'j1': 'pole_trajectory', 'j2': 'amplitude_indexed', 'j3': 'placed_poles', 'j4': 'preview',
              'j4f': 'preview_frozen'}
ARM_CODE = {v: k for k, v in RECORD_ARM.items()}
LEADS = ['pole_trajectory', 'amplitude_indexed', 'placed_poles', 'preview']   # preview_frozen is a control run


def arm_id(arm):
    return RECORD_ARM.get(arm, arm)


def arm_code(arm):
    return ARM_CODE.get(arm, arm)


def add(key, value, source, how='', fmt=None):
    """One number of the text. `fmt` is a format spec for the text; the raw value is kept beside."""
    if any(k == key for k, *_ in NUMBERS):
        sys.exit(f'duplicate key {key}')
    if value is None:
        sys.exit(f'no value for {key}')
    if fmt is None:
        text = f'{value:,}' if isinstance(value, int) and abs(value) >= 10000 else str(value)
    elif fmt == 'signed1':
        text = f'{value:+.1f}'
    elif fmt == 'signed2':
        text = f'{value:+.2f}'
    elif fmt == 'pct0':
        text = f'{100 * value:.0f}'
    elif fmt == 'pct1':
        text = f'{100 * value:.1f}'
    else:
        text = format(value, fmt)
    NUMBERS.append([key, text, value, source, how])


def write(name, header, rows):
    with open(os.path.join(DATA, name), 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(header)
        w.writerows(rows)


def grab(path, pattern, what, group=1, flags=0):
    text = open(path).read()
    m = re.search(pattern, text, flags)
    if not m:
        sys.exit(f'not found in {os.path.basename(path)}: {what}')
    return m.group(group)


def problem_id(system, tier, seed):
    return f'{system}{"" if tier == "linear" else "-" + tier}_s{seed:02d}'


def fnum(x):
    return None if x in ('', None) else float(x)


def median(xs):
    xs = [x for x in xs if x is not None]
    return st.median(xs) if xs else None


# ------------------------------------------------------------------------------------------------
# 1. How far the screen structures' modes move at full level, in half-power bandwidths.
def mode_shift(problems):
    rows, per = [], {}
    for system in SYSTEMS:
        for tier in ('realistic', 'strong'):
            for seed in SEEDS:
                pid = problem_id(system, tier, seed)
                s = json.load(open(os.path.join(problems, pid, 'structure.json')))
                p = json.load(open(os.path.join(problems, pid, 'problem.json')))
                fc = s['level_targets']['frequency_change']
                df = s['level_targets']['damping_factor']
                lo, hi = p['band_hz']
                shifts, changes, dfs, wide = [], [], [], []
                for i, m in enumerate(s['modes']):
                    if i < s['rigid_modes'] or not lo <= m['f_hz'] <= hi:
                        continue
                    bw = abs(fc[i]) / (2 * m['zeta'])
                    shifts.append(bw)
                    dfs.append(df[i])
                    wide.append(bw / df[i])
                    changes.append(abs(fc[i]))
                    rows.append([pid, system, tier, seed, round(m['f_hz'], 3), round(m['zeta'], 6),
                                 round(fc[i], 6), round(df[i], 4), round(bw, 4)])
                sine = p['checks']['state']['full_level']['median_abs_change']
                per[pid] = dict(tier=tier, shifts=shifts, dfs=dfs, wide=wide, med=st.median(shifts),
                                over1=sum(x > 1 for x in shifts) / len(shifts),
                                random_med=st.median(changes), sine_med=sine,
                                zeta=st.median(s['modes'][i]['zeta'] for i in range(len(s['modes']))
                                               if i >= s['rigid_modes']
                                               and lo <= s['modes'][i]['f_hz'] <= hi))
    write('fig1_mode_shift.csv', ['problem', 'system', 'tier', 'structure', 'f_hz', 'zeta',
                                  'frequency_change_at_full_level', 'damping_factor_at_full_level',
                                  'shift_in_bandwidths'], rows)
    src = 'data/fig1_mode_shift.csv (problems: structure.json level_targets, modes)'
    for tier in ('realistic', 'strong'):
        ps = [v for v in per.values() if v['tier'] == tier]
        meds = sorted(v['med'] for v in ps)
        pooled = [x for v in ps for x in v['shifts']]
        add(f'shift_{tier}_med_lo', meds[0], src, 'lowest structure median, bandwidths', '.1f')
        add(f'shift_{tier}_med_hi', meds[-1], src, 'highest structure median', '.1f')
        add(f'shift_{tier}_over1_pct', sum(x > 1 for x in pooled) / len(pooled), src,
            'pooled share of modes over one bandwidth', 'pct0')
        add(f'shift_{tier}_over025_pct', sum(x > 0.25 for x in pooled) / len(pooled), src,
            'pooled share over a quarter bandwidth', 'pct0')
        add(f'shift_{tier}_max', max(pooled), src, 'largest, bandwidths', '.1f')
        add(f'shift_{tier}_modes', len(pooled), src, 'modes in band, six structures')
        dfs = [x for v in ps for x in v['dfs']]
        add(f'damping_{tier}_med', st.median(dfs), src, 'median damping factor at full level', '.1f')
        wide = [x for v in ps for x in v['wide']]
        add(f'shift_{tier}_wide_med', st.median(wide), src,
            'pooled median shift in the full-level bandwidth (damping grown)', '.2f')
        add(f'shift_{tier}_wide_over1_pct', sum(x > 1 for x in wide) / len(wide), src, '', 'pct0')
        add(f'change_{tier}_med_lo', min(v['random_med'] for v in ps), src,
            'median frequency change, lowest structure, percent', 'pct1')
        add(f'change_{tier}_med_hi', max(v['random_med'] for v in ps), src, '', 'pct1')
    gap = max(abs(v['random_med'] - v['sine_med']) for v in per.values())
    add('sine_random_median_gap', gap, src + ' and problem.json checks.state.full_level',
        'largest difference, sine and Random median change', '.1e')
    zetas = [v['zeta'] for v in per.values()]
    add('zeta_med_lo', min(zetas), src, 'median damping ratio, lowest structure', 'pct1')
    add('zeta_med_hi', max(zetas), src, '', 'pct1')
    # The time a log sweep spends inside a half-power bandwidth: 60 / (Q s ln 2) s (the record's
    # derivation), at the median Q of the screen's modes.
    q = 1 / (2 * st.median(zetas))
    add('q_median', q, src, 'Q at the median damping ratio', '.0f')
    t1 = json.load(open(os.path.join(problems, 'frame-6x6_s00', 'test_T1.json')))
    lad = t1['ladder']
    add('ladder_start', lad['table_db'][0], 'problems: test_T1.json ladder', 'dB', 'g')
    add('ladder_step', lad['table_db'][1] - lad['table_db'][0], 'problems: test_T1.json ladder', 'dB', 'g')
    add('ladder_rungs', len(lad['table_db']), 'problems: test_T1.json ladder')
    add('rung_s', lad['per_rung']['seconds'], 'problems: test_T1.json ladder', 's', 'g')
    add('sysid_db', lad['sysid_level_db'], 'problems: test_T1.json ladder', 'dB', 'g')
    add('noise_pct', t1['noise']['relative'], 'problems: test_T1.json noise', 'percent of the full-level amplitude', 'pct1')
    add('band_lo', t1['band_hz'][0], 'problems: test_T1.json', 'Hz', 'g')
    add('band_hi', t1['band_hz'][1], 'problems: test_T1.json', 'Hz', 'g')
    add('t3_per_octave', json.load(open(os.path.join(problems, 'frame-6x6_s00', 'test_T3.json')))['steps_per_octave'],
        'problems: test_T3.json')
    for t in ('T1', 'T2'):
        add(f'rate_{t}', json.load(open(os.path.join(problems, 'frame-6x6_s00', f'test_{t}.json')))['rate_oct_per_min'],
            'problems: test_T1.json, test_T2.json', 'octaves a minute', 'g')
    for rate in (1, 4):
        add(f'bw_seconds_{rate}', 60 / (q * rate * math.log(2)), 'computed: 60 / (Q s ln 2)',
            f'seconds in a bandwidth at {rate} octaves a minute', '.1f')
    return per


# ------------------------------------------------------------------------------------------------
# 2. The screens' run tables, read run by run.
def read_runs(path):
    out = {}
    for r in csv.DictReader(open(path)):
        seed = int(r['problem'].rsplit('_s', 1)[1])
        out[(arm_id(r['arm']), r['test'], r['tier'], r['problem'])] = dict(
            completed=r['completed'] == 'True', scored=r['scored'] == 'True',
            ends=r['ends_in_tol'] == 'True', p95=fnum(r['p95']), over=fnum(r['over_test']),
            iec=fnum(r['iec_share']), coverage=fnum(r['coverage']), at_hz=fnum(r['at_hz']),
            level=fnum(r['at_level_db']), clock=fnum(r['clock_s']), seed=seed,
            problem=r['problem'], outcome=r['outcome'])
    return out


def cell(runs, arm, test, tier):
    return {k[3]: v for k, v in runs.items() if k[:3] == (arm, test, tier)}


def paired(a, b):
    """Paired readings of arm a against yardstick b over the same structures."""
    both = [p for p in a if p in b and a[p]['scored'] and b[p]['scored']]
    def diff(f):
        return [a[p][f] - b[p][f] for p in both if a[p][f] is not None and b[p][f] is not None]
    d95, dov, diec = diff('p95'), diff('over'), diff('iec')
    return dict(
        runs=len(a), completed=sum(v['completed'] for v in a.values()),
        completed_yard=sum(b[p]['completed'] for p in a),
        gained=sum(a[p]['completed'] and not b[p]['completed'] for p in a),
        lost=sum(b[p]['completed'] and not a[p]['completed'] for p in a),
        ends=sum(v['ends'] for v in a.values()), ends_yard=sum(b[p]['ends'] for p in a),
        n=len(d95), p95_lower=sum(x < 0 for x in d95), p95_med=median(d95),
        over_med=median(dov), over_higher=sum(x > 0 for x in dov), iec_med=median(diec),
        iec_higher=sum(x > 0 for x in diec),
        med_p95=median(v['p95'] for v in a.values() if v['scored']),
        med_over=median(v['over'] for v in a.values() if v['scored']))


def rule_j(c):
    """The second screen's rule on one cell (J_Screen.md section 2)."""
    return (c['completed'] > c['completed_yard'] and c['p95_lower'] >= 4
            and c['over_med'] is not None and c['over_med'] <= 1.0)


def screens(effort):
    g_runs = read_runs(os.path.join(effort, 'experiments', 'G', 'screen_runs.csv'))
    j_runs = read_runs(os.path.join(effort, 'experiments', 'J', 'screen_runs.csv'))
    g_json = json.load(open(os.path.join(effort, 'experiments', 'G', 'screen_report_output.json')))
    j_json = json.load(open(os.path.join(effort, 'experiments', 'J', 'screen_report_output.json')))
    gsrc = 'experiments/G/screen_runs.csv'
    jsrc = 'experiments/J/screen_runs.csv'
    add('g_runs', len(g_runs), gsrc, 'runs in the first screen')
    nl = sorted({k[3] for k in g_runs if k[2] != 'linear'})
    add('screen_structures', len(nl), gsrc, 'nonlinear structures in the screens')
    add('screen_linear', len({k[3] for k in g_runs if k[2] == 'linear'}), gsrc, 'linear structures, the control')
    add('screen_per_cell', len({k[3] for k in g_runs if (k[1], k[2]) == ('T1', 'realistic')}), gsrc,
        'structures on one test and tier')
    add('screen_structures_each', len({int(p.rsplit('_s', 1)[1]) for p in nl}), gsrc,
        'structures of each system and tier')
    add('leads', len({k[0] for k in j_runs if k[0] in LEADS}), jsrc)
    add('j_runs', sum(1 for k in j_runs if k[0] not in ('matrix', 'followed_poles')), jsrc,
        'runs in the second screen, the yardsticks apart')
    add('g_hours', grab(os.path.join(effort, 'G_Screen.md'), r'\*\*(\d+(?:\.\d+)?) runner-hours\*\*', 'G hours'),
        'G_Screen.md 4.1')
    add('j_hours', grab(os.path.join(effort, 'J_Screen.md'), r'(\d+(?:\.\d+)?) runner-hours, median', 'J hours'),
        'J_Screen.md 4')
    rows = []
    # The first screen: each candidate against its yardstick.
    g_arms = [('family_inverse', 'matrix', ['T1', 'T2', 'T3', 'T5']), ('level_ladder', 'matrix', ['T1', 'T5']),
              ('level_ladder_sw', 'matrix_sw', ['T1', 'T5']), ('rls_dither', 'matrix', ['T4']),
              ('followed_poles', 'matrix', ['T1', 'T2', 'T5'])]
    G = {}
    for arm, yard, tests in g_arms:
        for test in tests:
            for tier in TIERS:
                c = paired(cell(g_runs, arm, test, tier), cell(g_runs, yard, test, tier))
                G[(arm, test, tier)] = c
                ref = g_json['rule'].get(f'{arm_code(arm)}|{test}|{tier}')
                if ref and (ref['completed'] != c['completed'] or ref['completed_yard'] != c['completed_yard']
                            or (c['over_med'] is not None and abs(ref['paired']['over_test']['median'] - c['over_med']) > 0.006)):
                    sys.exit(f'G cross-check failed on {arm} {test} {tier}')
                rows.append(['G', arm, yard, test, tier, c['runs'], c['completed'], c['completed_yard'],
                             c['gained'], c['lost'], c['ends'], c['ends_yard'], c['n'], c['p95_lower'],
                             r3(c['p95_med']), r3(c['over_med']), c['over_higher'], r3(c['iec_med']),
                             r3(c['med_p95']), r3(c['med_over']), ''])
    # The yardsticks' own cells, for the figures.
    for arm in ('matrix', 'matrix_sw'):
        for test in ('T1', 'T2', 'T3', 'T4', 'T5'):
            for tier in TIERS:
                a = cell(g_runs, arm, test, tier)
                if a:
                    c = paired(a, a)
                    rows.append(['G', arm, '', test, tier, c['runs'], c['completed'], '', '', '', c['ends'],
                                 '', '', '', '', '', '', '', r3(c['med_p95']), r3(c['med_over']), ''])
    # The second screen: each lead against matrix and against followed poles.
    J = {}
    for arm in ('pole_trajectory', 'amplitude_indexed', 'placed_poles', 'preview', 'preview_frozen'):
        for yard in ('matrix', 'followed_poles'):
            for test in ('T1', 'T2', 'T5'):
                for tier in TIERS:
                    c = paired(cell(j_runs, arm, test, tier), cell(j_runs, yard, test, tier))
                    c['passes'] = tier != 'linear' and rule_j(c)
                    J[(arm, yard, test, tier)] = c
                    ref = j_json['rule'].get(f'{arm_code(arm)}|{test}|{tier}|{arm_code(yard)}')
                    if ref and ref.get('passes') is not None and tier != 'linear' and bool(ref['passes']) != c['passes']:
                        sys.exit(f'J cross-check failed on {arm} {yard} {test} {tier}')
                    rows.append(['J', arm, yard, test, tier, c['runs'], c['completed'], c['completed_yard'],
                                 c['gained'], c['lost'], c['ends'], c['ends_yard'], c['n'], c['p95_lower'],
                                 r3(c['p95_med']), r3(c['over_med']), c['over_higher'], r3(c['iec_med']),
                                 r3(c['med_p95']), r3(c['med_over']), int(c['passes'])])
    write('screen_cells.csv', ['screen', 'arm', 'yardstick', 'test', 'tier', 'runs', 'completed',
                               'completed_yardstick', 'gained', 'lost', 'ends_in_tolerance',
                               'ends_in_tolerance_yardstick', 'pairs_scored', 'p95_lower_on',
                               'p95_paired_median_db', 'over_test_paired_median_db', 'over_test_higher_on',
                               'iec_share_paired_median', 'median_p95_db', 'median_over_test_db',
                               'passes_second_rule'], rows)
    return g_runs, j_runs, G, J


def r3(x):
    return '' if x is None else round(x, 3)


def screen_numbers(g_runs, j_runs, G, J):
    s = 'data/screen_cells.csv'
    nl = ('realistic', 'strong')

    def tot(d, arm, tests, tiers, field, yard=None):
        if yard:
            return sum(d[(arm, yard, t, r)][field] for t in tests for r in tiers)
        return sum(d[(arm, t, r)][field] for t in tests for r in tiers)

    # Every sweep and stepped sine of the first screen: runs ending in tolerance.
    ends = sum(v['ends'] for k, v in g_runs.items() if k[1] in ('T1', 'T2', 'T3', 'T5'))
    ends_runs = sum(1 for k in g_runs if k[1] in ('T1', 'T2', 'T3', 'T5'))
    ends_nonlin = sum(v['ends'] for k, v in g_runs.items()
                      if k[1] in ('T1', 'T2', 'T3', 'T5') and k[2] != 'linear')
    add('g_sweepstep_runs', ends_runs, s, 'sweeps and stepped sines, every arm and tier')
    add('g_sweepstep_ends', ends, s, 'of them, ending in tolerance')
    add('g_sweepstep_ends_nonlinear', ends_nonlin, s, 'on the realistic and strong tiers')
    m3 = paired(cell(g_runs, 'matrix', 'T3', 'linear'), cell(g_runs, 'matrix', 'T3', 'linear'))
    add('g_matrix_t3_linear_ends', m3['ends'], s, 'matrix T3 linear ends in tolerance')
    dw = {tier: paired(cell(g_runs, 'matrix', 'T4', tier), cell(g_runs, 'matrix', 'T4', tier))['ends']
          for tier in TIERS}
    for tier in TIERS:
        add(f'g_matrix_t4_{tier}_ends', dw[tier], s, 'matrix dwells ending in tolerance')
    # The family inverse.
    for tier in TIERS:
        add(f'family_inverse_{tier}_completed', tot(G, 'family_inverse', ['T1', 'T2', 'T3', 'T5'], [tier], 'completed'), s)
        add(f'family_inverse_{tier}_completed_yard', tot(G, 'family_inverse', ['T1', 'T2', 'T3', 'T5'], [tier], 'completed_yard'), s)
        add(f'family_inverse_{tier}_runs', tot(G, 'family_inverse', ['T1', 'T2', 'T3', 'T5'], [tier], 'runs'), s)
    lin = [G[('family_inverse', t, 'linear')]['over_med'] for t in ('T1', 'T2', 'T3', 'T5')]
    add('family_inverse_linear_over_lo', min(lin), s, 'paired median over-test, linear cells', '.1f')
    add('family_inverse_linear_over_hi', max(lin), s, '', '.1f')
    lin95 = [G[('family_inverse', t, 'linear')]['p95_med'] for t in ('T1', 'T2', 'T3', 'T5')]
    add('family_inverse_linear_p95_lo', min(lin95), s, 'paired median p95, linear cells', '.1f')
    add('family_inverse_linear_p95_hi', max(lin95), s, '', '.1f')
    for t in ('T1', 'T2', 'T3', 'T5'):
        add(f'family_inverse_{t}_linear_completed', G[('family_inverse', t, 'linear')]['completed'], s)
        add(f'family_inverse_{t}_linear_completed_yard', G[('family_inverse', t, 'linear')]['completed_yard'], s)
    for t in ('T2', 'T3'):
        c = G[('family_inverse', t, 'strong')]
        add(f'family_inverse_{t}_strong_completed', c['completed'], s)
        add(f'family_inverse_{t}_strong_completed_yard', c['completed_yard'], s)
        add(f'family_inverse_{t}_strong_over', c['over_med'], s, '', '.2f')
    for t in ('T1', 'T2'):
        c = G[('family_inverse', t, 'realistic')]
        add(f'family_inverse_{t}_realistic_completed', c['completed'], s)
        add(f'family_inverse_{t}_realistic_completed_yard', c['completed_yard'], s)
        add(f'family_inverse_{t}_realistic_over', c['over_med'], s, '', '.1f')
    for t in ('T3', 'T5'):
        add(f'family_inverse_{t}_realistic_over', G[('family_inverse', t, 'realistic')]['over_med'], s, '', '.1f')
    for t in ('T1', 'T5'):
        add(f'family_inverse_{t}_strong_over', G[('family_inverse', t, 'strong')]['over_med'], s, '', '.1f')
    nlp = [G[('family_inverse', t, r)] for t in ('T1', 'T2', 'T3', 'T5') for r in nl]
    add('family_inverse_nl_p95_lower', sum(c['p95_lower'] for c in nlp), s, 'nonlinear pairs with lower p95')
    add('family_inverse_nl_pairs', sum(c['n'] for c in nlp), s)
    # The level ladder on the short rungs.
    for t in ('T1', 'T5'):
        for r in nl:
            c = G[('level_ladder', t, r)]
            add(f'level_ladder_{t}_{r}_completed', c['completed'], s)
            add(f'level_ladder_{t}_{r}_completed_yard', c['completed_yard'], s)
            add(f'level_ladder_{t}_{r}_p95', c['p95_med'], s, '', '+.1f')
            add(f'level_ladder_{t}_{r}_iec_pts', 100 * c['iec_med'], s, 'paired median IEC share, points', '+.0f')
    ll_lin = [G[('level_ladder', t, 'linear')] for t in ('T1', 'T5')]
    add('level_ladder_linear_p95_lower', sum(c['p95_lower'] for c in ll_lin), s)
    add('level_ladder_linear_pairs', sum(c['n'] for c in ll_lin), s)
    # The level ladder on whole-sweep rungs: where its runs stopped.
    stops = [v for k, v in g_runs.items() if k[0] == 'level_ladder_sw' and k[2] in nl]
    mstops = [v for k, v in g_runs.items() if k[0] == 'matrix_sw' and k[2] in nl]
    add('level_ladder_sw_nl_runs', len(stops), gsrc_runs())
    add('level_ladder_sw_nl_below_full', sum(1 for v in stops if not v['completed'] and v['level'] is not None and v['level'] < 0),
        gsrc_runs(), 'stopped on a pass below full level')
    add('level_ladder_sw_nl_at_m12', sum(1 for v in stops if v['level'] == -12.0), gsrc_runs())
    add('level_ladder_sw_nl_at_m9', sum(1 for v in stops if v['level'] == -9.0), gsrc_runs())
    add('mxsw_nl_below_full', sum(1 for v in mstops if not v['completed'] and v['level'] is not None and v['level'] < 0),
        gsrc_runs(), 'matrix on the same rungs')
    add('mxsw_nl_completed', sum(v['completed'] for v in mstops), gsrc_runs())
    add('mxsw_nl_runs', len(mstops), gsrc_runs())
    for t in ('T1', 'T5'):
        c = G[('level_ladder_sw', t, 'linear')]
        add(f'level_ladder_sw_{t}_linear_completed', c['completed'], s)
        add(f'level_ladder_sw_{t}_linear_completed_yard', c['completed_yard'], s)
    write('fig3_whole_sweep_stops.csv', ['arm', 'test', 'tier', 'problem', 'outcome', 'stopped_at_level_db',
                                         'stopped_at_hz'],
          [[k[0], k[1], k[2], k[3], v['outcome'], v['level'], r3(v['at_hz'])]
           for k, v in sorted(g_runs.items()) if k[0] in ('level_ladder_sw', 'matrix_sw')])
    # The dither identification at the dwell.
    rd = [G[('rls_dither', 'T4', r)] for r in TIERS]
    add('rls_dither_completed', sum(c['completed'] for c in rd), s)
    add('rls_dither_runs', sum(c['runs'] for c in rd), s)
    add('rls_dither_completed_yard', sum(c['completed_yard'] for c in rd), s)
    for r in TIERS:
        c = G[('rls_dither', 'T4', r)]
        add(f'rls_dither_{r}_ends', c['ends'], s)
        add(f'rls_dither_{r}_ends_yard', c['ends_yard'], s)
    add('rls_dither_over_higher', sum(c['over_higher'] for c in rd), s, 'pairs with higher worst over-test')
    add('rls_dither_pairs', sum(c['n'] for c in rd), s)
    add('rls_dither_over_lo', min(c['over_med'] for c in rd), s, '', '.2f')
    add('rls_dither_over_hi', max(c['over_med'] for c in rd), s, '', '.2f')
    # Followed poles on the first screen, for the yardstick section.
    fp = [G[('followed_poles', t, r)] for t in ('T1', 'T2', 'T5') for r in nl]
    add('followed_poles_nl_completed', sum(c['completed'] for c in fp), s)
    add('followed_poles_nl_runs', sum(c['runs'] for c in fp), s)
    add('mx_nl_sweep_completed', sum(c['completed_yard'] for c in fp), s, 'matrix, the same sweeps')
    add('followed_poles_nl_p95_lower', sum(c['p95_lower'] for c in fp), s)
    add('followed_poles_nl_pairs', sum(c['n'] for c in fp), s)
    strong = [G[('followed_poles', t, 'strong')]['over_med'] for t in ('T1', 'T2', 'T5')]
    add('followed_poles_strong_over_lo', min(strong), s, 'paired median over-test, strong', '+.2f')
    add('followed_poles_strong_over_hi', max(strong), s, '', '+.2f')
    real = [G[('followed_poles', t, 'realistic')]['over_med'] for t in ('T1', 'T2', 'T5')]
    add('followed_poles_real_over_lo', min(real), s, 'paired median over-test, realistic', '+.2f')
    add('followed_poles_real_over_hi', max(real), s, '', '+.2f')
    fp_cells = sum(1 for t in ('T1', 'T2', 'T5') for r in nl if rule_j(G[('followed_poles', t, r)]))
    add('followed_poles_cells_vs_matrix', fp_cells, s, 'followed_poles by the second rule against matrix')
    # The leads.
    for arm in ('pole_trajectory', 'amplitude_indexed', 'placed_poles', 'preview', 'preview_frozen'):
        a = [J[(arm, 'followed_poles', t, r)] for t in ('T1', 'T2', 'T5') for r in nl]
        m = [J[(arm, 'matrix', t, r)] for t in ('T1', 'T2', 'T5') for r in nl]
        add(f'{arm}_completed', sum(c['completed'] for c in a), s, 'nonlinear sweeps completed')
        add(f'{arm}_gained', sum(c['gained'] for c in a), s, 'against followed_poles')
        add(f'{arm}_lost', sum(c['lost'] for c in a), s, 'against followed_poles')
        add(f'{arm}_p95_lower_followed_poles', sum(c['p95_lower'] for c in a), s)
        add(f'{arm}_pairs_followed_poles', sum(c['n'] for c in a), s)
        add(f'{arm}_p95_lower_mx', sum(c['p95_lower'] for c in m), s)
        add(f'{arm}_pairs_mx', sum(c['n'] for c in m), s)
        add(f'{arm}_cells_mx', sum(c['passes'] for c in m), s, 'cells passing against matrix')
        add(f'{arm}_cells_followed_poles', sum(c['passes'] for c in a), s, 'cells passing against followed_poles')
        lin = [J[(arm, 'followed_poles', t, 'linear')] for t in ('T1', 'T2', 'T5')]
        add(f'{arm}_linear_completed', sum(c['completed'] for c in lin), s)
        for t in ('T1', 'T2', 'T5'):
            add(f'{arm}_{t}_linear_p95', J[(arm, 'followed_poles', t, 'linear')]['p95_med'], s,
                'linear control, paired median p95 against followed_poles', '+.2f')
    lin3 = [J[(a, 'followed_poles', t, 'linear')] for a in ('pole_trajectory', 'amplitude_indexed', 'placed_poles') for t in ('T1', 'T2', 'T5')]
    add('first_three_leads_linear_p95_maxabs', max(abs(c['p95_med']) for c in lin3), s,
        'largest absolute linear paired median p95 against followed_poles: pole_trajectory, '
        'amplitude_indexed and placed_poles', '.2f')
    if len({sum(J[(a, 'followed_poles', t, 'linear')]['completed'] for t in ('T1', 'T2', 'T5'))
            for a in ('pole_trajectory', 'amplitude_indexed', 'placed_poles')} | {sum(J[('pole_trajectory', 'followed_poles', t, 'linear')]['completed_yard']
                                              for t in ('T1', 'T2', 'T5'))}) != 1:
        sys.exit('the first three leads and followed_poles do not all complete the same linear sweeps')
    add('lead_runs_nl', sum(J[('pole_trajectory', 'followed_poles', t, r)]['runs'] for t in ('T1', 'T2', 'T5') for r in nl), s)
    add('followed_poles_j_completed', sum(J[('pole_trajectory', 'followed_poles', t, r)]['completed_yard'] for t in ('T1', 'T2', 'T5') for r in nl), s)
    add('mx_j_completed', sum(J[('pole_trajectory', 'matrix', t, r)]['completed_yard'] for t in ('T1', 'T2', 'T5') for r in nl), s)
    c = J[('amplitude_indexed', 'followed_poles', 'T5', 'realistic')]
    add('amplitude_indexed_t5r_over_followed_poles', c['over_med'], s, '', '.1f')
    add('amplitude_indexed_t5r_over_mx', J[('amplitude_indexed', 'matrix', 'T5', 'realistic')]['over_med'], s, '', '.1f')
    c = J[('placed_poles', 'followed_poles', 'T2', 'strong')]
    add('placed_poles_t2s_completed', c['completed'], s)
    add('placed_poles_t2s_completed_followed_poles', c['completed_yard'], s)
    add('placed_poles_t2s_p95_lower', c['p95_lower'], s)
    add('placed_poles_t2s_n', c['n'], s)
    add('placed_poles_t2s_over', c['over_med'], s, '', '+.2f')
    fields = ['arm', 'yardstick', 'test', 'tier', 'completed', 'completed_yardstick', 'p95_paired_median_db',
              'over_test_paired_median_db', 'passes']
    write('fig4_leads.csv', fields,
          [[k[0], k[1], k[2], k[3], v['completed'], v['completed_yard'], r3(v['p95_med']),
            r3(v['over_med']), int(v['passes'])] for k, v in sorted(J.items())])


def gsrc_runs():
    return 'data/fig3_whole_sweep_stops.csv (experiments/G/screen_runs.csv)'


# ------------------------------------------------------------------------------------------------
# 3. Traces from run files: the worst control error along a sweep.
def worst_trace(path, full_only=True):
    h = json.load(open(path))['history']
    out = []
    for i in range(h['points']):
        if full_only and h['level_db'][i] != 0.0:
            continue
        lo, hi = h['bin_error_db_min'][i], h['bin_error_db_max'][i]
        vals = [abs(x) for x in (lo or []) + (hi or []) if x is not None]
        if not vals:
            vals = [abs(x) for x in h['error_db'][i] if x is not None]
        if vals:
            out.append((h['time_s'][i], h['frequency_hz'][i], max(vals)))
    return out


WIN = (30, 50, 400)   # the start window of DNW-J4, and where the rest of the sweep is read from


def traces(g, j):
    rows = []
    pid = 'frame-6x6_s00'
    files = {arm: os.path.join(root, arm_code(arm), pid, 'T1', 'run.json') for arm, root in
             (('matrix', g), ('followed_poles', g), ('preview', j), ('preview_frozen', j))}
    band = {}
    for arm, path in files.items():
        tr = worst_trace(path)
        for t, f, e in tr:
            rows.append([arm, pid, 'T1', round(t, 4), round(f, 4), round(e, 4)])
        band[arm] = max(e for t, f, e in tr if WIN[0] <= f <= WIN[1])
        band[arm + '_above400'] = max(e for t, f, e in tr if f >= WIN[2])
    write('fig5_start_error.csv', ['arm', 'problem', 'test', 'time_s', 'frequency_hz',
                                   'worst_control_error_db'], rows)
    src = 'data/fig5_start_error.csv (run files, frame-6x6 structure 0, T1)'
    add('win_lo', WIN[0], 'dnw_data.py', 'the start window, Hz (the record names 30 to 50 Hz, DNW-J4)')
    add('win_hi', WIN[1], 'dnw_data.py', '')
    add('win_above', WIN[2], 'dnw_data.py', 'the upper part of the band read for comparison, Hz')
    for arm in ('followed_poles', 'preview', 'preview_frozen', 'matrix'):
        add(f'start_err_{arm}', band[arm], src, 'largest control error, 30 to 50 Hz, full level', '.1f')
        add(f'above400_err_{arm}', band[arm + '_above400'], src, 'largest control error above 400 Hz', '.1f')


# ------------------------------------------------------------------------------------------------
# 4. paired and ratio on the stepped sine: the study's cards, a trace, and the coupling.
def stepped(study, problems):
    rows = []
    for card in sorted(glob.glob(os.path.join(study, 'study', '*', 'T[34]__*', 'card.json'))):
        law = os.path.basename(os.path.dirname(card)).split('__')[1]
        test = os.path.basename(os.path.dirname(card)).split('__')[0]
        if law not in ('matrix', 'paired', 'ratio'):
            continue
        pid = os.path.basename(os.path.dirname(os.path.dirname(card)))
        c = json.load(open(card))
        system = pid.split('-')[1].split('_')[0]
        tier = pid.split('_')[0].split('-', 2)[2] if pid.count('-') >= 2 else 'linear'
        comp = c['completion']
        rows.append([pid, system, tier, test, law, comp['outcome'], comp.get('at_level_db'),
                     r3(comp.get('at_hz')), r3(comp.get('coverage'))])
    write('fig6_stepped_runs.csv', ['problem', 'system', 'kind', 'test', 'law', 'outcome',
                                    'ended_at_level_db', 'ended_at_hz', 'coverage'], rows)
    src = 'data/fig6_stepped_runs.csv (study cards, Hertzforge version)'
    for law in ('matrix', 'paired', 'ratio'):
        for test in ('T3', 'T4'):
            rs = [r for r in rows if r[4] == law and r[3] == test]
            add(f'{law}_{test}_runs', len(rs), src)
            add(f'{law}_{test}_completed', sum(r[5] == 'completed' for r in rs), src)
            add(f'{law}_{test}_completed_pct', sum(r[5] == 'completed' for r in rs) / len(rs), src, '', 'pct0')
        rs = [r for r in rows if r[4] == law and r[3] == 'T3']
        ab = [r for r in rs if r[5] == 'aborted']
        add(f'{law}_T3_aborted', len(ab), src)
        add(f'{law}_T3_aborted_m12', sum(r[6] == -12.0 for r in ab), src, 'aborts on the first rung')
        add(f'{law}_T3_aborted_full', sum(r[6] == 0.0 for r in ab), src, 'aborts at full level')
        full = [r[8] for r in ab if r[6] == 0.0 and r[8] != '']
        if full:
            add(f'{law}_T3_full_abort_cov_med', st.median(full), src,
                'median share of steps judged before an abort at full level', 'pct0')
        add(f'{law}_T3_held', sum(r[5] == 'held_by_identification' for r in rs), src)
        add(f'{law}_T3_aborted_mid', sum(r[6] in (-9.0, -6.0, -3.0) for r in ab), src, 'aborts on the middle rungs')
        lin = [r for r in rs if r[2] == 'linear']
        add(f'{law}_T3_linear_runs', len(lin), src)
        add(f'{law}_T3_linear_completed', sum(r[5] == 'completed' for r in lin), src)
        sq = [r for r in rs if r[1] in ('6x6', '12x12')]
        add(f'{law}_T3_square_runs', len(sq), src)
        add(f'{law}_T3_square_completed', sum(r[5] == 'completed' for r in sq), src)
    # A trace: worst control error at each judged step update, frame-6x6 structure 0 (linear).
    trows = []
    for law in ('matrix', 'paired', 'ratio'):
        h = json.load(open(os.path.join(study, 'study', 'frame-6x6_s00', f'T3__{law}', 'run.json')))['history']
        for i in range(h['points']):
            if h['level_db'][i] != 0.0:
                continue
            e = [abs(x) for x in h['error_db'][i] if x is not None]
            if e:
                trows.append([law, round(h['time_s'][i], 4), round(h['frequency_hz'][i], 4), round(max(e), 4),
                              int(bool(h['judged'][i]))])
    write('fig7_stepped_trace.csv', ['law', 'time_s', 'frequency_hz', 'worst_control_error_db', 'judged'], trows)
    for law in ('matrix', 'paired', 'ratio'):
        c = json.load(open(os.path.join(study, 'study', 'frame-6x6_s00', f'T3__{law}', 'card.json')))['completion']
        add(f'trace_{law}_outcome', c['outcome'], 'study card frame-6x6_s00 T3')
        if c['at_hz'] is not None:
            add(f'trace_{law}_at_hz', c['at_hz'], 'study card frame-6x6_s00 T3', '', '.0f')
    # The coupling of the square systems: each control's own shaker against the other shakers.
    sys.path.insert(0, os.path.join(problems, 'frame-6x6_s00'))
    import reference_model as rm  # the suite's own model code, read from the problem folder
    import numpy as np
    crows = []
    for pid in sorted(os.listdir(os.path.join(study, 'study'))):
        if not os.path.isdir(os.path.join(study, 'study', pid, 'T3__paired')):
            continue
        folder = os.path.join(problems, pid)
        s = rm.load_structure(os.path.join(folder, 'structure.json'))
        f = np.array(json.load(open(os.path.join(folder, 'test_T3.json')))['frequencies_hz'], float)
        H = np.abs(rm.frf(s, f, rows=s.rows('control')))      # (steps, controls, drives)
        k = min(H.shape[1], H.shape[2])                         # paired's pairs: control i, drive i
        own = np.stack([H[:, i, i] for i in range(k)], axis=1)
        row_sum = H[:, :k, :].sum(axis=2)
        row_max = H[:, :k, :].max(axis=2)
        system = pid.split('-')[1].split('_')[0]
        tier = pid.split('_')[0].split('-', 2)[2] if pid.count('-') >= 2 else 'linear'
        crows.append([pid, system, tier, H.shape[1], H.shape[2], len(f),
                      round(float(np.median(own / row_sum)), 4), round(float(np.mean(own >= row_max)), 4),
                      round(1 / H.shape[2], 4)])
    write('fig6_coupling.csv', ['problem', 'system', 'kind', 'controls', 'drives', 'steps',
                                'own_share_of_summed_paths_median', 'share_own_shaker_largest',
                                'one_over_drives'], crows)
    src = 'data/fig6_coupling.csv (problems: structure.json, test_T3.json)'
    add('coupling_structures', len(crows), src)
    for system in sorted({r[1] for r in crows}):
        rs = [r for r in crows if r[1] == system]
        tag = system
        add(f'coupling_{tag}_largest_med', st.median(r[7] for r in rs), src,
            'median share of steps and pairs where the paired shaker is the largest path', 'pct0')
        add(f'coupling_{tag}_chance', rs[0][8], src, 'one over the number of shakers', 'pct0')
        add(f'coupling_{tag}_ownshare_med', st.median(r[6] for r in rs), src,
            'median own share of the summed path magnitudes', 'pct0')
    add('coupling_largest_max', max(r[7] for r in crows), src, 'largest over every structure', 'pct0')
    # The study's pair claims on the stepped sine that set matrix against paired or ratio.
    claims = json.load(open(os.path.join(study, 'claims', 'claims.json')))['claims']
    pc = [c for c in claims if c['kind'] == 'pair' and c['test'] == 'T3'
          and {c['law'], c.get('against')} & {'paired', 'ratio'}]
    pc_mx = [c for c in pc if 'matrix' in (c['law'], c.get('against'))]
    good = {'completion': 'higher', 'iec_share': 'higher', 'worst_over_db': 'lower', 'p95_db': 'lower'}
    better = [c for c in pc_mx if (c['law'] == 'matrix') == (c['side'] == good[c['reading']])]
    add('t3_pair_claims_versions', ', '.join(sorted({c['version'] for c in pc})), 'claims.json')
    write('stepped_pair_claims.csv', ['id', 'law', 'against', 'reading', 'side', 'system', 'kind', 'n', 'median'],
          [[c['id'], c['law'], c.get('against'), c['reading'], c['side'], c['system'], c['structure_kind'],
            c['study'].get('n'), c['study'].get('median')] for c in pc])
    src = 'data/stepped_pair_claims.csv (claims.json)'
    add('t3_pair_claims', len(pc), src, 'pair claims on T3 with paired or ratio')
    add('t3_pair_claims_mx', len(pc_mx), src, 'of them, against matrix')
    add('t3_pair_claims_mx_better', len(better), src, 'matrix on the better side')
    add('t3_pair_claim_first', min(c['id'] for c in pc_mx), src, 'first id')
    add('t3_pair_claim_last', max(c['id'] for c in pc_mx), src, 'last id')
    # Followed poles against the Python matrix in the study: the pair claims, by reading and side (as
    # followed poles reads).
    fpc = [c for c in claims if c['kind'] == 'pair'
           and {arm_id(c['law']), arm_id(c.get('against'))} == {'matrix', 'followed_poles'}]
    flip = {'higher': 'lower', 'lower': 'higher'}
    fp_rows = []
    for c in fpc:
        side = c['side'] if arm_id(c['law']) == 'followed_poles' else flip[c['side']]
        fp_rows.append([c['id'], c['reading'], side, c['test'], c['system'], c['structure_kind'], c['version']])
    write('followed_poles_pair_claims.csv', ['id', 'reading', 'followed_poles_side', 'test', 'system', 'kind', 'version'], fp_rows)
    s3 = 'data/followed_poles_pair_claims.csv (claims.json)'
    add('followed_poles_claims', len(fp_rows), s3, 'pair claims, followed_poles against matrix')
    for reading in ('completion', 'iec_share', 'worst_over_db'):
        for side in ('higher', 'lower'):
            rs = [r for r in fp_rows if r[1] == reading and r[2] == side]
            add(f'followed_poles_claims_{reading}_{side}', len(rs), s3)
            if rs:
                add(f'followed_poles_claims_{reading}_{side}_first', min(r[0] for r in rs), s3)
    add('followed_poles_claims_versions', ', '.join(sorted({r[6] for r in fp_rows})), s3)
    # The study's effects of the structure on the sweeps: a nonlinear tier against the linear one.
    harder = {'completion': 'lower', 'iec_share': 'lower', 'worst_over_db': 'higher'}
    ef = [c for c in claims if c['kind'] == 'effect' and c.get('against') == 'linear'
          and c['test'] in ('T1', 'T2', 'T5')]
    efh = [c for c in ef if c['side'] == harder[c['reading']]]
    write('sweep_effect_claims.csv', ['id', 'reading', 'side', 'kind', 'against', 'test', 'system', 'version'],
          [[c['id'], c['reading'], c['side'], c['structure_kind'], c['against'], c['test'], c['system'],
            c['version']] for c in ef])
    s4 = 'data/sweep_effect_claims.csv (claims.json)'
    add('effect_sweep_claims', len(ef), s4, 'effect claims, a nonlinear tier against linear, on sweeps')
    add('effect_sweep_harder', len(efh), s4, 'of them, the nonlinear tier on the harder side')
    add('effect_sweep_first', min(c['id'] for c in efh), s4)
    add('t3_pair_readings', ', '.join(sorted({c['reading'] for c in pc_mx})), src)


# ------------------------------------------------------------------------------------------------
# 5. The modal fit and the delay.
def fits(effort, out_c):
    rows = []
    port = open(os.path.join(effort, 'experiments', 'G', 'port_check_output_sys.txt')).read()
    for block in port.split('\n\n'):
        m = re.match(r'(frame-[\w-]+?)/T1:', block.strip())
        if not m:
            continue
        pid = m.group(1)
        for line in block.splitlines():
            d = re.match(r'\s+delay (.+?)\s+(\{.*\})$', line)
            if d:
                v = json.loads(d.group(2))
                rows.append(['delay', pid, d.group(1).strip(), v['found_share'], v['model_error']])
    names = {'block': 'the block', 'lag': 'lag less pipeline', 'C': 'estimate', 'no': 'none'}
    src = 'data/fig8_fits.csv (experiments/G/port_check_output_sys.txt)'
    for r in [r for r in rows if r[0] == 'delay']:
        key = {'b': 'block', 'l': 'lag', 'C': 'est', 'n': 'none'}[r[2][0]]
        tag = '6x6' if '6x6' in r[1] else '12x6'
        add(f'delay_err_{tag}_{key}', r[4], src, 'in-band model error', '.2f')
        add(f'delay_found_{tag}_{key}', r[3], src, 'modes found', 'pct0')
        n = re.search(r'(\d+(?:\.\d+)?)', r[2])
        if key in ('block', 'lag') and n:
            add(f'delay_samples_{tag}_{key}', int(float(n.group(1))), src)
    for name, keys in (('E9_ident_obs.json', None), ('E10_ident_obs.json', 'results'),
                       ('E10b_ident_obs.json', 'results')):
        d = json.load(open(os.path.join(out_c, name)))
        d = d[keys] if keys else d
        for k, v in d.items():
            fit, frames = k.split('|')
            rows.append(['fit', frames, fit, round(v['summary']['found'], 4), round(v['summary']['share_eps10'], 4)])
    write('fig8_fits.csv', ['part', 'structures', 'case', 'found_share', 'model_error_or_within_10pct'], rows)
    src = 'data/fig8_fits.csv (modal-fit records E9, E10, E10b)'
    fr = [r for r in rows if r[0] == 'fit']
    for fit in ('m0', 'm7d', 'm9d'):
        f = [r[3] for r in fr if r[2] == fit]
        e = [r[4] for r in fr if r[2] == fit]
        add(f'fit_{fit}_found_lo', min(f), src, 'modes found, frame sets', 'pct0')
        add(f'fit_{fit}_found_hi', max(f), src, '', 'pct0')
        add(f'fit_{fit}_within_lo', min(e), src, 'within 10 percent', 'pct0')
        add(f'fit_{fit}_within_hi', max(e), src, '', 'pct0')
    real = [r[4] for r in fr if r[2] in ('m3', 'm5', 'm7', 'm9') and r[1].endswith('realistic')]
    add('fit_real_undelayed_within_max', max(real), src, 'M3 to M9 on the realistic frames, delay left in', 'pct0')
    add('fit_m7c_within_lo', min(r[4] for r in fr if r[2] == 'm7c'), src, '', 'pct0')
    add('fit_m7c_within_hi', max(r[4] for r in fr if r[2] == 'm7c'), src, '', 'pct0')
    cm = os.path.join(effort, 'C_Modal_Fit.md')
    m = re.search(r'The bar is (\d+(?:\.\d+)?) found and\s+(\d+(?:\.\d+)?) within 10 %', open(cm).read())
    add('bar1_found', float(m.group(1)), 'C_Modal_Fit.md 4.3', '', 'pct0')
    add('bar1_within', float(m.group(2)), 'C_Modal_Fit.md 4.3', '', 'pct0')
    m = re.search(r'M9d took (\d+(?:\.\d+)?) to (\d+(?:\.\d+)?) min a structure', open(cm).read())
    add('m9d_min_lo', m.group(1), 'C_Modal_Fit.md 4.3')
    add('m9d_min_hi', m.group(2), 'C_Modal_Fit.md 4.3')
    m = re.search(r'phase\s+-(\d+(?:\.\d+)?) deg at 1000 Hz', open(cm).read())
    add('c10_phase_deg', m.group(1), 'C_Modal_Fit.md 4.3')


# ------------------------------------------------------------------------------------------------
# 6. Facts read from the record's own files.
def record(effort, research):
    dnw = os.path.join(effort, 'Did_Not_Work.md')
    led = os.path.join(research, 'Claims_Ledger.md')
    cat = os.path.join(research, 'Candidate_Laws.md')
    js = os.path.join(effort, 'J_Screen.md')
    gs = os.path.join(effort, 'G_Screen.md')
    # The research round on its own testbed.
    t = grab(led, r'MSN-C-T-07 \|[^|]*\|[^|]*\| Of the five published baselines.*?\((\d+) to (\d+) of (\d+) complete\)', 'T-07', 0)
    m = re.search(r'\((\d+) to (\d+) of (\d+) complete\)', t)
    add('rr_dwell_laws_sweep_lo', int(m.group(1)), 'MIMO_Sine/Claims_Ledger.md MSN-C-T-07')
    add('rr_dwell_laws_sweep_hi', int(m.group(2)), 'MIMO_Sine/Claims_Ledger.md MSN-C-T-07')
    add('rr_dwell_laws_sweep_n', int(m.group(3)), 'MIMO_Sine/Claims_Ledger.md MSN-C-T-07')
    a08 = grab(led, r'MSN-C-A-08 \|.*?completes (\d+) of (\d+) sweeps of the linear twin \((\d+) control aborts, (\d+) divergence', 'A-08', 0)
    m = re.search(r'completes (\d+) of (\d+) sweeps', a08)
    add('rr_fixed_gain_completed', int(m.group(1)), 'MIMO_Sine/Claims_Ledger.md MSN-C-A-08')
    add('rr_fixed_gain_runs', int(m.group(2)), 'MIMO_Sine/Claims_Ledger.md MSN-C-A-08')
    add('rr_fixed_gain', grab(led, r'MSN-C-T-04 \|.*?with the published gain \((\d+(?:\.\d+)?) an update\)', 'T-04'),
        'MIMO_Sine/Claims_Ledger.md MSN-C-T-04')
    add('rr_update_ms', grab(led, r'MSN-C-T-04 \|.*?and a (\d+) ms update', 'T-04 ms'),
        'MIMO_Sine/Claims_Ledger.md MSN-C-T-04')
    a13 = grab(led, r'MSN-C-A-13 \|.*?by a median (\d+(?:\.\d+)?) dB sweeping up.*?completes (\d+) of (\d+) against (\d+) sweeping down', 'A-13', 0)
    m = re.search(r'by a median (\d+(?:\.\d+)?) dB sweeping up.*?completes (\d+) of (\d+) against (\d+) sweeping down', a13)
    add('rr_carry_worse_db', m.group(1), 'MIMO_Sine/Claims_Ledger.md MSN-C-A-13')
    add('rr_carry_down', int(m.group(2)), 'MIMO_Sine/Claims_Ledger.md MSN-C-A-13')
    add('rr_carry_down_n', int(m.group(3)), 'MIMO_Sine/Claims_Ledger.md MSN-C-A-13')
    add('rr_carry_down_pub', int(m.group(4)), 'MIMO_Sine/Claims_Ledger.md MSN-C-A-13')
    l211 = grab(led, r'MSN-C-L2-11 \|.*?\((\d+) s a drive at (\d+) Hz, `Q` (\d+)\) against (\d+(?:\.\d+)?) s spent', 'L2-11', 0)
    m = re.search(r'\((\d+) s a drive at (\d+) Hz, `Q` (\d+)\) against (\d+(?:\.\d+)?) s spent', l211)
    add('rr_pilot_s', int(m.group(1)), 'MIMO_Sine/Claims_Ledger.md MSN-C-L2-11')
    add('rr_pilot_hz', int(m.group(2)), 'MIMO_Sine/Claims_Ledger.md MSN-C-L2-11')
    add('rr_pilot_q', int(m.group(3)), 'MIMO_Sine/Claims_Ledger.md MSN-C-L2-11')
    add('rr_pilot_in_bw_s', m.group(4), 'MIMO_Sine/Claims_Ledger.md MSN-C-L2-11')
    # The candidates' testbed standing before the benchmark.
    a15 = grab(cat, r'MSN-C-A-15\)\.\*\* The result does not rest on the shift\s+being right: (\d+), (\d+) and (\d+) of (\d+) completed.*?only (\d+) to (\d+) of \d+ within 3 dB', 'A-15', 0, re.S)
    m = re.search(r'(\d+), (\d+) and (\d+) of (\d+) completed.*?only (\d+) to (\d+) of \d+ within 3 dB', a15, re.S)
    for i, k in enumerate(['half', 'right', 'double', 'n', 'tol_lo', 'tol_hi']):
        add(f'tb_family_inverse_{k}', int(m.group(i + 1)), 'MIMO_Sine/Candidate_Laws.md, family_inverse (MSN-C-A-15)')
    a01 = grab(led, r'MSN-C-A-01 \|.*?on (\d+) \(up\) and (\d+) \(down\) of seeds 0 to 19 and on (\d+) and (\d+) of the held-back seeds 20 to 39; the published law on (\d+) and (\d+), and (\d+) and (\d+)', 'A-01', 0)
    m = re.search(r'on (\d+) \(up\) and (\d+) \(down\) of seeds 0 to 19 and on (\d+) and (\d+) of the held-back seeds 20 to 39; the published law on (\d+) and (\d+), and (\d+) and (\d+)', a01)
    for i, k in enumerate(['up', 'down', 'hb_up', 'hb_down', 'pub_up', 'pub_down', 'pub_hb_up', 'pub_hb_down']):
        add(f'tb_level_ladder_{k}', int(m.group(i + 1)), 'MIMO_Sine/Claims_Ledger.md MSN-C-A-01')
    a02 = grab(led, r'MSN-C-A-02 \|.*?K4 completes and holds 3 dB on (\d+) \(up\) and (\d+) \(down\) of seeds 0 to 19', 'A-02', 0)
    m = re.search(r'on (\d+) \(up\) and (\d+) \(down\) of seeds 0 to 19', a02)
    add('tb_level_ladder_ident_up', int(m.group(1)), 'MIMO_Sine/Claims_Ledger.md MSN-C-A-02')
    add('tb_level_ladder_ident_down', int(m.group(2)), 'MIMO_Sine/Claims_Ledger.md MSN-C-A-02')
    dither_txt = grab(cat, r'K5 with a\s+1 percent dither completes (\d+) of (\d+) at a 2 bandwidth drift', 'rls_dither A-04', 0, re.S)
    m = re.search(r'completes (\d+) of (\d+) at a 2 bandwidth drift', dither_txt)
    add('tb_rls_dither_completed', int(m.group(1)), 'MIMO_Sine/Candidate_Laws.md, rls_dither (MSN-C-A-04)')
    add('tb_rls_dither_n', int(m.group(2)), 'MIMO_Sine/Candidate_Laws.md, rls_dither (MSN-C-A-04)')
    add('tb_rls_dither_pub_stops', int(grab(cat, r'the published law stops\s+on the control abort on (\d+) of 40 seeds', 'rls_dither pub', 1, re.S)),
        'MIMO_Sine/Candidate_Laws.md, rls_dither (MSN-C-A-04)')
    # Package F's tuning runs.
    f8 = grab(dnw, r'\| DNW-F8 \|.*?\| (\d+) of (\d+) sweeps completed \(as `matrix`\), and it ended earlier than `matrix` on (\d+) of (\d+)', 'F8', 0)
    m = re.search(r'(\d+) of (\d+) sweeps completed \(as `matrix`\), and it ended earlier than `matrix` on (\d+) of (\d+)', f8)
    add('f8_completed', int(m.group(1)), 'Did_Not_Work.md DNW-F8')
    add('f8_runs', int(m.group(2)), 'Did_Not_Work.md DNW-F8')
    add('f8_earlier', int(m.group(3)), 'Did_Not_Work.md DNW-F8')
    f9 = grab(dnw, r'\| DNW-F9 \|.*?\| (\d+) of (\d+) completed, nearly all on the first pass', 'F9', 0)
    m = re.search(r'(\d+) of (\d+) completed, nearly all', f9)
    add('f9_completed', int(m.group(1)), 'Did_Not_Work.md DNW-F9')
    add('f9_runs', int(m.group(2)), 'Did_Not_Work.md DNW-F9')
    # Package J's development runs.
    j6 = grab(dnw, r'\| DNW-J6 \|.*?p95 (\d+(?:\.\d+)?) and (\d+(?:\.\d+)?) dB against K3\'s (\d+(?:\.\d+)?) dB.*?\((\d+(?:\.\d+)?) and (\d+(?:\.\d+)?) dB: still above K3\)', 'J6', 0)
    m = re.search(r'p95 (\d+(?:\.\d+)?) and (\d+(?:\.\d+)?) dB against K3\'s (\d+(?:\.\d+)?) dB.*?\((\d+(?:\.\d+)?) and (\d+(?:\.\d+)?) dB: still above K3\)', j6)
    for i, k in enumerate(['pole_trajectory_first', 'amplitude_indexed_first', 'followed_poles', 'pole_trajectory_after', 'amplitude_indexed_after']):
        add(f'jdev_{k}', m.group(i + 1), 'Did_Not_Work.md DNW-J6')
    dev = grab(js, r'j_predictive/dev/` \(MSNB-J-E1\), on structures that are \*\*not\*\* in the screen:(.*?)All at (T\d)', 'dev list', 0, re.S)
    add('jdev_structures', len(re.findall(r'frame-[\w-]+ s\d+', dev)), 'J_Screen.md 1.4', 'structures named in the list')
    add('jdev_test', re.search(r'All at (T\d)', dev).group(1), 'J_Screen.md 1.4')
    add('jdev_preview_abort_hz', int(grab(js, r'`j4` as first written aborted on the linear frame-6x6 s03 at (\d+) Hz', 'preview abort')), 'J_Screen.md 1.4')
    add('jdev_runs', int(grab(js, r'(\d+) runs in `[^`]*j_predictive/dev/`', 'dev runs')), 'J_Screen.md 1.4')
    add('j_mutations', int(grab(js, r'\*\*(\d+) of \d+ mutations caught\*\*', 'mutations')), 'J_Screen.md 1.3')
    # The research round's fit, on the testbed's own structures, and the followed-poles runs it gave.
    c1 = grab(dnw, r'\| DNW-C1 \|.*?found (\d+(?:\.\d+)?) to (\d+(?:\.\d+)?) of modes on exact testbed data.*?K3 with it: (\d+) and (\d+) of (\d+) on soft4x4_real \(up, down\) against (\d+) and (\d+) for K3_true', 'C1', 0)
    m = re.search(r'found (\d+(?:\.\d+)?) to (\d+(?:\.\d+)?) of modes on exact testbed data.*?K3 with it: (\d+) and (\d+) of (\d+) on soft4x4_real \(up, down\) against (\d+) and (\d+) for K3_true', c1)
    add('c1_found_lo', float(m.group(1)), 'Did_Not_Work.md DNW-C1', '', 'pct0')
    add('c1_found_hi', float(m.group(2)), 'Did_Not_Work.md DNW-C1', '', 'pct0')
    for i, k in enumerate(['up', 'down', 'n', 'true_up', 'true_down']):
        add(f'c1_followed_poles_{k}', int(m.group(i + 3)), 'Did_Not_Work.md DNW-C1')
    c11 = grab(dnw, r'\| DNW-C11 \|.*?the delay turns mode r\'s residue by -2 w_r / fs radians \(-(\d+) deg at (\d+) Hz, -(\d+) deg at (\d+) Hz\)', 'C11', 0)
    m = re.search(r'\(-(\d+) deg at (\d+) Hz, -(\d+) deg at (\d+) Hz\)', c11)
    for i, k in enumerate(['deg_lo', 'hz_lo', 'deg_hi', 'hz_hi']):
        add(f'c11_{k}', int(m.group(i + 1)), 'Did_Not_Work.md DNW-C11')
    # Followed poles on the M9d fit (first screen) and its cost.
    m9 = grab(gs, r'M9d costs (\d+) to (\d+) times the M7d run\'s clock', 'M9d', 0)
    m = re.search(r'(\d+) to (\d+) times', m9)
    add('m9d_cost_lo', int(m.group(1)), 'G_Screen.md 5')
    add('m9d_cost_hi', int(m.group(2)), 'G_Screen.md 5')
    # The two amplitude laws on the stepped sine in the agreement sample and the pilot.
    d5 = grab(os.path.join(effort, 'Claims_Ledger.md'), r'\| MSNB-C-D-5 \|.*?\|.*?\|(.*?)\|', 'D-5', 1)
    m = re.search(r'\((\d+) of (\d+) in each of the two agreement arms; (\d+) and (\d+) in the pilot\)', d5)
    add('d5_agree_aborts', int(m.group(1)), 'Claims_Ledger.md MSNB-C-D-5')
    add('d5_agree_runs', int(m.group(2)), 'Claims_Ledger.md MSNB-C-D-5')
    add('d5_pilot_aborts', int(m.group(3)), 'Claims_Ledger.md MSNB-C-D-5')
    m = re.search(r'T3 `paired` (\d+) of (\d+) in each of its three arms', d5)
    add('d5_py_paired', int(m.group(1)), 'Claims_Ledger.md MSNB-C-D-5')
    add('d5_py_n', int(m.group(2)), 'Claims_Ledger.md MSNB-C-D-5')
    m = re.search(r'T3 `ratio` (\d+), (\d+) \((\d+) more ended in law faults\) and (\d+) of (\d+)', d5)
    add('d5_py_ratio_lo', int(m.group(1)), 'Claims_Ledger.md MSNB-C-D-5')
    add('d5_py_ratio_hi', int(m.group(4)), 'Claims_Ledger.md MSNB-C-D-5')
    # The screens' setup, as their records state it.
    m = re.search(r'abort band (\d+) dB, (\d+) updates', open(gs).read())
    add('abort_band_db', int(m.group(1)), 'G_Screen.md 4')
    add('abort_updates', int(m.group(2)), 'G_Screen.md 4')
    m = re.search(r'cell medians (\d+) to (\d+) dB on the nonlinear', open(gs).read().replace('\n', ' '))
    add('g_over_cell_med_lo', int(m.group(1)), 'G_Screen.md 4')
    add('g_over_cell_med_hi', int(m.group(2)), 'G_Screen.md 4')
    m = re.search(r'within \+/-(\d+) % up to (\d+) Hz and \+/-(\d+) % above', open(gs).read())
    add('iec_pct_low', int(m.group(1)), 'G_Screen.md 3')
    add('iec_split_hz', int(m.group(2)), 'G_Screen.md 3')
    add('iec_pct_high', int(m.group(3)), 'G_Screen.md 3')
    jl = open(os.path.join(effort, 'J_Leads.md')).read()
    add('followed_poles_window', int(re.search(r"K3's fit pools the last (\d+) updates", jl).group(1)), 'J_Leads.md 2')
    add('followed_poles_step_bw', re.search(r'is limited to (\d+(?:\.\d+)?) bandwidths a', jl).group(1), 'J_Leads.md 2')
    add('amplitude_indexed_fp_passes', int(grab(js, r"fixed point on the loop's own drive \((\d+) passes", 'fp')), 'J_Screen.md 7')
    j5 = grab(dnw, r'\| DNW-J5 \|(.*?)\n', 'J5')
    m = re.search(r'non-finite at (\d+) Hz.*?offset of (\d+(?:\.\d+)?) of the reference.*?\(p95 (\d+(?:\.\d+)?) dB, K3 (\d+(?:\.\d+)?) dB\)', j5)
    for i, k in enumerate(['nonfinite_hz', 'gate', 'p95', 'followed_poles']):
        add(f'j5_{k}', m.group(i + 1), 'Did_Not_Work.md DNW-J5')
    j6 = grab(dnw, r'\| DNW-J6 \|(.*?)\n', 'J6')
    m = re.search(r'fitted poles ran (\d+) to (\d+) bandwidths', j6)
    add('j6_bw_lo', int(m.group(1)), 'Did_Not_Work.md DNW-J6')
    add('j6_bw_hi', int(m.group(2)), 'Did_Not_Work.md DNW-J6')
    c1 = grab(dnw, r'\| DNW-C1 \|(.*?)\n', 'C1 row')
    m = re.search(r'(\d+(?:\.\d+)?) to (\d+(?:\.\d+)?) on exact frame data', c1)
    add('c1_frame_exact_lo', float(m.group(1)), 'Did_Not_Work.md DNW-C1', '', 'pct0')
    add('c1_frame_exact_hi', float(m.group(2)), 'Did_Not_Work.md DNW-C1', '', 'pct0')
    c2 = grab(dnw, r'\| DNW-C2 \|(.*?)\n', 'C2 row')
    m = re.search(r'\((\d+(?:\.\d+)?) to (\d+(?:\.\d+)?) on lin4x4\).*?found unchanged at (\d\.\d+)', c2)
    add('c2_err_before', m.group(1), 'Did_Not_Work.md DNW-C2')
    add('c2_err_after', m.group(2), 'Did_Not_Work.md DNW-C2')
    add('c2_found', float(m.group(3)), 'Did_Not_Work.md DNW-C2', '', 'pct0')
    c4 = grab(dnw, r'\| DNW-C4 \|(.*?)\n', 'C4 row')
    m = re.search(r'over the whole (\d+)-(\d+) Hz band.*?Misses the (\d+) to (\d+) Hz modes on exact data: about (\d+) lines in their bandwidth against about (\d+) at (\d+) Hz', c4)
    for i, k in enumerate(['band_lo', 'band_hi', 'miss_lo', 'miss_hi', 'lines_low', 'lines_high', 'at_hz']):
        add(f'c4_{k}', int(m.group(i + 1)), 'Did_Not_Work.md DNW-C4')
    c15 = grab(dnw, r'\| DNW-C15 \|(.*?)\n', 'C15 row')
    m = re.search(r'M7 exact (\d+(?:\.\d+)?) to (\d+(?:\.\d+)?) found\); the identification costs another (\d+(?:\.\d+)?) to (\d+(?:\.\d+)?)', c15)
    add('c15_exact_lo', float(m.group(1)), 'Did_Not_Work.md DNW-C15', '', 'pct0')
    add('c15_exact_hi', float(m.group(2)), 'Did_Not_Work.md DNW-C15', '', 'pct0')
    add('c15_ident_lo', float(m.group(3)), 'Did_Not_Work.md DNW-C15', 'points', 'pct0')
    add('c15_ident_hi', float(m.group(4)), 'Did_Not_Work.md DNW-C15', 'points', 'pct0')
    f8 = grab(dnw, r'\| DNW-F8 \|(.*?)\n', 'F8 row')
    # The rules' thresholds, as written before the runs.
    gtxt = ' '.join(open(gs).read().split())
    jtxt = ' '.join(open(js).read().split())
    add('rule_db', int(re.search(r"not worse than `matrix`'s by more than (\d+) dB in the median", gtxt).group(1)), 'G_Screen.md 3')
    m = re.search(r"lower than > `matrix`'s on at least (\d+) of the (\d+) structures|lower than `matrix`'s on at least (\d+) of the (\d+) structures", jtxt)
    add('rule_j_p95', int(m.group(1) or m.group(3)), 'J_Screen.md 2')
    add('rule_j_n', int(m.group(2) or m.group(4)), 'J_Screen.md 2')
    add('family_inverse_drop_pct', float(re.search(r'expected_drop` (\d+(?:\.\d+)?)', gtxt).group(1)), 'G_Screen.md 1', '', 'pct0')
    ctxt = ' '.join(open(cat).read().split())
    m = re.search(r'stops on the control abort on (\d+) of (\d+) seeds .*? K5 with a (\d+) percent dither completes (\d+) of (\d+) at a (\d+) bandwidth drift', ctxt)
    add('tb_rls_dither_pub_n', int(m.group(2)), 'MIMO_Sine/Candidate_Laws.md, rls_dither')
    add('tb_rls_dither_dither_pct', int(m.group(3)), 'MIMO_Sine/Candidate_Laws.md, rls_dither')
    add('tb_rls_dither_drift_bw', int(m.group(6)), 'MIMO_Sine/Candidate_Laws.md, rls_dither')
    ltxt = ' '.join(open(led).read().split())
    m = re.search(r'MSN-C-A-01 \|.*?of seeds (\d+) to (\d+) and on', ltxt)
    add('tb_level_ladder_n', int(m.group(2)) - int(m.group(1)) + 1, 'MIMO_Sine/Claims_Ledger.md MSN-C-A-01', 'seeds counted from the range')
    # Kevin's words.
    dec = os.path.join(effort, '..', '..', 'DECISIONS.md')
    add('quote_followed_poles', grab(dec, r'Kevin: "(Include) K3"', 'Include') + ' [followed poles]', 'DECISIONS.md 2026-11-25',
        "Kevin's words, the law's name in brackets for its code")
    add('quote_leads', grab(dec, r'Kevin: "(Don\'t add any of the four)"', 'leads'), 'DECISIONS.md 2026-11-25')
    add('quote_reactive', grab(dec, r'\.\.\. (something predictive rather than reactive based on the system Id/frf since reactive laws clearly can\'t handle the nonlinear shifts)', 'reactive'),
        'DECISIONS.md 2026-11-25')
    # The engine's pipeline delay.
    add('pipeline_samples', int(grab(js, r'(\d+)-sample delay are what is left', 'pipeline', 1)
                                if False else grab(os.path.join(effort, 'J_Leads.md'),
                                                   r'The drive reaches the structure (\d+) samples after it is written', 'pipeline')),
        'J_Leads.md 2')


def main():
    ap = argparse.ArgumentParser()
    for a in ('effort', 'research', 'problems', 'g-runs', 'j-runs', 'study', 'fits'):
        ap.add_argument('--' + a, required=True)
    a = ap.parse_args()
    if 'audit_runs' in os.path.realpath(a.study) or any('audit_runs' in os.path.realpath(p) for p in
                                                        (a.g_runs, a.j_runs, a.problems)):
        sys.exit('the audit is not read')
    os.makedirs(DATA, exist_ok=True)
    mode_shift(a.problems)
    g_runs, j_runs, G, J = screens(a.effort)
    screen_numbers(g_runs, j_runs, G, J)
    traces(a.g_runs, a.j_runs)
    stepped(a.study, a.problems)
    fits(a.effort, a.fits)
    record(a.effort, a.research)
    write('numbers.csv', ['key', 'text', 'value', 'source', 'how'], NUMBERS)
    print('wrote', len(NUMBERS), 'numbers')


if __name__ == '__main__':
    main()
