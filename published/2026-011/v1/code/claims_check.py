"""The claims of the article set beside the held-back structures. Reads ../data/claims.json (the
claims, written before any held-back result of the law was read, with the exception stated in
../data/README.md) and the tables law_results.py wrote, and
writes ../data/audit_verdicts.csv: one row a claim, with the study figure on the same system, the
held-back figure and the verdict. It runs nothing.

    PYTHONDONTWRITEBYTECODE=1 python3 claims_check.py

A claim in claims.json is one of:
  {"id": 1, "kind": "pair", "law": A, "against": B, "systems": "more_controls" or "equal",
   "structure_kind": "none", "realistic" or "strong", "line": "control", "held_out" or "stress",
   "side": "lower" or "higher", "text": "..."}
  {"id": 2, "kind": "level", "law": A, "systems": ..., "structure_kind": ..., "side": "on level",
   "high" or "low", "text": "..."}
  {"id": 3, "kind": "setting" or "checks" or "other", "text": "..."}       (not judged here)

The held-back sample is each law at its defaults on structures 20, 21, 22, 23 and 52, on the
6 x 12 system (more control gauges than shakers) and the 6 x 6 system (as many shakers as control
gauges). The study figure set beside it is on the same system alone.

The rule, fixed before any held-back result was read:
- pair: "holds" if the held-back median of the difference (law minus the other, same structure and
  system) is on the claim's side and larger than 0.2 dB in size; "not borne out" if it is on the
  other side and larger than 0.2 dB; otherwise "inside 0.2 dB".
- level: "holds" if the held-back median level is on the claim's side of the lines at +1.0 and
  -1.0 dB (on level: within 1.0 dB of zero; high: above +1.0 dB; low: below -1.0 dB); otherwise
  "not borne out".
- setting, checks, other: "not judged on the held-back structures".

Copyright 2026 Kevin Cross and Norman Hunter. MIT license.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
FLOOR = 0.2
LEVEL = 1.0


def rows(name):
    with open(os.path.join(DATA, name), newline='') as f:
        return list(csv.DictReader(f))


def one(table, **want):
    hit = [r for r in table if all(r[k] == v for k, v in want.items())]
    return hit[0] if len(hit) == 1 else None


def pair(c, study, audit):
    key = dict(systems=c['systems'], structure_kind=c['structure_kind'], law=c['law'], against=c['against'])
    s, a = one(study, **key), one(audit, **key)
    line = c['line']
    out = ['', '', '', '', '', '']
    if s is not None and s[line + '_n'] != '':
        out[:3] = [s[line + '_median'], f"{s[line + '_lower']} lower, {s[line + '_higher']} higher", s[line + '_n']]
    if a is None or a[line + '_n'] == '':
        return out + ['no held-back result']
    d = float(a[line + '_median'])
    out[3:] = [a[line + '_median'], f"{a[line + '_lower']} lower, {a[line + '_higher']} higher", a[line + '_n']]
    want = -1.0 if c['side'] == 'lower' else 1.0
    if abs(d) <= FLOOR:
        return out + ['inside 0.2 dB']
    return out + ['holds' if d * want > 0 else 'not borne out']


def level(c, study, audit):
    s = one(study, systems=c['systems'], structure_kind=c['structure_kind'], law=c['law'], settings='default')
    a = one(audit, systems=c['systems'], structure_kind=c['structure_kind'], law=c['law'], structures='all')
    out = ['', '', '', '', '', '']
    if s is not None:
        out[:3] = [s['level_db'], f"quartiles {s['level_q1']} to {s['level_q3']}", s['n']]
    if a is None:
        return out + ['no held-back result']
    x = float(a['level_db'])
    out[3:] = [a['level_db'], f"quartiles {a['level_q1']} to {a['level_q3']}", a['n']]
    side = 'on level' if abs(x) <= LEVEL else ('high' if x > 0 else 'low')
    return out + ['holds' if side == c['side'] else 'not borne out']


def main():
    claims = json.load(open(os.path.join(DATA, 'claims.json')))['claims']
    study_pairs, audit_pairs = rows('study_pairs_two.csv'), rows('audit_pairs.csv')
    study_scores, audit_scores = rows('study_settings_scores.csv'), rows('audit_scores.csv')
    out, counts = [], {}
    for c in claims:
        if c['kind'] == 'pair':
            r = pair(c, study_pairs, audit_pairs)
        elif c['kind'] == 'level':
            r = level(c, study_scores, audit_scores)
        else:
            r = ['', '', '', '', '', '', 'not judged on the held-back structures']
        counts[r[-1]] = counts.get(r[-1], 0) + 1
        out.append([c['id'], c['kind'], c.get('law', ''), c.get('against', ''), c.get('systems', ''), c.get('structure_kind', ''),
                    c.get('line', 'level' if c['kind'] == 'level' else ''), c.get('side', '')] + r + [c['text']])
    with open(os.path.join(DATA, 'audit_verdicts.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['claim', 'kind', 'law', 'against', 'systems', 'structure_kind', 'line', 'side', 'study_same_system_db',
                    'study_detail', 'study_n', 'held_back_db', 'held_back_detail', 'held_back_n', 'verdict', 'text'])
        w.writerows(out)
    print('wrote audit_verdicts.csv:', len(out), 'claims;', ', '.join(f'{k}: {v}' for k, v in sorted(counts.items())))


if __name__ == '__main__':
    main()
