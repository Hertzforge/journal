"""Fill the article's audit slots from the audit's verdicts and readings. Copyright 2026 Kevin Cross.
MIT license.

    python3 audit_fill.py CLAIMS_JSON VERDICTS_CSV AUDIT_READINGS_CSV [--report R_AUDIT_MD]
        [--data DIR] [--apply SOURCE] [--out ARTICLE]

VERDICTS_CSV is the output of `make_claims.py check` on the held-back structures (columns id,
kind, verdict, audit_median, audit_n, study_median, study_q1, study_q3, text); AUDIT_READINGS_CSV
is the audit's readings file in the study's layout; R_AUDIT_MD is the audit's report, read only for
the list of verdicts that turn on the rounding of the stored quartiles. Writes DIR/audit_numbers.csv
(key, value, text) with the text of every slot, and the verdicts to DIR/audit_verdicts.csv for
Figure 8 (without the claims' text, which names the laws). With --apply, writes ARTICLE (default
../article.md) from SOURCE (code/article_src.md) with every `[AUDIT: key ...]` slot replaced by its
text; SOURCE is not written over.

Besides the fixed keys, a slot `[AUDIT: vg_R2340_R2364 ...]` (or `Vg_`, capitalized) is the
held-back verdict of the claims named, grouped by verdict ("on the held-back structures, R2364 holds
weaker (...) and the other one holds"). After filling, every claim identifier the article prints
outside a slot whose verdict is not "holds" must be named in a `vg_` slot of the same paragraph; the
tool lists any that is not and exits 1.
"""
import argparse
import csv
import json
import os
import re
import statistics
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
VERDICTS = ('holds', 'weaker', 'does not hold', 'not tested', 'not judged')
SLOT = re.compile(r'\[AUDIT: ([A-Za-z0-9_]+)[^\]]*\]')
WEAKER_NOTE = "the direction held and the size fell outside the study's quartiles"


def pct(x):
    return f'{100 * x:.0f}'


def join(items):
    items = list(items)
    if len(items) <= 1:
        return ''.join(items)
    return ', '.join(items[:-1]) + ' and ' + items[-1]


def decimals(x):
    s = repr(float(x))
    return len(s.split('.')[1]) if '.' in s and 'e' not in s else 0


