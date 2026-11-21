"""Write the claims about a law from the study's tables, by one rule, before its held-back runs are
read. Appends to ../data/claims.json; a claim already in the file is never rewritten. It runs
nothing and reads no held-back result.

    PYTHONDONTWRITEBYTECODE=1 python3 make_claims.py LAW [LAW ...]
    PYTHONDONTWRITEBYTECODE=1 python3 make_claims.py --note KIND LAW "TEXT"     (KIND: setting, checks or other)

The rule, the same for every law (written 2026-11-20, before any held-back result of any of the
three laws was read):

- pair: from study_pairs_two.csv (the 6 x 12 and 6 x 6 systems alone, structures 0 to 9, defaults).
  For each row that names the law (as `law` or as `against`), and each of the three lines (control
  gauges, held-out gauges, stress), a claim is written where the median difference is larger than
  0.2 dB in size, at least 6 in 10 of the structures differ by more than 0.2 dB on the median's
  side, and at most 2 in 10 on the other side. The claim's side is the median's sign.
- level: from study_settings_scores.csv, the law at its defaults, each of the two systems and each
  stage: "on level" where the median level error is within 1.0 dB of zero, "high" above +1.0 dB,
  "low" below -1.0 dB.
- A note (setting, checks, other) is a claim in words that the held-back sample does not judge.

claims_check.py sets each claim beside the held-back structures.

Copyright 2026 Kevin Cross and Norman Hunter. MIT license.
"""
import csv
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
FILE = os.path.join(DATA, 'claims.json')
FLOOR, LEVEL = 0.2, 1.0
SYSTEM = {'more_controls': 'the 6 x 12 system', 'equal': 'the 6 x 6 system'}
KIND = {'none': 'linear structures', 'realistic': 'the realistic size of change', 'strong': 'the strong size of change'}
LINE = {'control': 'error at the control gauges', 'held_out': 'error at the held-out gauges', 'stress': 'stress error'}


def rows(name):
    with open(os.path.join(DATA, name), newline='') as f:
        return list(csv.DictReader(f))


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    doc = json.load(open(FILE)) if os.path.exists(FILE) else {'claims': []}
    claims = doc['claims']
    stamp = time.strftime('%Y-%m-%d %H:%M %Z')
    nid = max([c['id'] for c in claims], default=0)
    added = 0
    if args[0] == '--note':
        kind, law, text = args[1], args[2], args[3]
        if kind not in ('setting', 'checks', 'other'):
            sys.exit('a note is of kind setting, checks or other')
        claims.append(dict(id=nid + 1, kind=kind, law=law, text=text, written=stamp))
        added = 1
    else:
        laws = args
        have = {(c['kind'], c.get('law'), c.get('against'), c.get('systems'), c.get('structure_kind'), c.get('line')) for c in claims}
        for r in rows('study_pairs_two.csv'):
            if r['law'] not in laws and r['against'] not in laws:
                continue
            for line in ('control', 'held_out', 'stress'):
                if r[line + '_n'] == '':
                    continue
                n, med = int(r[line + '_n']), float(r[line + '_median'])
                lower, higher = int(r[line + '_lower']), int(r[line + '_higher'])
                side = 'lower' if med < 0 else 'higher'
                mine, other = (lower, higher) if med < 0 else (higher, lower)
                if abs(med) <= FLOOR or mine < 0.6 * n or other > 0.2 * n:
                    continue
                key = ('pair', r['law'], r['against'], r['systems'], r['structure_kind'], line)
                if key in have:
                    continue
                nid += 1
                added += 1
                claims.append(dict(
                    id=nid, kind='pair', law=r['law'], against=r['against'], systems=r['systems'], structure_kind=r['structure_kind'],
                    line=line, side=side, written=stamp,
                    text=(f"On {SYSTEM[r['systems']]}, {KIND[r['structure_kind']]}: {r['law']} has a {side} {LINE[line]} than "
                          f"{r['against']} (study: median {med:+.2f} dB; {lower} lower and {higher} higher of {n} structures).")))
        for r in rows('study_settings_scores.csv'):
            if r['law'] not in laws or r['settings'] != 'default':
                continue
            key = ('level', r['law'], None, r['systems'], r['structure_kind'], None)
            if key in have:
                continue
            x = float(r['level_db'])
            side = 'on level' if abs(x) <= LEVEL else ('high' if x > 0 else 'low')
            nid += 1
            added += 1
            words = {'on level': 'is within 1.0 dB of the target in level', 'high': 'runs more than 1.0 dB high in level',
                     'low': 'runs more than 1.0 dB low in level'}[side]
            claims.append(dict(
                id=nid, kind='level', law=r['law'], systems=r['systems'], structure_kind=r['structure_kind'], side=side, written=stamp,
                text=(f"On {SYSTEM[r['systems']]}, {KIND[r['structure_kind']]}: {r['law']} at its defaults {words} "
                      f"(study: median {x:+.2f} dB, quartiles {r['level_q1']} to {r['level_q3']}, {r['n']} structures).")))
    with open(FILE, 'w') as f:
        json.dump(doc, f, indent=1)
        f.write('\n')
    kinds = {}
    for c in claims:
        kinds[c['kind']] = kinds.get(c['kind'], 0) + 1
    print(f'{added} claims added at {stamp};', len(claims), 'in the file:', ', '.join(f'{k} {v}' for k, v in sorted(kinds.items())))


if __name__ == '__main__':
    main()
