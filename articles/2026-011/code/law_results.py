"""The results of the three laws of this article beside the six laws of the earlier study, from the
scorecards of the runs. Writes the data of the results section's figures and tables into ../data.
Reads the scorecards only; it runs nothing and imports no study or scorer code.

    PYTHONDONTWRITEBYTECODE=1 python3 law_results.py six=SIX_CARDS LAW[,LAW]=CARDS [LAW=CARDS ...]
    PYTHONDONTWRITEBYTECODE=1 python3 law_results.py six=AUDIT_CARDS,AUDIT2_CARDS LAW=CARDS ... --audit

Each argument names the laws to take from a folder of scorecards. `six` stands for the six laws of the
earlier study; its folder is `cards/main` of the record "Hertzforge Open Benchmark Set, MIMO Random
Suite: Results of the Control Law Study and Its Independent Audit", version 0.2
(DOI 10.5281/zenodo.24310746), unpacked. A folder may hold scorecards of other laws; only the laws
named for it are read from it. Several folders for one name are joined with commas.
The three laws' folders are `cards/main` and, with --audit, `cards/held_back` of the record "Hertzforge
Open Benchmark Set, MIMO Random Suite: Results of the Study of Independent Drive Laws and a Broyden
Congruence Law" (DOI 10.5281/zenodo.24407972), unpacked.

Without --audit the files are written as `study_*` and cover structures 0 to 9. With --audit they are
written as `audit_*` and cover the held-back structures 20, 21, 22, 23 and 52 on the 6 x 12 and 6 x 6
systems, each law at its defaults.

Rules, the same as the earlier study's:
- The result of a case is its run with the checks widened where that run exists and completed, else
  its completed run with the checks at their defaults. A stopped run is never a result.
- Systems with as many shakers as control gauges (6 x 6, 12 x 12) and systems with more control gauges
  than shakers (3 x 12, 6 x 12, 12 x 24) are never pooled. A structure's value in a group is the mean
  over the systems of that group; medians and quartiles (numpy, linear) are over structures.
- A change, or a difference between two laws, is taken on the same structure and system, then averaged
  over the group's systems. Counts "up" and "down" (or "lower" and "higher") are structures on which it
  exceeds 0.2 dB either way.
- "Flagged" structures are the ones the benchmark marks (structure 5, driven above 30 g RMS; structure
  1 on the systems with as many shakers as control gauges, where a member would yield at full level).

Copyright 2026 Kevin Cross and Norman Hunter. MIT license.
"""
import csv
import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np

AUDIT = '--audit' in sys.argv[1:]
PREFIX = 'audit' if AUDIT else 'study'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
SIX = ['pinv_closed', 'pinv_open', 'shape_svd', 'buzz_match', 'min_drive', 'band_average']
NEW = ['independent', 'nearly_independent', 'broyden_congruence']
LAWS = SIX + NEW
STRUCTURES = (20, 21, 22, 23, 52) if AUDIT else tuple(range(10))
SYSTEMS = ('6x12', '6x6') if AUDIT else ('3x12', '6x12', '12x24', '6x6', '12x12')
TWO = ('6x12', '6x6')                      # the systems the other settings of a law were run on
STAGES = ('none', 'realistic', 'strong')   # the linear structure, and the two sizes of the level-dependent one
SQUARE = ('6x6', '12x12')
FLOOR = 0.2
SETTINGS = ('default', 'tuned', 'published', 'open', 'weighted')
LINES = {
    'control': lambda d: d['card']['c_b3_rms'],         # control gauges, per-gauge RMS dB error in 1/3-octave bands
    'held_out': lambda d: d['card']['h_b3_rms'],        # held-out gauges, the same
    'level': lambda d: d['card']['level_mean'],         # mean dB error over gauges and bands (signed)
    'over_test': lambda d: d['card']['worst_over_b3'],  # worst band over its target, dB
    'stress': lambda d: d['stress']['rms'],             # RMS over elements of the dB error of element RMS stress
    'stress_bias': lambda d: d['stress']['bias'],       # mean of the same (signed)
}
STOPS = {'divergence': 'stopped_growing_error', 'cap_divergence': 'stopped_change_cap_held'}


def group(system):
    return 'equal' if system in SQUARE else 'more_controls'


def flagged(structure, system):
    return structure == 5 or (structure == 1 and system in SQUARE)


def sources():
    """{law: [folders]} from the command line."""
    src = {}
    for a in sys.argv[1:]:
        if a == '--audit':
            continue
        if '=' not in a:
            sys.exit(__doc__)
        names, folders = a.split('=', 1)
        for n in names.split(','):
            for law in (SIX if n == 'six' else [n]):
                if law not in LAWS:
                    sys.exit(f'unknown law {law!r}')
                if law in src:
                    sys.exit(f'{law} is given twice')
                src[law] = folders.split(',')
    if not src:
        sys.exit(__doc__)
    return src