def group_text(ids, verdict_of, capital):
    """The held-back verdicts of the claims named, grouped by verdict."""
    by = {v: [i for i in ids if verdict_of[i] == v] for v in VERDICTS}
    parts = []
    if by['does not hold']:
        d = by['does not hold']
        parts.append(f"{join(d)} {'does' if len(d) == 1 else 'do'} not hold")
    if by['weaker']:
        w = by['weaker']
        parts.append(f"{join(w)} {'holds' if len(w) == 1 else 'hold'} weaker ({WEAKER_NOTE})")
    for v in ('not tested', 'not judged'):
        if by[v]:
            parts.append(f"{join(by[v])} {'was' if len(by[v]) == 1 else 'were'} {v}")
    h = len(by['holds'])
    if h and len(parts):
        parts.append(f"the other {'one holds' if h == 1 else f'{h} hold'}")
    elif h:
        parts.append('it holds' if h == 1 else ('both hold' if h == 2 else f'all {h} hold'))
    lead = 'On' if capital else 'on'
    return f'{lead} the held-back structures, ' + join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('claims')
    ap.add_argument('verdicts')
    ap.add_argument('readings')
    ap.add_argument('--report')
    ap.add_argument('--data', default=os.path.join(HERE, '..', 'data'))
    ap.add_argument('--apply')
    ap.add_argument('--out', default=os.path.join(HERE, '..', 'article.md'))
    a = ap.parse_args()
    claims = {c['id']: c for c in json.load(open(a.claims))['claims']}
    verdicts = list(csv.DictReader(open(a.verdicts)))
    assert {v['id'] for v in verdicts if v['kind'] != 'late'} == set(claims), 'verdicts do not match the claims'
    verdict_of = {v['id']: v['verdict'] for v in verdicts}
    out = []

    def put(key, value, text):
        out.append({'key': key, 'value': value, 'text': text})

    def counts(key, ids):
        c = Counter(verdict_of[i] for i in ids)
        n = len(ids)
        put(f'{key}_n', n, f'{n:,}')
        for v in VERDICTS:
            put(f"{key}_{v.replace(' ', '_')}", c.get(v, 0), f'{c.get(v, 0):,}')
        tested = n - c.get('not tested', 0) - c.get('not judged', 0)
        put(f'{key}_tested', tested, f'{tested:,}')
        same = c.get('holds', 0) + c.get('weaker', 0)
        put(f'{key}_same_side', same, f'{same:,}')
        put(f'{key}_same_side_pct', same / tested if tested else 0, pct(same / tested) if tested else '0')
        for v in ('holds', 'weaker', 'does not hold'):
            share = c.get(v, 0) / n if n else 0
            put(f"{key}_{v.replace(' ', '_')}_pct", share, pct(share))
        dnh = sorted(i for i in ids if verdict_of[i] == 'does not hold')
        put(f'{key}_does_not_hold_ids', len(dnh), join(dnh))
        return c

    ids_all = set(claims)
    c = counts('all', ids_all)
    untested = c.get('not tested', 0) + c.get('not judged', 0)
    put('all_not_tested_sentence', untested,
        'Every combination the claims need was run, so every claim was tested.' if untested == 0
        else f'{untested:,} claims were on combinations the audit did not run and were not tested.')
    for kind in ('effect', 'level', 'pair'):
        counts(kind, {i for i, c in claims.items() if c['kind'] == kind})
    check = {i for i, c in claims.items() if c['kind'] == 'level' and c['line'] == 'iec_check_point'}
    counts('check_nondwell', {i for i in check if claims[i]['test'] != 'T4'})
    counts('check_dwell', {i for i in check if claims[i]['test'] == 'T4'})
    for t in ('T1', 'T2', 'T3', 'T4', 'T5', 'L1'):
        counts(f'effect_{t}', {i for i, c in claims.items() if c['kind'] == 'effect' and c['test'] == t})

    # The verdicts that turn on the rounding of the stored study quartiles, as the audit's report
    # lists them. Each must read "weaker" here with its audit median equal to a stored quartile.
    if a.report:
        report = ' '.join(open(a.report).read().split())
        m = re.search(r'The (\d+) are ((?:R\d{4}, )+R\d{4} and R\d{4})', report)
        assert m, 'the report names no rounding verdicts'
        rounding = re.findall(r'R\d{4}', m.group(2))
        assert len(rounding) == int(m.group(1)), 'the report\'s count and list differ'
        row = {v['id']: v for v in verdicts}
        for i in rounding:
            r = row[i]
            assert r['verdict'] == 'weaker', i
            assert r['audit_median'] in (r['study_q1'], r['study_q3']), i
        places = max(decimals(claims[i]['study'][q]) for i in claims for q in ('q1', 'q3')
                     if claims[i]['study'].get(q) not in (None, float('inf'), float('-inf')))
        kinds = Counter(claims[i]['kind'] for i in rounding)
        put('rounding_n', len(rounding), f'{len(rounding)}')
        put('rounding_ids', len(rounding), join(rounding))
        put('rounding_places', places, f'{places}')
        put('rounding_kinds', len(kinds), join(sorted(kinds)))
        put('rounding_pair_n', kinds.get('pair', 0), f"{kinds.get('pair', 0)}")
        put('words_holds', c['holds'] + len(rounding), f"{c['holds'] + len(rounding):,}")
        put('words_weaker', c['weaker'] - len(rounding), f"{c['weaker'] - len(rounding):,}")
        put('words_does_not_hold', c['does not hold'], f"{c['does not hold']:,}")

    # The held-back pooled readings, as in the study's Figure 5
    rows = list(csv.DictReader(open(a.readings)))
    put('audit_runs', len(rows), f'{len(rows):,}')
    for version in ('hertzforge', 'python'):
        for kind in ('linear', 'realistic', 'strong'):
            for test in ('T1', 'T2', 'T3', 'T4', 'T5', 'L1'):
                g = [r for r in rows if r['version'] == version and r['kind'] == kind and r['test'] == test]
                if not g:
                    continue
                done = sum(r['outcome'] == 'completed' for r in g) / len(g)
                iec = statistics.median(float(r['iec_share'] or 0) for r in g)
                put(f'done_{version}_{kind}_{test}', done, pct(done))
                put(f'iec_{version}_{kind}_{test}', iec, pct(iec))

    source = open(a.apply).read() if a.apply else ''
    for key in sorted(set(SLOT.findall(source))):
        if key[:3] in ('vg_', 'Vg_'):
            ids = key[3:].split('_')
            assert all(i in verdict_of for i in ids), key
            put(key, len(ids), group_text(ids, verdict_of, key[0] == 'V'))

    os.makedirs(a.data, exist_ok=True)
    with open(os.path.join(a.data, 'audit_numbers.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['key', 'value', 'text'], lineterminator='\n')
        w.writeheader()
        w.writerows(out)
    # The verdicts for Figure 8, without the claims' text, which names the laws (this article names
    # none; a claim's text is in the claims file under its identifier).
    fields = ['id', 'kind', 'verdict', 'audit_median', 'audit_n', 'study_median', 'study_q1', 'study_q3']
    with open(os.path.join(a.data, 'audit_verdicts.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
        w.writeheader()
        w.writerows(verdicts)
    print('wrote', len(out), 'slot values')

    if a.apply:
        values = {o['key']: o['text'] for o in out}
        missing = []

        def fill(m):
            key = m.group(1)
            if key not in values:
                missing.append(key)
                return m.group(0)
            return values[key]
        filled = SLOT.sub(fill, source)
        open(a.out, 'w').write(filled)
        print('wrote', a.out, '; slots left unfilled:', ', '.join(sorted(set(missing))) or 'none')

        # Every printed claim that does not simply hold is named in a vg_ slot of its paragraph.
        bad = []
        for para in source.split('\n\n'):
            named = {i for k in SLOT.findall(para) if k[:3] in ('vg_', 'Vg_') for i in k[3:].split('_')}
            printed = set(re.findall(r'R\d{4}', SLOT.sub(' ', para)))
            bad += sorted(i for i in printed - named if verdict_of[i] != 'holds')
        cited = set(re.findall(r'R\d{4}', SLOT.sub(' ', source)))
        print('claims cited:', len(cited), dict(Counter(verdict_of[i] for i in cited)))
        print('cited claims that do not simply hold, with no verdict in their paragraph:',
              ', '.join(bad) or 'none')
        if missing or bad:
            sys.exit(1)


if __name__ == '__main__':
    main()
