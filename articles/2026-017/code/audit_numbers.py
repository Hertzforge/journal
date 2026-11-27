"""Write ../data/audit_numbers.csv and ../data/audit_verdicts.csv from the audit on the held-back
structures: the verdict counts the text quotes, and the held-back readings set beside the study's.
Standard library only. Copyright 2026 Kevin Cross. MIT license.

    python audit_numbers.py CLAIMS_JSON VERDICTS_CSV AUDIT_READINGS_CSV R_AUDIT_MD

CLAIMS_JSON is the study's claims file (beside it, the study's readings.csv, used only to check that
the held-back readings below are computed as `law_results.py` and `law_numbers.py` compute the
study's); VERDICTS_CSV is the audit's `make_claims.py check` output; AUDIT_READINGS_CSV the audit's
readings file in the study's layout; R_AUDIT_MD the audit's report, read only for its list of the
verdicts that turn on the rounding of the stored study quartiles. The verdicts are the frozen code's
and are not changed. Each key of audit_numbers.csv names the file it came from.
"""
import collections
import csv
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
VERDICTS = ('holds', 'weaker', 'does not hold', 'not tested', 'not judged')
# The study's records name the candidate law by the effort's code; these files use its name.
RECORD_LAW = {'k3': 'followed_poles'}
BETTER_HIGHER = {'iec_share': True, 'completion': True, 'worst_over_db': False}


def law_id(name):
    return RECORD_LAW.get(name, name)


def read(path):
    with open(path, newline='') as file:
        return list(csv.DictReader(file))


def pct(a, b):
    return f'{100 * a / b:.0f}' if b else ''


def join(items):
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1] if items else ''


def num(value):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def readings_numbers(rows, prefix):
    """Completions by job and the pooled over-tests, as law_results.py and law_numbers.py compute
    the study's from its readings.csv."""
    out = {}
    jobs = collections.defaultdict(list)
    for r in rows:
        jobs[(r['version'], law_id(r['law']), r['test'])].append(r)
    pool = collections.defaultdict(lambda: [0, 0, 0])
    for (version, law, test), g in jobs.items():
        k = f'{prefix}{version}_{law}_{test}_all'
        done = sum(r['outcome'] == 'completed' for r in g)
        out[f'{k}_runs'] = len(g)
        out[f'{k}_completed'] = done
        out[f'{k}_completed_pct'] = pct(done, len(g))
        have = [w for w in (num(r['worst_over_db']) for r in g) if w is not None]
        kind = 'dwell' if test == 'T4' else 'sweep_step'
        for key in (f'{version}_{kind}', f'{version}_{law}_{kind}'):
            pool[key][0] += len(g)
            pool[key][1] += len(have)
            pool[key][2] += sum(w > 6 for w in have)
    for key, (n, w, o) in pool.items():
        out[f'{prefix}{key}_runs'] = n
        out[f'{prefix}{key}_over_6db'] = o
        out[f'{prefix}{key}_over_6db_pct_of_runs'] = pct(o, n)
        out[f'{prefix}{key}_over_6db_pct_of_scored'] = pct(o, w)
    return out


