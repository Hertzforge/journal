"""Write every file in ../data from the study's saved results.

This is the record of how the data files were made. It needs the study's run files and its
printed outputs, which are not in this bundle:

    python extract_data.py --runs <folder of run files> --outputs <folder of printed outputs>

`--runs` is the folder that holds the run records (`audit/`, `audit_e3/`, `heldout/`, `gym/`);
`--outputs` is the folder that holds the printed outputs (`experiments/r4/`, `experiments/r6/`).
The geometry and the development structures' modes are read from the simulator code in `--runs`
(`heldout/` and `gym/`), which needs numpy and, for `gym/`, its compiled bridge library.

Every count quoted in the article is added here, by this script, and written with its source to
`../data/numbers.csv`. Copyright 2026 Kevin Cross. MIT license.
"""
import argparse
import csv
import glob
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
NUMBERS = []


def write(name, header, rows):
    with open(os.path.join(DATA, name), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow([('%.4f' % v) if isinstance(v, float) else v for v in r])
    print('wrote', name, len(rows), 'rows')


def number(key, value, source):
    NUMBERS.append((key, value, source))


def load(path):
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------- Figure 1: the structures
def geometry(runs):
    sys.path.insert(0, os.path.join(runs, 'gym'))
    sys.path.insert(0, os.path.join(runs, 'heldout'))
    from mshock_heldout import definitions as d
    rows = []
    for name, P, extra, sup, ctrl, split in (
            ('panel', d.S4_PLATE, d.S4_EXTRA, [(r, c, b) for r, c, b, _ in d.S4_SUPPORTS], d.S4_CTRL,
             d.S4_SPLIT['split_col']),
            ('frame', d.F_PLATE, d.F_EXTRA, [(r, c, b) for r, c, b, _ in d.F_SUPPORTS], d.F_CTRL,
             d.F_SPLIT['split_col'])):
        L = P['Lx']
        for r in range(P['rows']):
            for c in range(P['cols']):
                rows.append((name, 'node', c * L, r * L, '', '', '', ''))
                if c + 1 < P['cols']:
                    kind = 'lap_beam' if c == split else 'beam'
                    rows.append((name, kind, c * L, r * L, (c + 1) * L, r * L, '', ''))
                if r + 1 < P['rows']:
                    rows.append((name, 'beam', c * L, r * L, c * L, (r + 1) * L, '', ''))
        for r, c, kg in extra:
            rows.append((name, 'component', c * L, r * L, '', '', kg, ''))
        for r, c, b in sup:
            rows.append((name, 'support_and_shaker', c * L, r * L, '', '', b, ''))
        for k, (r, c) in enumerate(ctrl):
            rows.append((name, 'control', c * L, r * L, '', '', k + 1, ''))
        rows.append((name, 'lap_joint_line', (split + 0.5) * L, -0.03, (split + 0.5) * L,
                     (P['rows'] - 1) * L + 0.03, '', ''))
        rows.append((name, 'plate', P['m_plate'], P['rows'], P['cols'], L, '', ''))
    write('fig1_geometry.csv', ['structure', 'item', 'x_m', 'y_m', 'x2_m', 'y2_m', 'value', 'note'],
          rows)
    number('panel_mass_kg', d.S4_PLATE['m_plate'], 'heldout definitions S4_PLATE')
    number('panel_base_masses_kg', ' '.join(str(m) for m in d.S4_BASE_MASS), 'S4_BASE_MASS')
    number('panel_shaker_gain_N_per_V', d.S4_GAIN, 'S4_GAIN')


def development_structures(runs):
    sys.path.insert(0, os.path.join(runs, 'gym'))
    from mshock_gym import plants
    from mshock_gym.numpy_plants import port_of
    rows = []
    first = None
    for name in ('linear', 'moderate', 'severe', 'nonsat', 'late', 'spring16', 'spring32'):
        q = port_of(plants.get(name))
        if first is None:
            first = q
        kd = getattr(q, 'kd', '')
        # the springs carry the jointed parameters by inheritance but use only their stiffness
        # term (numpy_plants.SpringNumpy.simulate_batch), so no envelope law is written for them
        j = None if kd != '' else q.joint
        rows.append((name, q.n_drives, q.n_controls, q.fs, q.record_len,
                     ' '.join('%g' % f for f in q.f_hz),
                     j['delta'] if j else ('' if kd != '' else 0.0), j['freq_exponent'] if j else '',
                     j['damping_gain'] if j else '', j['decay_cycles'] if j else '', kd))
    q = port_of(plants.get('research8'))
    rows.append(('research', q.n_drives, q.n_controls, float(q.fs), q.record_len,
                 ' '.join('%g' % m['fn0_hz'] for m in q.p['modes']), q.p['delta'], '', '', '', ''))
    number('research_model_damping_percent', ' '.join('%g' % (100 * m['zeta0']) for m in q.p['modes']),
           'gym research8 LevelNumpy params')
    write('fig1_development_structures.csv',
          ['structure', 'shakers', 'controls', 'sample_rate_hz', 'record_samples', 'modes_hz', 'mode_drop',
           'drop_exponent', 'damping_gain', 'envelope_decay_cycles', 'spring_stiffness_drop'], rows)
    write('fig1_development_modes.csv', ['mode', 'frequency_hz', 'damping_ratio'],
          [(k + 1, float(f), float(z)) for k, (f, z) in enumerate(zip(first.f_hz, first.zeta0))])


# ---------------------------------------------------------------- Figure 2: the test sequence
def sequence(runs):
    r = load(os.path.join(runs, 'audit_e3/out/D/severe__followed__s11__n0.json'))
    rows = [(x['index'] + 1, x['kind'], x['level_db'], x['over_db'], x['abs_db']) for x in r['records']]
    write('fig2_test_sequence.csv', ['pulse', 'kind', 'level_db', 'over_db', 'absolute_db'], rows)
    # the identification of the development structures: 40 realizations of two records of 16384
    # samples at 12 800 Hz (gym/mshock_gym/ident.py: FRAMES, PROBE_REALIZATIONS)
    number('buzz_seconds_4x4', 40 * 2 * 16384 / 12800.0, 'gym ident.py: 40 realizations x 2 records')


# ---------------------------------------------------------------- Figure 3: softening by level
def softening(outputs, runs):
    rows = []
    txt = open(os.path.join(outputs, 'experiments/r4/ms_r4_01_fit_by_level.txt')).read()
    for plant, label in (('shock-jointed-4x4-moderate', 'moderate'),
                         ('shock-jointed-4x4-severe', 'severe'),
                         ('jointed-4x4-non-saturating', 'non-saturating')):
        block = txt.split(plant + ':', 1)[1].split('full level', 1)[0]
        for m in re.finditer(r'^\| ([+-]\d+) \| [+-][\d.]+ \| ([\d.]+) \|', block, re.M):
            rows.append(('development', label, float(m.group(1)), float(m.group(2))))
    for plant, label in (('hyst-moderate', 'held-out moderate joints'),
                         ('hyst-onset', 'held-out onset'),
                         ('hyst-severe', 'held-out low preload')):
        t = open(os.path.join(outputs, 'experiments/r6/heldout/outputs/characterization_%s.txt' % plant)).read()
        block = t.split("(b) burst at the pulse's amplitude: frequency change %", 1)[1].split('\n\n', 1)[0]
        for line in block.strip().splitlines():
            parts = [p.strip() for p in line.split('|')]
            if not re.match(r'^[+-]\d+$', parts[0]):
                continue
            vals = [float(v) for v in parts[1:]]
            rows.append(('held-out', label, float(parts[0]), -min(vals)))
    write('fig3_softening_by_level.csv', ['set', 'structure', 'level_db', 'largest_drop_percent'], rows)


# ---------------------------------------------------------------- Figure 4: the networks
def identification_length(outputs, runs):
    rows = []
    d = load(os.path.join(runs, 'audit/out/e2_heldout_pred.json'))
    for pred, nlow in (('frozen', 0), ('setnet', 0), ('setnet', 4), ('powerlaw', 4)):
        by_len = {}
        for plant, v in d.items():
            for e in v['howlong']:
                if e['n_low'] == (0 if pred == 'frozen' else nlow):
                    by_len.setdefault(e['buzz_s'], []).append(abs(e[pred]['over']))
        for s in sorted(by_len):
            rows.append(('held-out (nine)', pred, nlow, s, float(np.median(by_len[s])), len(by_len[s])))
    pop = load(os.path.join(outputs, 'experiments/r6/e2/outputs/e2_06_howlong.json'))
    for tier in ('realistic', 'stress'):
        for pred, nlow in (('frozen', 0), ('setnet', 4)):
            by_len = {}
            for e in pop:
                if e['tier'] == tier and e['n_low'] == (0 if pred == 'frozen' else nlow):
                    by_len.setdefault(e['buzz_s'], []).append(abs(e[pred]['over']))
            for s in sorted(by_len):
                rows.append(('population, %s' % tier, pred, nlow, s, float(np.median(by_len[s])),
                             len(by_len[s])))
    write('fig4a_identification_length.csv',
          ['plants', 'predictor', 'low_pulses', 'buzz_s', 'median_abs_error_db', 'n'], rows)


def per_pulse(path, law, seed=''):
    r = load(path)
    return [(law, seed, x['index'] + 1, x['kind'], x['level_db'], x['over_db'], x['abs_db'])
            for x in r['records']]


def hardening(runs):
    rows = per_pulse(os.path.join(runs, 'audit/out/main/harden__e2_model_setnet4__s11__n0.json'),
                     'network as the law\'s model')
    rows += per_pulse(os.path.join(runs, 'heldout/out/bench/harden__followed__seed11__noise0.json'),
                      'followed family, 12 % ceiling')
    rows += per_pulse(os.path.join(runs, 'audit/out/lead_recheck/harden__frozen__s11__n0.json'),
                      'frozen law')
    write('fig4b_hardening_pulses.csv',
          ['law', 'seed', 'pulse', 'kind', 'level_db', 'over_db', 'absolute_db'], rows)


# ---------------------------------------------------------------- Figure 6: unjudged pulses
def full_level(runs):
    rows = []
    for seed in range(11, 16):
        for law, path in (
                ('coupled corrector', 'audit_e3/out/C/spring32__e3__s%d__n0.001.json'),
                ('hold rule', 'audit_e3/out_ah/ah4/spring32__hold3__s%d__n0.001.json'),
                ('followed family, 12 % ceiling', 'audit_e3/out/D/spring32__followed__s%d__n0.001.json')):
            r = load(os.path.join(runs, path % seed))
            full = [x for x in r['records'] if x['level_db'] == 0.0]
            judged = set()
            if full:
                judged.add(full[0]['index'])
                if len(full) >= 3:
                    judged.add(full[2]['index'])
                judged.add(r['records'][-1]['index'])
            for k, x in enumerate(full):
                rows.append((law, seed, k + 1, x['over_db'], 'yes' if x['index'] in judged else 'no'))
    write('fig6_full_level_pulses.csv',
          ['law', 'seed', 'full_level_pulse', 'over_db', 'judged_by_first_third_last'], rows)
    for law in ('coupled corrector', 'hold rule', 'followed family, 12 % ceiling'):
        worst = max(r[3] for r in rows if r[0] == law)
        number('spring32_1e-3_worst_full_level_over_%s' % law.replace(' ', '_'), round(worst, 2),
               'fig6_full_level_pulses.csv')


# ---------------------------------------------------------------- Figure 5: held out, by reading
HELD = [('s4-linear', 'control'), ('hyst-moderate', 'realistic'),
        ('shaker-clip-moderate', 'realistic'), ('soft-harden', 'realistic'),
        ('hyst-onset', 'stress'), ('harden', 'stress'), ('hyst-severe', 'stress'),
        ('hyst-scatter', 'stress'), ('shaker-clip-severe', 'stress')]


def held_out_path(runs, law, plant, noise):
    n = '0' if noise == 0 else '0.001'
    if law in ('frozen', 'followed') and noise == 0:
        return 'heldout/out/bench/%s__%s__seed11__noise0.json' % (plant, law)
    return {'frozen': 'audit/out/main/%s__frozen__s11__n%s.json',
            'followed': 'audit/out/main/%s__followed__s11__n%s.json',
            'physics model': 'audit/out/main/%s__e1__s11__n%s.json',
            'network as the law\'s model': 'audit/out/main/%s__e2_model_setnet4__s11__n%s.json',
            'network sets the ceiling': 'audit/out/main/%s__e2_ceil_setnet__s11__n%s.json',
            'coupled corrector': 'audit_e3/out/B/%s__e3__s11__n%s.json',
            'hold rule': 'audit_e3/out_ah/ah3/%s__hold3__s11__n%s.json'}[law] % (plant, n)


def verdicts(r):
    """Strict: criteria 1 to 7. A: the run ends at full level with every control inside 3 dB.
    B: nothing, at any level, more than 3 dB over the full-level target."""
    recs = r['records']
    c7 = all(x['over_db'] <= 3.0 for x in recs if x['level_db'] == 0.0)
    strict = bool(r['passed']) and c7
    a = bool(r['criteria']['5_completed_last_within_3'])
    b = all(x['abs_db'] <= 3.0 for x in recs)
    worst_abs = max(x['abs_db'] for x in recs)
    return strict, a, b, worst_abs


def held_out(runs):
    laws = ['frozen', 'followed', 'physics model', 'network as the law\'s model',
            'network sets the ceiling', 'coupled corrector', 'hold rule']
    rows = []
    for law in laws:
        for plant, tier in HELD:
            for noise in (0, 1e-3):
                r = load(os.path.join(runs, held_out_path(runs, law, plant, noise)))
                s, a, b, w = verdicts(r)
                rows.append((law, plant, tier, noise, 'pass' if s else 'fail', 'yes' if a else 'no',
                             'yes' if b else 'no', w, r['end']))
    write('fig5_held_out_runs.csv',
          ['law', 'structure', 'tier', 'noise', 'strict', 'ends_at_full_level_in_tolerance',
           'never_over_full_level_target_by_3db', 'worst_absolute_db', 'end'], rows)
    for law in laws:
        for tier in ('control', 'realistic', 'stress'):
            sel = [r for r in rows if r[0] == law and r[2] == tier]
            number('heldout_%s_%s_strict' % (law, tier), '%d of %d' % (sum(r[4] == 'pass' for r in sel),
                   len(sel)), 'fig5_held_out_runs.csv')
            number('heldout_%s_%s_readingA' % (law, tier), sum(r[5] == 'yes' for r in sel),
                   'fig5_held_out_runs.csv')
            number('heldout_%s_%s_readingB' % (law, tier), sum(r[6] == 'yes' for r in sel),
                   'fig5_held_out_runs.csv')


# ---------------------------------------------------------------- Figure 7: the noise cures
def rows_of(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def noise_cures(outputs):
    lead = os.path.join(outputs, 'experiments/r6/lead')
    hold = [r for r in rows_of(os.path.join(lead, 'hold_runs_2026-11-14.jsonl')) if r['law'] == 'hold3']
    hold += [r for r in rows_of(os.path.join(lead, 'hold_seeds_runs_2026-11-14.jsonl')) if r['law'] == 'hold3']
    avg = rows_of(os.path.join(lead, 'avg_probes_runs_2026-11-14.jsonl'))
    climb = rows_of(os.path.join(lead, 'climb_runs_2026-11-14.jsonl'))
    out = []
    realistic = ('linear', 'moderate')
    for method, rs in (('hold rule as it is (jump from -34 dB to -12 dB)', hold),
                       ('each probe averaged 16 times', avg),
                       ('climb in 6 dB steps, unchecked', climb)):
        seen = set()
        for noise in sorted({r['noise'] for r in rs}):
            sel = []
            for r in rs:
                key = (r['plant'], r['noise'], r['seed'])
                if r['noise'] == noise and key not in seen:
                    seen.add(key)
                    sel.append(r)
            strict = sum(1 for r in sel if r['r6'] and r['c7'])
            a = sum(1 for r in sel if r['crit'][4] == 'o')
            # criteria 2 and 6, and no full-level pulse over by 3 dB (a run that never reached full
            # level has no full-level pulse: `maxfull` is NaN there)
            b = sum(1 for r in sel if r['crit'][1] == 'o' and r['crit'][5] == 'o'
                    and not (r['maxfull'] == r['maxfull'] and r['maxfull'] > 3.0))
            real = [r for r in sel if r['plant'] in realistic]
            out.append((method, noise, len(sel), strict, a, b, sum(1 for r in real if r['r6'] and r['c7']),
                        len(real)))
    write('fig7_noise_cures.csv', ['method', 'noise', 'runs', 'strict', 'ends_at_full_level_in_tolerance',
                                   'never_over_full_level_target_by_3db', 'realistic_strict', 'realistic_runs'],
          out)
    for row in out:
        number('noise_cure_%s_%g' % (row[0][:12].replace(' ', '_'), row[1]),
               '%d/%d strict, %d A, %d B; realistic %d/%d' % (row[3], row[2], row[4], row[5], row[6], row[7]),
               'fig7_noise_cures.csv')
    return hold


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', required=True)
    ap.add_argument('--outputs', required=True)
    a = ap.parse_args()
    os.makedirs(DATA, exist_ok=True)
    geometry(a.runs)
    development_structures(a.runs)
    sequence(a.runs)
    softening(a.outputs, a.runs)
    identification_length(a.outputs, a.runs)
    hardening(a.runs)
    full_level(a.runs)
    held_out(a.runs)
    noise_cures(a.outputs)
    write('numbers.csv', ['key', 'value', 'source'], NUMBERS)


if __name__ == '__main__':
    main()
