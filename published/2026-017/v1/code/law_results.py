"""Write the law files of ../data that the laws article's figures and numbers read. NumPy only.
Copyright 2026 Kevin Cross. MIT license.

    python -I law_results.py STUDY_RUNS PROBLEMS

STUDY_RUNS is the study's folder of run sets (`study`, `study_py`, `study_defaults`,
`study_py_defaults`, `study_repeat_1` to `_3`, `study_py_repeat_1` to `_3`, and `claims`, which
holds the frozen `readings.csv` and `claims.json`). PROBLEMS is the suite's problem folders, read
only for the suite's format version. It runs nothing, imports no suite or scorer code, and reads no
audit run.
"""
import collections
import csv
import glob
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
# The study's records (readings.csv, claims.json, the run folders) name the candidate law by its
# effort code; these files and the article use its name. ../data/README.md maps the two.
RECORD_LAW = {'k3': 'followed_poles'}
LAW_ORDER = ['matrix', 'paired', 'ratio', 'steepest_descent', 'secant', 'followed_poles']
TEST_ORDER = ['T1', 'T2', 'T3', 'T4', 'T5', 'L1']
TIERS = ['linear', 'realistic', 'strong']
READINGS = ['iec_share', 'worst_over_db', 'completion']
LINES = ['iec_check_point', 'iec_reference_point', 'mil_composite', 'mil_average_individual',
         'mil_maxi_individual']
# For each reading, the side that is better for the law named first.
BETTER = {'iec_share': 'higher', 'completion': 'higher', 'worst_over_db': 'lower'}


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


def num(value):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if np.isfinite(x) else None


def r4(x):
    return '' if x is None or (isinstance(x, float) and not np.isfinite(x)) else round(float(x), 4)