def main(claims_path, verdicts_path, readings_path, report_path):
    assert 'audit_runs' not in os.path.abspath(claims_path), 'the claims are the study\'s'
    claims = {c['id']: c for c in json.load(open(claims_path))['claims']}
    for c in claims.values():
        for field in ('law', 'against'):
            if field in c:
                c[field] = law_id(c[field])
    verdicts = read(verdicts_path)
    assert {v['id'] for v in verdicts} == set(claims), 'verdicts do not match the claims'
    verdict_of = {v['id']: v['verdict'] for v in verdicts}
    out = []

    def add(key, value, source):
        out.append([key, value, source])

    def counts(key, ids):
        ids = sorted(ids)
        c = collections.Counter(verdict_of[i] for i in ids)
        add(f'{key}_n', len(ids), 'verdicts.csv')
        for v in VERDICTS[:4]:
            add(f"{key}_{v.replace(' ', '_')}", c.get(v, 0), 'verdicts.csv')
        add(f'{key}_holds_pct', pct(c.get('holds', 0), len(ids)), 'verdicts.csv')
        add(f'{key}_does_not_hold_ids', join(i for i in ids if verdict_of[i] == 'does not hold'),
            'verdicts.csv')
        return c

    law_claims = {i for i, c in claims.items() if c['kind'] in ('level', 'pair')}
    counts('law', law_claims)
    for version in ('hertzforge', 'python'):
        counts(f'law_{version}', {i for i in law_claims if claims[i]['version'] == version})
    for kind in ('level', 'pair'):
        counts(kind, {i for i in law_claims if claims[i]['kind'] == kind})
    counts('pair_hertzforge', {i for i in law_claims if claims[i]['kind'] == 'pair'
                               and claims[i]['version'] == 'hertzforge'})
    fp = {i for i in law_claims if 'followed_poles' in (claims[i].get('law'), claims[i].get('against'))}
    counts('followed_poles', fp)
    counts('followed_poles_level', {i for i in fp if claims[i]['kind'] == 'level'})
    counts('followed_poles_pair', {i for i in fp if claims[i]['kind'] == 'pair'})

    def favoured(c):
        law_better = (c['side'] == 'higher') == BETTER_HIGHER[c['reading']]
        return c['law'] if law_better else c['against']
    for test, reading in (('T1', 'worst_over_db'), ('T5', 'completion'), ('T2', 'iec_share')):
        counts(f'followed_poles_favoured_{test}_{reading}',
               {i for i in fp if claims[i]['kind'] == 'pair' and claims[i]['test'] == test
                and claims[i]['reading'] == reading and favoured(claims[i]) == 'followed_poles'})
    counts('followed_poles_favoured', {i for i in fp if claims[i]['kind'] == 'pair'
                                       and favoured(claims[i]) == 'followed_poles'})
    counts('matrix_favoured_over_followed_poles',
           {i for i in fp if claims[i]['kind'] == 'pair' and favoured(claims[i]) == 'matrix'})

    # The ids of each group of paired claims (version, test, law, against, reading), for the text's
    # verdict tokens.
    groups = collections.defaultdict(list)
    for i in sorted(law_claims):
        c = claims[i]
        if c['kind'] == 'pair':
            groups[f"pair_ids_{c['version']}_{c['test']}_{c['law']}_{c['against']}_{c['reading']}"].append(i)
    for key, ids in sorted(groups.items()):
        add(key, ' '.join(ids), 'claims.json')

    level = {i: c for i, c in claims.items() if c['kind'] == 'level'}
    for law in ('matrix', 'steepest_descent', 'secant', 'ratio', 'paired'):
        counts(f'dwell_check_inside_{law}', {i for i, c in level.items() if c['version'] == 'hertzforge'
                                             and c['law'] == law and c['test'] == 'T4'
                                             and c['line'] == 'iec_check_point' and c['side'] == 'inside'})
    for version in ('hertzforge', 'python'):
        counts(f'sweep_step_check_{version}', {i for i, c in level.items() if c['version'] == version
                                               and c['test'] != 'T4' and c['line'] == 'iec_check_point'})
        counts(f'sweep_step_{version}', {i for i, c in level.items() if c['version'] == version
                                         and c['test'] != 'T4'})
    # By job: each law's level claims, by version.
    jobs = sorted({(c['version'], c['law']) for c in level.values()})
    for version, law in jobs:
        counts(f'job_{version}_{law}', {i for i, c in level.items()
                                        if c['version'] == version and c['law'] == law})
        for dwell in (True, False):
            counts(f"job_{version}_{law}_{'dwell' if dwell else 'sweep_step'}",
                   {i for i, c in level.items() if c['version'] == version and c['law'] == law
                    and (c['test'] == 'T4') == dwell})

    # The verdicts that turn on the rounding of the stored study quartiles, as the report lists them.
    report = ' '.join(open(report_path).read().split())
    m = re.search(r'The (\d+) are ((?:R\d{4}, )+R\d{4} and R\d{4})', report)
    assert m, 'the report names no rounding verdicts'
    rounding = re.findall(r'R\d{4}', m.group(2))
    assert len(rounding) == int(m.group(1))
    row = {v['id']: v for v in verdicts}
    for i in rounding:
        assert row[i]['verdict'] == 'weaker' and row[i]['audit_median'] in (row[i]['study_q1'], row[i]['study_q3']), i
    places = max(len(repr(float(c['study'][q])).split('.')[1]) for c in claims.values() for q in ('q1', 'q3')
                 if num(c['study'].get(q)) is not None and 'e' not in repr(float(c['study'][q])))
    law_c = collections.Counter(verdict_of[i] for i in law_claims)
    in_scope = [i for i in rounding if i in law_claims]
    add('rounding_n', len(rounding), 'R_Audit.md')
    add('rounding_ids', join(rounding), 'R_Audit.md')
    add('rounding_places', places, 'claims.json')
    add('rounding_hertzforge_pairs', sum(claims[i]['kind'] == 'pair' and claims[i]['version'] == 'hertzforge'
                                         for i in rounding), 'R_Audit.md')
    add('rounding_tests', join(sorted({claims[i]['test'] for i in rounding})), 'claims.json')
    add('rounding_law_words_holds', law_c['holds'] + len(in_scope), 'verdicts.csv')
    add('rounding_law_words_weaker', law_c['weaker'] - len(in_scope), 'verdicts.csv')
    counts('dwell_other_lines', {i for i, c in level.items() if c['version'] == 'hertzforge'
                                 and c['test'] == 'T4' and c['line'] != 'iec_check_point'})
    # Statements the text makes in words from these counts; stop if the verdicts no longer bear them.
    assert not any(verdict_of[i] == 'does not hold' for i, c in level.items()
                   if c['version'] == 'hertzforge' and c['law'] in ('matrix', 'paired')), 'matrix and paired: none fails'
    assert len(rounding) == sum(claims[i]['kind'] == 'pair' and claims[i]['version'] == 'hertzforge'
                                and claims[i]['test'] == 'T4' for i in rounding), 'the rounding sentence'
    assert not any(verdict_of[i] == 'does not hold' for i, c in level.items()
                   if c['version'] == 'hertzforge' and c['test'] != 'T4'), 'every Hertzforge level not holding is at the dwell'
    assert not any(verdict_of[i] == 'does not hold' for i, c in level.items()
                   if c['test'] != 'T4' and c['line'] == 'iec_check_point'), 'every sweep check-point claim stays outside'
    assert not any(verdict_of[i] == 'does not hold' for i, c in level.items()
                   if c['version'] == 'hertzforge' and c['law'] == 'matrix'), 'no matrix level claim fails'
    assert all(c['system'] == '6x6' for i, c in level.items() if verdict_of[i] == 'does not hold'
               and c['version'] == 'hertzforge' and c['test'] == 'T4' and c['line'] == 'iec_check_point'
               and c['law'] in ('steepest_descent', 'secant')), 'their dwell check-point failures are on 6 x 6'
    all_c = collections.Counter(verdict_of.values())
    untested = all_c['not tested'] + all_c['not judged']
    add('all_not_tested_text', 'Every claim was tested.' if untested == 0 else
        f'{untested:,} claims were not tested.', 'verdicts.csv')
    add('all_n', len(verdict_of), 'verdicts.csv')
    add('all_holds', all_c['holds'], 'verdicts.csv')
    add('all_weaker', all_c['weaker'], 'verdicts.csv')
    add('all_does_not_hold', all_c['does not hold'], 'verdicts.csv')

    # The held-back readings, computed as the study's; checked on the study's own readings first.
    study = readings_numbers(read(os.path.join(os.path.dirname(claims_path), 'readings.csv')), '')
    law_numbers = {r['key']: r['value'] for r in read(os.path.join(DATA, 'law_numbers.csv'))}
    checked = 0
    for key, value in study.items():
        if key in law_numbers:
            assert str(value) == law_numbers[key], (key, value, law_numbers[key])
            checked += 1
    assert checked > 50, checked
    held = readings_numbers(read(readings_path), 'heldout_')
    for key, value in sorted(held.items()):
        add(key, value, 'readings.csv (audit)')
    held_rows = read(readings_path)
    add('heldout_runs_hertzforge', sum(r['version'] == 'hertzforge' for r in held_rows), 'readings.csv (audit)')
    add('heldout_runs_python', sum(r['version'] == 'python' for r in held_rows), 'readings.csv (audit)')

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, 'audit_numbers.csv'), 'w', newline='') as file:
        w = csv.writer(file, lineterminator='\n')
        w.writerow(['key', 'value', 'source'])
        w.writerows(out)
    # Every claim's verdict, with the laws named as in these files (the claim's text is in the claims
    # file under its id).
    with open(os.path.join(DATA, 'audit_verdicts.csv'), 'w', newline='') as file:
        w = csv.writer(file, lineterminator='\n')
        w.writerow(['id', 'kind', 'version', 'law', 'against', 'test', 'reading_or_line', 'side',
                    'verdict', 'audit_median', 'audit_n', 'study_median', 'study_q1', 'study_q3'])
        for v in verdicts:
            c = claims[v['id']]
            w.writerow([v['id'], c['kind'], c['version'], c.get('law', ''), c.get('against', ''),
                        c['test'], c.get('reading', c.get('line', '')), c['side'], v['verdict'],
                        v['audit_median'], v['audit_n'], v['study_median'], v['study_q1'], v['study_q3']])
    print('wrote audit_numbers.csv', len(out), 'rows; audit_verdicts.csv', len(verdicts), 'rows;',
          checked, 'held-back formulas checked on the study')


if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
