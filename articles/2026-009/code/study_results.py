"""The study's results, law by law, from the scorecards of the study's runs. Writes the data of
Section 3's tables and of Figures 1 and 2 into ../data. Reads the scorecards only; it runs nothing
and imports no study or scorer code.

    PYTHONDONTWRITEBYTECODE=1 python3 study_results.py RESULTS/cards/main
    PYTHONDONTWRITEBYTECODE=1 python3 study_results.py RESULTS/cards/audit RESULTS/cards/audit2 --audit

RESULTS is the record "Hertzforge Open Benchmark Set, MIMO Random Suite: Results of the Control Law
Study and Its Independent Audit", version 0.2 (DOI 10.5281/zenodo.24310746), unpacked. Its
cards/main holds the 3,793
scorecards of the study's runs (scorer 0.2.1-draft). With --audit, the audit's two batches (the ten
held-back structures) are read together, structure 24 is left out as in the audit's record, and the
same tables are written as `audit_*` files.

Rules, the same as the study's analysis:
- The result of a case is its run with the checks widened where that run exists and completed,
  else its completed run with the checks at their defaults. A stopped run is never a result.
- Systems with as many shakers as control gauges (6 x 6, 12 x 12) and systems with more control gauges
  than shakers (3 x 12, 6 x 12, 12 x 24) are never pooled. A structure's value in a group is the
  mean over the systems of that group; medians and quartiles (numpy, linear) are over structures.
- A change is the difference on the same structure and system, then the mean over the group's systems.
  Counts "up" and "down" are structures on which it exceeds 0.2 dB either way.
- "Flagged" structures are the ones the benchmark marks (seeds 5 and 33, driven above 30 g RMS;
  seed 15 on 12 x 12 at the realistic size, whose service calculation oscillates; seed 1 on the
  systems with as many shakers as control gauges, where the member would yield at full level).
- A structure whose hardening member changes in service by less than a quarter of the size's
  design change (realistic 1 percent, strong 4 percent) is listed as changing little in service.

Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
import csv
import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np

ARGS = [a for a in sys.argv[1:] if a != '--audit']
if not ARGS:
    sys.exit('usage: study_results.py CARDS_FOLDER [CARDS_FOLDER ...] [--audit]')
CARDS = ARGS                                               # one or more folders of scorecards
PREFIX = 'audit' if '--audit' in sys.argv[1:] else 'study'   # 'audit' for the held-back structures' scorecards
LEFT_OUT = ('s24_',) if PREFIX == 'audit' else ()           # structure 24 is not in the audit's results
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
LAWS = ['pinv_closed', 'pinv_open', 'shape_svd', 'buzz_match', 'min_drive', 'band_average']
SQUARE = ('6x6', '12x12')
FLOOR = 0.2
TIER = {'realistic': 1.0, 'strong': 4.0}
LINES = {
    'control': lambda d: d['card']['c_b3_rms'],      # control gauges, per-gauge RMS dB error in 1/3-octave bands
    'held_out': lambda d: d['card']['h_b3_rms'],     # held-out gauges, the same
    'level': lambda d: d['card']['level_mean'],      # mean dB error over gauges and bands
    'over_test': lambda d: d['card']['worst_over_b3'],  # worst band over its target, dB
    'stress': lambda d: d['stress']['rms'],          # RMS over elements of the dB error of element RMS stress
    'stress_bias': lambda d: d['stress']['bias'],    # mean of the same
}


def group(rig):
    return 'equal' if rig in SQUARE else 'more_controls'


def flagged(seed, rig, variant):
    return seed in (5, 33) or (seed == 15 and rig == '12x12' and variant == 'realistic') or (seed == 1 and rig in SQUARE)


def arm(j):
    return 'tuned' if j['setting'] == 'tuned' else ('measured_again' if j['frf'] == 'update' else 'default')


def load():
    passes = defaultdict(dict)   # base id -> {'default': card, 'opened': card}
    for p in sorted(q for c in CARDS for q in glob.glob(os.path.join(c, '*.json'))):
        if os.path.basename(p).startswith(LEFT_OUT):
            continue
        d = json.load(open(p))
        j = d['job']
        passes[j['base_id']]['opened' if j['protections'] == 'opened' else 'default'] = d
    results, jobs = {}, {}
    for b, ps in passes.items():
        j = (ps.get('opened') or ps.get('default'))['job']
        jobs[b] = (j, ps)
        o, dflt = ps.get('opened'), ps.get('default')
        pick = None
        if o is not None and o['outcome']['completed'] and o.get('scored'):
            pick = o
        elif dflt is not None and dflt['outcome']['completed'] and dflt.get('scored'):
            pick = dflt
        if pick is not None:
            results[(j['seed'], j['rig'], j['variant'], j['law'], arm(j))] = pick
    return results, jobs


def write(name, header, rows):
    name = PREFIX + name[len('study'):] if name.startswith('study') else name
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print('wrote', name, len(rows), 'rows')


def stats(vals):
    v = np.array(list(vals.values()))
    if v.size == 0:
        return None
    return dict(n=int(v.size), median=float(np.median(v)), q1=float(np.percentile(v, 25)), q3=float(np.percentile(v, 75)),
                up=int((v > FLOOR).sum()), down=int((v < -FLOOR).sum()))


def per_structure(results, law, a, variant, grp, line, keep=lambda s, r, v: True, rigs=None, base=None):
    acc = defaultdict(list)
    for (s, r, v, l, ar), d in results.items():
        if l != law or ar != a or v != variant or group(r) != grp or (rigs and r not in rigs) or not keep(s, r, v):
            continue
        x = LINES[line](d)
        if base is not None:
            b = base(s, r)
            if b is None:
                continue
            x = x - LINES[line](b)
        acc[s].append(x)
    return {s: float(np.mean(x)) for s, x in acc.items()}


def main():
    os.makedirs(OUT, exist_ok=True)
    results, jobs = load()

    # The member's change in service, per structure and size (one value per structure and variant).
    service = defaultdict(list)
    tested = defaultdict(list)
    for (s, r, v, l, a), d in results.items():
        m = ((d.get('structure_state') or {}).get('service_line') or {}).get('member') or {}
        if v in ('realistic', 'strong') and m.get('change_pct_service') is not None:
            service[(s, v)].append(m['change_pct_service'])
            if a == 'default' and m.get('change_pct_played') is not None:
                tested[(v, r, s)].append(m['change_pct_played'])
        if v.endswith('_hard') and a == 'default' and m.get('change_pct_played') is not None:
            tested[(v, r, s)].append(m['change_pct_played'])
    # As tested: per structure, the median over the laws' runs; then over structures.
    tested_by = defaultdict(list)
    for (v, r, s), x in tested.items():
        tested_by[(v, r)].append(float(np.median(x)))
    tested = tested_by
    little = {v: {s for (s, vv), x in service.items() if vv == v and float(np.median(x)) < TIER[v] / 4} for v in TIER}
    keep_all = lambda s, r, v: True
    keep_noflag = lambda s, r, v: not flagged(s, r, v)
    keep_moved = lambda s, r, v: s not in little.get(v.split('_')[0], set())
    rows = []
    for v in TIER:
        x = np.array([float(np.median(service[k])) for k in service if k[1] == v])
        rows.append([v, 'in service', '', len(x), f'{np.median(x):+.2f}', f'{x.min():+.2f}', f'{x.max():+.2f}',
                     ' '.join(str(s) for s in sorted(little[v]))])
        for r in ('3x12', '6x12', '12x24', '6x6', '12x12'):
            t = np.array(tested.get((v, r), []))
            if t.size:
                rows.append([v, 'as tested, both effects', r, t.size, f'{np.median(t):+.2f}', f'{t.min():+.2f}', f'{t.max():+.2f}', ''])
        for r in ('6x12', '6x6'):
            t = np.array(tested.get((v + '_hard', r), []))
            if t.size:
                rows.append([v, 'as tested, hardening member only', r, t.size, f'{np.median(t):+.2f}', f'{t.min():+.2f}', f'{t.max():+.2f}', ''])
    write('study_member_state.csv', ['size', 'state', 'rig', 'structures', 'member_change_pct_median', 'min', 'max',
                                     'structures_changing_little_in_service'], rows)

    # Outcomes with the checks at their defaults, and with them widened.
    rows = []
    totals = defaultdict(int)
    stop_loops = []
    for law in LAWS:
        for a in ('default', 'tuned', 'measured_again'):
            c = defaultdict(int)
            for b, (j, ps) in jobs.items():
                if j['law'] != law or arm(j) != a:
                    continue
                dflt, o = ps.get('default'), ps.get('opened')
                if dflt is not None:
                    c['default_runs'] += 1
                    if dflt['outcome']['completed']:
                        c['default_completed'] += 1
                    else:
                        g = dflt['outcome']['stop']['guard']
                        c['stopped_' + g] += 1
                        stop_loops.append(dflt['outcome']['stop']['loop'])
                        if o is not None and o['outcome']['completed']:
                            c['stopped_then_completed_widened'] += 1
                if o is not None:
                    c['widened_runs'] += 1
                    if o['outcome']['completed']:
                        c['widened_completed'] += 1
                    else:
                        c['widened_stopped_' + o['outcome']['stop']['guard']] += 1
            for k, x in c.items():
                totals[k] += x
            rows.append([law, a, c['default_runs'], c['default_completed'], c['stopped_divergence'], c['stopped_cap_divergence'],
                         c['stopped_then_completed_widened'], c['widened_runs'], c['widened_completed'], c['widened_stopped_drive_voltage']])
    rows.append(['all', 'all', totals['default_runs'], totals['default_completed'], totals['stopped_divergence'], totals['stopped_cap_divergence'],
                 totals['stopped_then_completed_widened'], totals['widened_runs'], totals['widened_completed'], totals['widened_stopped_drive_voltage']])
    write('study_outcomes.csv', ['law', 'settings', 'runs_checks_default', 'completed', 'stopped_growing_error', 'stopped_change_cap_held',
                                 'stopped_then_completed_widened', 'runs_checks_widened', 'completed_widened', 'widened_stopped_drive_voltage'], rows)
    sl = np.array(stop_loops)
    print('stops at default checks: loops', sl.min(), 'to', sl.max(), '; at loop 7:', int((sl == 7).sum()),
          '; by loop 12:', int((sl <= 12).sum()), 'of', sl.size)
    # The same case at both settings, where the default run completed.
    same = []
    for b, (j, ps) in jobs.items():
        dflt, o = ps.get('default'), ps.get('opened')
        if dflt and o and dflt['outcome']['completed'] and dflt.get('scored') and o.get('scored'):
            same.append(max(abs(LINES[k](dflt) - LINES[k](o)) for k in LINES))
    print('cases completed at both settings:', len(same), '; largest difference on any line', max(same) if same else None, 'dB')

    # Scores by stage, rig group and law, at each law's defaults, the measured frequency response kept.
    rows = []
    for grp in ('more_controls', 'equal'):
        for v in ('none', 'realistic', 'strong'):
            for law in LAWS:
                for sub, keep in (('all', keep_all), ('not flagged', keep_noflag)):
                    row = [grp, v, law, sub]
                    for line in ('control', 'held_out', 'level', 'over_test', 'stress', 'stress_bias'):
                        st = stats(per_structure(results, law, 'default', v, grp, line, keep))
                        row += [st['n'], f"{st['median']:.2f}", f"{st['q1']:.2f}", f"{st['q3']:.2f}"] if line == 'stress' else [f"{st['median']:.2f}"]
                    rows.append(row)
    write('study_scores.csv', ['rigs', 'structure', 'law', 'structures', 'control_db', 'held_out_db', 'level_db', 'worst_over_test_db',
                               'n', 'stress_db', 'stress_q1', 'stress_q3', 'stress_bias_db'], rows)

    # Paired changes on three lines of the scorecard.
    def change_rows(kind):
        rows = []
        for grp in ('more_controls', 'equal'):
            variants = ('none', 'realistic', 'strong') if kind != 'stage2' else ('realistic', 'strong')
            for v in variants:
                for law in LAWS:
                    subs = [('all', keep_all), ('not flagged', keep_noflag)]
                    if kind == 'stage2':
                        subs += [('member moved in service', keep_moved),
                                 ('member moved, not flagged', lambda s, r, v: keep_moved(s, r, v) and keep_noflag(s, r, v))]
                    for sub, keep in subs:
                        row = [grp, v, law, sub]
                        for line in ('control', 'held_out', 'stress'):
                            if kind == 'stage2':
                                base = lambda s, r, law=law: results.get((s, r, 'none', law, 'default'))
                                d = per_structure(results, law, 'default', v, grp, line, keep, base=base)
                            else:
                                base = lambda s, r, law=law, v=v: results.get((s, r, v, law, 'default'))
                                d = per_structure(results, law, kind, v, grp, line, keep, base=base)
                            st = stats(d)
                            row += ['', '', '', '', '', ''] if st is None else [st['n'], f"{st['median']:+.2f}", f"{st['q1']:+.2f}", f"{st['q3']:+.2f}", st['up'], st['down']]
                        if row[4] != '':
                            rows.append(row)
        return rows
    head = ['rigs', 'structure', 'law', 'structures']
    for line in ('control', 'held_out', 'stress'):
        head += [f'{line}_n', f'{line}_median', f'{line}_q1', f'{line}_q3', f'{line}_up', f'{line}_down']
    write('study_change_linear_to_stage2.csv', head, change_rows('stage2'))
    write('study_change_tuned.csv', head, change_rows('tuned'))
    write('study_change_measured_again.csv', head, change_rows('measured_again'))

    # The same change on each system alone (stress only), for the systems with more control gauges than shakers.
    rows = []
    for r in ('3x12', '6x12', '12x24', '6x6', '12x12'):
        for v in ('realistic', 'strong'):
            for law in LAWS:
                base = lambda s, rr, law=law: results.get((s, rr, 'none', law, 'default'))
                st = stats(per_structure(results, law, 'default', v, group(r), 'stress', rigs=(r,), base=base))
                lin = stats(per_structure(results, law, 'default', 'none', group(r), 'stress', rigs=(r,)))
                rows.append([r, v, law, st['n'], f"{lin['median']:.2f}", f"{st['median']:+.2f}", st['up'], st['down']])
    write('study_change_by_rig.csv', ['rig', 'structure', 'law', 'structures', 'linear_stress_median_db', 'change_median_db', 'up', 'down'], rows)

    # Each law at its defaults on each system alone, linear structure.
    rows = []
    for r in ('3x12', '6x12', '12x24', '6x6', '12x12'):
        for law in LAWS:
            row = [r, law]
            for line in ('control', 'held_out', 'level', 'stress', 'stress_bias'):
                st = stats(per_structure(results, law, 'default', 'none', group(r), line, rigs=(r,)))
                row += [st['n'] if line == 'control' else None, f"{st['median']:.2f}"]
            rows.append([x for x in row if x is not None])
    write('study_scores_by_rig.csv', ['rig', 'law', 'structures', 'control_db', 'held_out_db', 'level_db', 'stress_db', 'stress_bias_db'], rows)

    # Softening only and hardening only, against the same law on the linear structure: systems 6 x 12 and 6 x 6.
    rows = []
    for r in ('6x12', '6x6'):
        for t in TIER:
            for eff, suffix in (('both', ''), ('softening only', '_soft'), ('hardening only', '_hard')):
                for law in LAWS:
                    for sub, keep in (('all', keep_all), ('member moved in service', keep_moved)):
                        row = [r, t, eff, law, sub]
                        for line in ('control', 'held_out', 'stress'):
                            base = lambda s, rr, law=law: results.get((s, rr, 'none', law, 'default'))
                            d = per_structure(results, law, 'default', t + suffix, group(r), line, keep, rigs=(r,),
                                              base=base)
                            st = stats(d)
                            row += [st['n'], f"{st['median']:+.2f}", f"{st['q1']:+.2f}", f"{st['q3']:+.2f}", st['up'], st['down']]
                        rows.append(row)
    write('study_single_effects.csv', ['rig', 'size', 'effects', 'law', 'structures'] + head[4:], rows)


if __name__ == '__main__':
    main()