def load(src):
    """results[(structure, system, stage, law, setting)] = card; jobs[base id] = (job, {'default': card, 'opened': card})."""
    by_folder = defaultdict(set)
    for law, folders in src.items():
        for f in folders:
            by_folder[f].add(law)
    passes = defaultdict(dict)
    for folder, laws in sorted(by_folder.items()):
        files = sorted(glob.glob(os.path.join(folder, '*.json')))
        if not files:
            sys.exit(f'no scorecards in {folder}')
        for p in files:
            d = json.load(open(p))
            j = d['job']
            if (j['law'] not in laws or j['seed'] not in STRUCTURES or j['rig'] not in SYSTEMS or j['variant'] not in STAGES
                    or j['frf'] != 'hold' or j['setting'] not in SETTINGS or (AUDIT and j['setting'] != 'default')):
                continue
            key = (j['law'], j['base_id'])
            which = 'opened' if j['protections'] == 'opened' else 'default'
            if which in passes[key]:
                sys.exit(f'{j["base_id"]} ({which}) is in two folders')
            passes[key][which] = d
    results, jobs = {}, {}
    for key, ps in passes.items():
        o, dflt = ps.get('opened'), ps.get('default')
        j = (o or dflt)['job']
        jobs[key] = (j, ps)
        pick = None
        if o is not None and o['outcome']['completed'] and o.get('scored'):
            pick = o
        elif dflt is not None and dflt['outcome']['completed'] and dflt.get('scored'):
            pick = dflt
        if pick is not None:
            results[(j['seed'], j['rig'], j['variant'], j['law'], j['setting'])] = pick
    return results, jobs