def tier(kind):
    return kind.split('_')[0]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as file:
        for block in iter(lambda: file.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def quart(values):
    v = [x for x in values if x is not None]
    if not v:
        return None, None, None
    q = np.percentile(v, [25, 50, 75])
    return float(q[0]), float(q[1]), float(q[2])


def card_readings(card):
    """The claims rule's three readings of one card, as `sine/make_claims.py` states them: the IEC
    share is the share inside times the coverage (1 for a completed run) and 0 for an unscored run;
    the worst over-test is missing for an unscored run."""
    comp = card['completion']
    coverage = float(comp.get('coverage') or 0.0)
    done = comp['outcome'] == 'completed'
    out = {'outcome': comp['outcome'], 'iec_share': 0.0, 'worst_over_db': None,
           'completion': 1.0 if done else coverage}
    if card.get('scored'):
        out['iec_share'] = float(card['amplitude']['iec_check_point']['share_inside']) * (1.0 if done else coverage)
        out['worst_over_db'] = card['resonances'].get('worst_db')
    return out


def law_id(name):
    return RECORD_LAW.get(name, name)


def job_id(job):
    """A run folder's job (`T1__k3`) with the law named as in these files."""
    test, sep, law = job.partition('__')
    return f'{test}{sep}{law_id(law)}' if sep else job


def cards(folder):
    out = {}
    for path in glob.glob(os.path.join(folder, '*', '*', 'card.json')):
        structure = os.path.basename(os.path.dirname(os.path.dirname(path)))
        job = os.path.basename(os.path.dirname(path))
        out[(structure, job_id(job))] = json.load(open(path))
    return out


def main(runs, problems):
    claims_dir = os.path.join(runs, 'claims')
    rd = read_csv(os.path.join(claims_dir, 'readings.csv'))
    claims_doc = json.load(open(os.path.join(claims_dir, 'claims.json')))
    claims = claims_doc['claims']
    for r in rd:
        r['law'] = law_id(r['law'])
    for c in claims:
        for field in ('law', 'against'):
            if field in c:
                c[field] = law_id(c[field])

    # Scope: what was scored, with which files.
    formats = collections.Counter(json.load(open(p)).get('format')
                                  for p in glob.glob(os.path.join(problems, '*', 'problem.json')))
    scorer = collections.Counter()
    for name in ('study', 'study_py'):
        for c in cards(os.path.join(runs, name)).values():
            scorer[(c['scorer']['version'], c['scorer']['sha256'])] += 1
    scope = [['problems', sum(formats.values()), 'problem folders'],
             ['problem_format', ';'.join(f'{k}' for k in formats), 'problem.json format'],
             ['readings_rows', len(rd), 'readings.csv rows'],
             ['readings_sha256', sha256(os.path.join(claims_dir, 'readings.csv')), ''],
             ['claims_sha256', sha256(os.path.join(claims_dir, 'claims.json')), ''],
             ['claims_schema', claims_doc['schema'], ''],
             ['claims_rule_sha256', claims_doc['rule']['sha256'], 'sine/make_claims.py'],
             ['claims', len(claims), 'every claim'],
             ['claims_late', len(claims_doc.get('late', [])), 'claims added after the freeze']]
    for kind in ('level', 'pair', 'effect'):
        scope.append([f'claims_{kind}', sum(c['kind'] == kind for c in claims), ''])
    scope.append(['claims_followed_poles', sum('admitted_after_screen' in c for c in claims),
                  'claims carrying admitted_after_screen'])
    scope.append(['claims_law', sum(c['kind'] != 'effect' for c in claims), 'level and pair claims'])
    for reading, threshold in claims_doc['rule']['thresholds'].items():
        scope.append([f'threshold_{reading}', threshold, 'claims rule'])
    for (version, sha), n in scorer.items():
        scope.append(['scorer_version', version, f'{n} cards of study and study_py'])
        scope.append(['scorer_sha256', sha, ''])
    for version in ('hertzforge', 'python'):
        v = [r for r in rd if r['version'] == version]
        scope.append([f'runs_{version}', len(v), 'readings.csv'])
        for outcome, n in sorted(collections.Counter(r['outcome'] for r in v).items()):
            scope.append([f'runs_{version}_{outcome}', n, 'readings.csv'])
        scope.append([f'runs_{version}_unscored', sum(r['scored'] != '1' for r in v), 'readings.csv'])
    structures = sorted({r['structure'] for r in rd})
    scope.append(['structures', len(structures), 'readings.csv'])
    scope.append(['structure_numbers', ' '.join(str(x) for x in sorted({int(r['seed']) for r in rd})),
                  'readings.csv seeds'])
    for t in TEST_ORDER:
        scope.append([f'structures_{t}', len({r['structure'] for r in rd if r['test'] == t}), ''])
    cells = collections.defaultdict(set)
    for r in rd:
        cells[r['test']].add((r['system'], r['kind']))
    for t in TEST_ORDER:
        scope.append([f'cells_{t}', len(cells[t]), 'system and structure kind'])
    write_csv('law_scope.csv', ['key', 'value', 'note'], scope)

    # Readings by version, law, test and tier, and pooled over the tiers.
    groups = collections.defaultdict(list)
    for r in rd:
        groups[(r['version'], r['law'], r['test'], tier(r['kind']))].append(r)
        groups[(r['version'], r['law'], r['test'], 'all')].append(r)
    table = []
    for key in sorted(groups, key=lambda k: (k[0], LAW_ORDER.index(k[1]), TEST_ORDER.index(k[2]),
                                             (TIERS + ['all']).index(k[3]))):
        g = groups[key]
        n = len(g)
        oc = collections.Counter(r['outcome'] for r in g)
        row = list(key) + [n, oc['completed'], oc['aborted'], oc['held_by_identification'],
                           oc['law_fault'], r4(oc['completed'] / n)]
        for reading in READINGS:
            q1, med, q3 = quart([num(r[reading]) for r in g])
            row += [r4(med), r4(q1), r4(q3)]
        worst = [num(r['worst_over_db']) for r in g]
        have = [w for w in worst if w is not None]
        row += [len(have), sum(w > 3 for w in have), sum(w > 6 for w in have),
                r4(sum(w > 6 for w in have) / n), r4(max(have) if have else None)]
        exc = [num(r['excursion_iec_check_point']) for r in g]
        row += [sum(e is not None and e <= 0 for e in exc), r4(sum(e is not None and e <= 0 for e in exc) / n)]
        table.append(row)
    header = ['version', 'law', 'test', 'tier', 'runs', 'completed', 'aborted', 'held',
              'law_fault', 'share_completed']
    for reading in READINGS:
        header += [f'{reading}_median', f'{reading}_q1', f'{reading}_q3']
    header += ['with_worst_reading', 'worst_over_3db', 'worst_over_6db', 'share_over_6db_of_runs',
               'worst_over_max_db', 'inside_check_point', 'share_inside_check_point_of_runs']
    write_csv('law_readings.csv', header, table)

    # Safety, by version, law and test: every run's worst over-test, where the largest was.
    safety = []
    for key in sorted({k[:3] for k in groups},
                      key=lambda k: (k[0], LAW_ORDER.index(k[1]), TEST_ORDER.index(k[2]))):
        g = groups[key + ('all',)]
        have = [(num(r['worst_over_db']), r['structure']) for r in g if num(r['worst_over_db']) is not None]
        top = max(have) if have else (None, '')
        safety.append(list(key) + [len(g), len(have), sum(w > 1.5 for w, _ in have),
                                   sum(w > 3 for w, _ in have), sum(w > 6 for w, _ in have),
                                   sum(w > 12 for w, _ in have), r4(top[0]), top[1]])
    write_csv('law_safety.csv', ['version', 'law', 'test', 'runs', 'with_reading', 'over_1_5db',
                                 'over_3db', 'over_6db', 'over_12db', 'largest_db',
                                 'largest_structure'], safety)
    write_csv('law_worst_runs.csv', ['version', 'law', 'test', 'tier', 'structure', 'worst_over_db',
                                     'outcome'],
              [[r['version'], r['law'], r['test'], tier(r['kind']), r['structure'],
                r4(num(r['worst_over_db'])), r['outcome']]
               for r in rd if num(r['worst_over_db']) is not None])

    # Level claims: one row a law, cell and line.
    level = []
    for c in claims:
        if c['kind'] != 'level':
            continue
        s = c['study']
        level.append([c['id'], c['version'], c['law'], c['test'], c['system'], c['structure_kind'],
                      c['line'], c['side'], r4(s['median']), s['n'], s.get('unscored', 0),
                      'yes' if 'admitted_after_screen' in c else ''])
    write_csv('law_level_claims.csv', ['id', 'version', 'law', 'test', 'system', 'kind', 'line',
                                       'side', 'median_worst_excursion_db', 'n', 'unscored',
                                       'admitted_after_screen'], level)
    # Their counts: cells inside each line, by law and test.
    count = collections.defaultdict(lambda: [0, 0, []])
    for row in level:
        k = (row[1], row[2], row[3], row[6])
        count[k][1] += 1
        if row[7] == 'inside':
            count[k][0] += 1
            count[k][2].append(row[0])
    write_csv('law_level_counts.csv', ['version', 'law', 'test', 'line', 'cells_inside', 'cells',
                                       'ids_inside'],
              [list(k) + [v[0], v[1], ' '.join(v[2])] for k, v in
               sorted(count.items(), key=lambda kv: (kv[0][0], LAW_ORDER.index(kv[0][1]),
                                                     TEST_ORDER.index(kv[0][2]), LINES.index(kv[0][3])))])

    # The same counts split by the system's shape: square (as many shakers as controls) or more
    # controls than shakers.
    shape = collections.defaultdict(lambda: [0, 0, [], []])
    for row in level:
        controls, drives = row[4].split('x')
        k = (row[1], row[2], row[3], row[6], 'square' if controls == drives else 'more_controls')
        shape[k][1] += 1
        shape[k][2 if row[7] == 'inside' else 3].append(row[0])
        if row[7] == 'inside':
            shape[k][0] += 1
    write_csv('law_level_by_shape.csv', ['version', 'law', 'test', 'line', 'shape', 'cells_inside',
                                         'cells', 'ids_inside', 'ids_outside'],
              [list(k) + [v[0], v[1], ' '.join(v[2]), ' '.join(v[3])] for k, v in
               sorted(shape.items(), key=lambda kv: (kv[0][0], LAW_ORDER.index(kv[0][1]),
                                                     TEST_ORDER.index(kv[0][2]), LINES.index(kv[0][3]), kv[0][4]))])

    # Pair claims: one row a claim, with the law the claim favours.
    pairs = []
    for c in claims:
        if c['kind'] != 'pair':
            continue
        s = c['study']
        favours = c['law'] if c['side'] == BETTER[c['reading']] else c['against']
        pairs.append([c['id'], c['version'], c['test'], c['law'], c['against'], c['reading'],
                      c['side'], favours, c['system'], c['structure_kind'], r4(s['median']),
                      r4(s['q1']), r4(s['q3']), s['higher'], s['lower'], s['n_valid'], s['n'],
                      'yes' if 'admitted_after_screen' in c else ''])
    write_csv('law_pair_claims.csv', ['id', 'version', 'test', 'law', 'against', 'reading', 'side',
                                      'favours', 'system', 'kind', 'median', 'q1', 'q3', 'higher',
                                      'lower', 'n_valid', 'n', 'admitted_after_screen'], pairs)
    # Their counts: for each pair of laws on a test and reading, the cells each law is favoured in.
    pc = collections.defaultdict(lambda: {'first': [], 'second': []})
    for row in pairs:
        k = (row[1], row[2], row[3], row[4], row[5])
        pc[k]['first' if row[7] == row[3] else 'second'].append(row[0])
    tested = collections.defaultdict(set)
    for r in rd:
        tested[(r['version'], r['test'], r['law'])].add((r['system'], r['kind']))
    pair_counts = []
    for version, test in sorted({(r['version'], r['test']) for r in rd},
                                key=lambda k: (k[0], TEST_ORDER.index(k[1]))):
        laws = [law for law in LAW_ORDER if (version, test, law) in tested]
        for i, a in enumerate(laws):
            for b in laws[i + 1:]:
                ncell = len(tested[(version, test, a)] & tested[(version, test, b)])
                for reading in READINGS:
                    v = pc[(version, test, a, b, reading)]
                    pair_counts.append([version, test, a, b, reading, ncell, len(v['first']),
                                        len(v['second']), ncell - len(v['first']) - len(v['second']),
                                        ' '.join(v['first']), ' '.join(v['second'])])
    write_csv('law_pair_counts.csv', ['version', 'test', 'law', 'against', 'reading', 'cells',
                                      'cells_favour_law', 'cells_favour_against', 'cells_no_claim',
                                      'ids_favour_law', 'ids_favour_against'], pair_counts)

    # followed_poles against the Python matrix, cell by cell: the paired median difference
    # (followed_poles less matrix)
    # on every reading, with the claim where the rule made one.
    py = collections.defaultdict(dict)
    for r in rd:
        if r['version'] == 'python':
            py[(r['test'], r['system'], r['kind'])].setdefault(r['structure'], {})[r['law']] = r
    claim_at = {(c['test'], c['system'], c['structure_kind'], c['reading']): c for c in claims
                if c['kind'] == 'pair' and c['version'] == 'python' and c['against'] == 'followed_poles'}
    fp_rows, mismatch = [], 0
    for (test, system, kind), by_structure in sorted(py.items(), key=lambda kv: (
            TEST_ORDER.index(kv[0][0]), kv[0][1], kv[0][2])):
        for reading in READINGS:
            d = []
            for s in by_structure.values():
                a, b = num(s.get('matrix', {}).get(reading)), num(s.get('followed_poles', {}).get(reading))
                if a is not None and b is not None:
                    d.append(b - a)
            med = float(np.median(d)) if d else None
            c = claim_at.get((test, system, kind, reading))
            if c and med is not None and abs(-c['study']['median'] - med) > 1e-6:
                mismatch += 1
            fp_favoured = ''
            if c:
                fp_favoured = 'followed_poles' if (c['side'] != BETTER[reading]) else 'matrix'
            fp_rows.append([test, system, kind, tier(kind), reading, len(d), r4(med),
                           c['id'] if c else '', fp_favoured])
    print('followed_poles medians that differ from their claim:', mismatch)
    write_csv('law_followed_poles_cells.csv', ['test', 'system', 'kind', 'tier', 'reading', 'pairs',
                                               'median_followed_poles_less_matrix', 'claim',
                                               'claim_favours'], fp_rows)

    # The stepped sine: where each law's run ended (cards of the study of record).
    study = cards(os.path.join(runs, 'study'))
    kind_of = {r['structure']: r['kind'] for r in rd}
    steps = []
    for law in ('matrix', 'paired', 'ratio'):
        for t in TIERS + ['all']:
            g = [c for (s, job), c in study.items() if job == f'T3__{law}' and
                 (t == 'all' or tier(kind_of[s]) == t)]
            oc = collections.Counter(c['completion']['outcome'] for c in g)
            ab = [c['completion'] for c in g if c['completion']['outcome'] == 'aborted']
            rung = collections.Counter(a['at_level_db'] for a in ab)
            guards = collections.Counter(a['guard'] for a in ab)
            cov = [a.get('coverage') or 0.0 for a in ab]
            steps.append([law, t, len(g), oc['completed'], oc['aborted'], oc['held_by_identification'],
                          oc['law_fault']] + [rung.get(x, 0) for x in (-12.0, -9.0, -6.0, -3.0, 0.0)] +
                         [';'.join(f'{k}:{v}' for k, v in guards.items()),
                          r4(float(np.median(cov)) if cov else None)])
    write_csv('law_steps.csv', ['law', 'tier', 'runs', 'completed', 'aborted', 'held', 'law_fault',
                                'aborted_at_m12db', 'aborted_at_m9db', 'aborted_at_m6db',
                                'aborted_at_m3db', 'aborted_at_0db', 'guards',
                                'median_coverage_of_aborts'], steps)

    # Check: the cards of record give readings.csv's readings.
    check = 0
    by_run = {(r['structure'], f"{r['test']}__{r['law']}"): r for r in rd if r['version'] == 'hertzforge'}
    for key, c in study.items():
        r, got = by_run.get(key), card_readings(c)
        if r is None or got is None:
            continue
        for reading in READINGS:
            a, b = num(r[reading]), got[reading]
            if (a is None) != (b is None) or (a is not None and abs(a - b) > 1e-9):
                check += 1
    print('card readings that differ from readings.csv:', check)

    # The default protections and the repeats, against the runs of record.
    def compare(base_set, other_set, label):
        base, other = cards(os.path.join(runs, base_set)), cards(os.path.join(runs, other_set))
        out = []
        for key, c in sorted(other.items()):
            b = base.get(key)
            if b is None:
                continue
            x, y = card_readings(b), card_readings(c)
            row = [label, key[0], key[1], b['completion']['outcome'], c['completion']['outcome']]
            for reading in READINGS:
                row.append(r4(None if x is None or y is None or x[reading] is None or y[reading] is None
                              else y[reading] - x[reading]))
            out.append(row)
        return out
    header = ['set', 'structure', 'job', 'outcome_of_record', 'outcome'] + [f'{r}_less_record' for r in READINGS]
    defaults = compare('study', 'study_defaults', 'hertzforge') + compare('study_py', 'study_py_defaults', 'python')
    write_csv('law_defaults.csv', header, defaults)
    summary = collections.defaultdict(collections.Counter)
    for row in defaults:
        test = row[2].split('__')[0]
        kind = 'dwell' if test == 'T4' else 'sweep_or_step'
        for k in (row[0], f'{row[0]}_{kind}'):
            summary[k]['runs'] += 1
            summary[k][row[4]] += 1
            summary[k]['record_' + row[3]] += 1
            if row[3] == 'completed' and row[4] != 'completed':
                summary[k]['completed_on_record_stopped_at_defaults'] += 1
    keys = ['runs', 'completed', 'stopped_by_protective_default', 'record_completed',
            'completed_on_record_stopped_at_defaults']
    write_csv('law_defaults_summary.csv', ['set'] + keys,
              [[k] + [v[x] for x in keys] for k, v in sorted(summary.items())])
    repeats = []
    for k in (1, 2, 3):
        repeats += compare('study', f'study_repeat_{k}', f'hertzforge_repeat_{k}')
        repeats += compare('study_py', f'study_py_repeat_{k}', f'python_repeat_{k}')
    write_csv('law_repeats.csv', header, repeats)
    out = []
    for version in ('hertzforge', 'python'):
        g = [row for row in repeats if row[0].startswith(version)]
        row = [version, len(g), len({(r[1], r[2]) for r in g}), sum(r[3] != r[4] for r in g)]
        for k, reading in enumerate(READINGS):
            v = sorted(abs(r[5 + k]) for r in g if r[5 + k] != '')
            row += [len(v), sum(x == 0 for x in v), r4(float(np.median(v)) if v else None),
                    r4(v[-1] if v else None),
                    sum(x > claims_doc['rule']['thresholds'][reading] for x in v)]
        out.append(row)
    head = ['version', 'repeat_runs', 'jobs', 'outcome_changed']
    for reading in READINGS:
        head += [f'{reading}_{x}' for x in ('n', 'equal', 'median_abs_change', 'largest_abs_change',
                                            'beyond_threshold')]
    write_csv('law_repeats_summary.csv', head, out)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
