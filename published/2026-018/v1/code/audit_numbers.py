"""Write ../data/audit_numbers.csv (in the layout of numbers.csv: key, text, value, source, how) and
../data/audit_verdicts.csv from the audit on the held-back structures: the verdicts of the study's
claims this article cites. Standard library only. Copyright 2026 Kevin Cross. MIT license.

    python audit_numbers.py VERDICTS_CSV R_AUDIT_MD

VERDICTS_CSV is the audit's `make_claims.py check` output; R_AUDIT_MD the audit's report, read only
for its list of the verdicts that turn on the rounding of the stored study quartiles. The claim sets
are those dnw_data.py wrote to ../data (the stepped-sine pair claims, the claims of followed poles
against the Python matrix). The verdicts are the frozen code's and are not changed.
"""
import collections
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
VERDICTS = ('holds', 'weaker', 'does not hold', 'not tested', 'not judged')


def read(path):
    with open(path, newline='') as file:
        return list(csv.DictReader(file))


def join(items):
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1] if items else ''


def main(verdicts_path, report_path):
    verdicts = read(verdicts_path)
    verdict_of = {v['id']: v['verdict'] for v in verdicts}
    out = []

    def add(key, text, value, source, how=''):
        out.append([key, text, value, source, how])

    def counts(key, ids, source):
        c = collections.Counter(verdict_of[i] for i in ids)
        n = len(ids)
        add(f'{key}_n', f'{n:,}', n, source, 'claims')
        for v in VERDICTS:
            k = v.replace(' ', '_')
            add(f'{key}_{k}', f'{c.get(v, 0):,}', c.get(v, 0), 'verdicts.csv (audit)', f'claims whose verdict is {v}')
        h, w, d = c.get('holds', 0), c.get('weaker', 0), c.get('does not hold', 0)
        add(f'{key}_holds_phrase', f"{h:,} {'holds' if h == 1 else 'hold'}", h, 'verdicts.csv (audit)', 'count with its verb')
        add(f'{key}_weaker_phrase', f"{w:,} {'holds' if w == 1 else 'hold'} weaker", w, 'verdicts.csv (audit)', 'count with its verb')
        add(f'{key}_does_not_hold_phrase', f"{d:,} {'does' if d == 1 else 'do'} not hold", d, 'verdicts.csv (audit)', 'count with its verb')
        ids_d = sorted(i for i in ids if verdict_of[i] == 'does not hold')
        add(f'{key}_does_not_hold_ids', join(ids_d), len(ids_d), 'verdicts.csv (audit)', 'ids, does not hold')
        untested = c.get('not tested', 0) + c.get('not judged', 0)
        assert untested == 0, f'{key}: the text says every claim was tested'
        return c

    stepped = read(os.path.join(DATA, 'stepped_pair_claims.csv'))
    stepped_mx = sorted(r['id'] for r in stepped if 'matrix' in (r['law'], r['against']))
    counts('audit_t3_mx', stepped_mx, 'data/stepped_pair_claims.csv')
    fp = sorted(r['id'] for r in read(os.path.join(DATA, 'followed_poles_pair_claims.csv')))
    counts('audit_followed_poles', fp, 'data/followed_poles_pair_claims.csv')

    report = ' '.join(open(report_path).read().split())
    m = re.search(r'The (\d+) are ((?:R\d{4}, )+R\d{4} and R\d{4})', report)
    assert m, 'the report names no rounding verdicts'
    rounding = re.findall(r'R\d{4}', m.group(2))
    assert len(rounding) == int(m.group(1))
    row = {v['id']: v for v in verdicts}
    for i in rounding:
        assert row[i]['verdict'] == 'weaker' and row[i]['audit_median'] in (row[i]['study_q1'], row[i]['study_q3']), i
        assert row[i]['kind'] == 'pair' and ', T4:' in row[i]['text'] and 'Python version' not in row[i]['text'], i
    assert not set(rounding) & (set(stepped_mx) | set(fp)), 'the text says none is among the claims counted here'
    places = max(len(v.split('.')[1]) for r in verdicts for v in (r['study_q1'], r['study_q3']) if '.' in v and 'e' not in v)
    add('audit_rounding_n', str(len(rounding)), len(rounding), 'R_Audit.md', 'verdicts that turn on rounding')
    add('audit_rounding_places', str(places), places, 'verdicts.csv (audit)', 'decimals of the stored quartiles')

    with open(os.path.join(DATA, 'audit_numbers.csv'), 'w', newline='') as file:
        w = csv.writer(file, lineterminator='\n')
        w.writerow(['key', 'text', 'value', 'source', 'how'])
        w.writerows(out)
    with open(os.path.join(DATA, 'audit_verdicts.csv'), 'w', newline='') as file:
        w = csv.writer(file, lineterminator='\n')
        w.writerow(['id', 'kind', 'verdict', 'audit_median', 'audit_n', 'study_median', 'study_q1', 'study_q3'])
        for r in verdicts:
            w.writerow([r[k] for k in ('id', 'kind', 'verdict', 'audit_median', 'audit_n', 'study_median',
                                       'study_q1', 'study_q3')])
    print('wrote audit_numbers.csv', len(out), 'rows; audit_verdicts.csv', len(verdicts), 'rows')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