def write(name, header, rows):
    with open(os.path.join(OUT, f'{PREFIX}_{name}'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print('wrote', f'{PREFIX}_{name}', len(rows), 'rows')


def per_structure(results, law, setting, stage, grp, line, systems=SYSTEMS, keep=lambda s, r: True, base=None):
    """{structure: mean over the group's systems of the line (or of the line less the base's)}."""
    acc = defaultdict(list)
    for (s, r, v, l, a), d in results.items():
        if l != law or a != setting or v != stage or r not in systems or group(r) != grp or not keep(s, r):
            continue
        x = LINES[line](d)
        if base is not None:
            b = base(s, r, v)
            if b is None:
                continue
            x = x - LINES[line](b)
        acc[s].append(x)
    return {s: float(np.mean(x)) for s, x in acc.items()}


def stats(vals):
    v = np.array(list(vals.values()))
    if v.size == 0:
        return None
    return dict(n=int(v.size), median=float(np.median(v)), q1=float(np.percentile(v, 25)), q3=float(np.percentile(v, 75)),
                mean=float(np.mean(v)), up=int((v > FLOOR).sum()), down=int((v < -FLOOR).sum()))


def main():
    os.makedirs(OUT, exist_ok=True)
    src = sources()
    results, jobs = load(src)
    laws = [l for l in LAWS if l in src]
    new = [l for l in NEW if l in src]
    all_lines = ('control', 'held_out', 'level', 'over_test', 'stress', 'stress_bias')
    keep_noflag = lambda s, r: not flagged(s, r)

    # 1. Scores at each law's defaults, by group of systems and stage.
    rows, by_structure = [], []
    for grp in ('more_controls', 'equal'):
        for v in STAGES:
            for law in laws:
                for sub, keep in (('all', lambda s, r: True), ('not flagged', keep_noflag)):
                    row, n = [grp, v, law, sub], None
                    for line in all_lines:
                        st = stats(per_structure(results, law, 'default', v, grp, line, keep=keep))
                        if st is None:
                            break
                        n = st['n']
                        row += [f"{st['median']:.2f}", f"{st['q1']:.2f}", f"{st['q3']:.2f}"]
                    else:
                        rows.append(row[:4] + [n] + row[4:])
                vals = {line: per_structure(results, law, 'default', v, grp, line) for line in all_lines}
                for s in sorted(vals['control']):
                    by_structure.append([grp, v, law, s] + [f'{vals[line][s]:.3f}' for line in all_lines])
    head = ['systems', 'structure_kind', 'law', 'structures', 'n']
    for line in all_lines:
        head += [f'{line}_db', f'{line}_q1', f'{line}_q3']
    write('scores.csv', head, rows)
    write('scores_by_structure.csv', ['systems', 'structure_kind', 'law', 'structure'] + [f'{line}_db' for line in all_lines], by_structure)

    # 2. What the controller's checks did: runs at the default checks, and with them widened.
    rows = []
    for law in laws:
        for a in SETTINGS:
            c = defaultdict(int)
            for (l, _), (j, ps) in jobs.items():
                if l != law or j['setting'] != a:
                    continue
                dflt, o = ps.get('default'), ps.get('opened')
                if dflt is not None:
                    c['default_runs'] += 1
                    if dflt['outcome']['completed']:
                        c['default_completed'] += 1
                    else:
                        c[STOPS.get(dflt['outcome']['stop']['guard'], 'stopped_other')] += 1
                        if o is not None and o['outcome']['completed']:
                            c['stopped_then_completed_widened'] += 1
                if o is not None:
                    c['widened_runs'] += 1
                    c['widened_completed' if o['outcome']['completed'] else 'widened_stopped'] += 1
            if c['default_runs'] or c['widened_runs']:
                rows.append([law, a] + [c[k] for k in ('default_runs', 'default_completed', 'stopped_growing_error', 'stopped_change_cap_held',
                                                      'stopped_other', 'stopped_then_completed_widened', 'widened_runs',
                                                      'widened_completed', 'widened_stopped')])
    write('outcomes.csv', ['law', 'settings', 'runs_checks_default', 'completed', 'stopped_growing_error', 'stopped_change_cap_held',
                           'stopped_other', 'stopped_then_completed_widened', 'runs_checks_widened', 'completed_widened',
                           'widened_stopped'], rows)

    # 3. Each new law against each other law at their defaults: the difference on the same structure and system.
    #    pairs.csv is over every system run; pairs_two.csv (the study only) is over the 6 x 12 and 6 x 6 systems alone,
    #    the systems the held-back sample was run on, so a study number can be set beside its held-back counterpart.
    head = ['systems', 'structure_kind', 'law', 'against']
    for line in ('control', 'held_out', 'stress'):
        head += [f'{line}_n', f'{line}_median', f'{line}_q1', f'{line}_q3', f'{line}_lower', f'{line}_higher']
    for name, systems in (('pairs.csv', SYSTEMS),) + ((('pairs_two.csv', TWO),) if not AUDIT else ()):
        rows = []
        for grp in ('more_controls', 'equal'):
            for v in STAGES:
                for a in new:
                    for b in laws:
                        if b == a or (b in new and new.index(b) < new.index(a)):
                            continue
                        row = [grp, v, a, b]
                        for line in ('control', 'held_out', 'stress'):
                            base = lambda s, r, vv, b=b: results.get((s, r, vv, b, 'default'))
                            st = stats(per_structure(results, a, 'default', v, grp, line, systems=systems, base=base))
                            row += ['', '', '', '', '', ''] if st is None else [st['n'], f"{st['median']:+.2f}", f"{st['q1']:+.2f}",
                                                                               f"{st['q3']:+.2f}", st['down'], st['up']]
                        if row[4] != '':
                            rows.append(row)
        write(name, head, rows)

    if AUDIT:
        return

    # 4. The other settings of the new laws (tuned, the published form, the open form, the target weighting) on the
    #    6 x 12 and 6 x 6 systems: each setting's own scores, and its change from the law's defaults.
    rows, changes = [], []
    for grp in ('more_controls', 'equal'):
        for v in STAGES:
            for law in laws:
                for a in SETTINGS:
                    row, n = [grp, v, law, a], None
                    for line in all_lines:
                        st = stats(per_structure(results, law, a, v, grp, line, systems=TWO))
                        if st is None:
                            break
                        n = st['n']
                        row += [f"{st['median']:.2f}", f"{st['q1']:.2f}", f"{st['q3']:.2f}"]
                    else:
                        rows.append(row[:4] + [n] + row[4:])
                    if a == 'default':
                        continue
                    base = lambda s, r, vv, law=law: results.get((s, r, vv, law, 'default'))
                    row = [grp, v, law, a]
                    for line in ('control', 'held_out', 'level', 'stress'):
                        st = stats(per_structure(results, law, a, v, grp, line, systems=TWO, base=base))
                        row += ['', '', '', '', '', ''] if st is None else [st['n'], f"{st['median']:+.2f}", f"{st['q1']:+.2f}",
                                                                           f"{st['q3']:+.2f}", st['up'], st['down']]
                    if row[4] != '':
                        changes.append(row)
    head = ['systems', 'structure_kind', 'law', 'settings', 'n']
    for line in all_lines:
        head += [f'{line}_db', f'{line}_q1', f'{line}_q3']
    write('settings_scores.csv', head, rows)
    head = ['systems', 'structure_kind', 'law', 'settings']
    for line in ('control', 'held_out', 'level', 'stress'):
        head += [f'{line}_n', f'{line}_median', f'{line}_q1', f'{line}_q3', f'{line}_up', f'{line}_down']
    write('settings_change.csv', head, changes)

    # What was read, for the record beside the files.
    counts = defaultdict(int)
    for (l, _), (j, ps) in jobs.items():
        counts[(l, j['setting'])] += len(ps)
    print('scorecards read:', ', '.join(f'{l} {a} {n}' for (l, a), n in sorted(counts.items())))
    print('results:', len(results), 'cases of', len(jobs))


if __name__ == '__main__':
    main()
