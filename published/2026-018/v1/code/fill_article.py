"""Fill the article's numbers: every {{key}} in article_src.md is replaced by the text of that key in
../data/numbers.csv, which dnw_data.py writes. Stops on a key it does not know. Writes ../article.md
and ../data/number_sources.csv (each key used, its text and the file it came from), and lists the
numerals left in the prose that are not tokens, so each can be checked to be a label, a year, a
reference or a test name and not a result. Keys of ../data/audit_numbers.csv (the audit on the
held-back structures, written by audit_numbers.py) are read the same way. `{{vg:k1+k2}}` (or
`{{Vg:...}}`, capitalized) is the held-back verdict of the claims named, each a claim id or a key
holding one, grouped by verdict from ../data/audit_verdicts.csv ("on the held-back structures, R1568
holds weaker (...) and the other one holds"); every claim id the article prints outside these tokens
whose verdict is not "holds" must be named in one in the same paragraph, or the script stops.
Copyright 2026 Kevin Cross. MIT license.

    python fill_article.py
"""
import collections
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
TOKEN = re.compile(r'\{\{(?:(vg|Vg):)?([a-zA-Z0-9_+]+)\}\}')
VERDICTS = ('does not hold', 'weaker', 'not tested', 'not judged', 'holds')
WEAKER_NOTE = "the direction held and the size fell outside the study's quartiles"


def join(items):
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]


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
    if h and parts:
        parts.append(f"the other {'one holds' if h == 1 else f'{h} hold'}")
    elif h:
        parts.append(f'{ids[0]} holds' if h == 1 else ('both hold' if h == 2 else f'all {h} hold'))
    return ('On' if capital else 'on') + ' the held-back structures, ' + join(parts)


def main():
    with open(os.path.join(DATA, 'numbers.csv'), newline='') as f:
        numbers = {r['key']: r for r in csv.DictReader(f)}
    with open(os.path.join(DATA, 'audit_numbers.csv'), newline='') as f:
        for r in csv.DictReader(f):
            if r['key'] in numbers:
                sys.exit('duplicate key: ' + r['key'])
            numbers[r['key']] = r
    with open(os.path.join(DATA, 'audit_verdicts.csv'), newline='') as f:
        verdict_of = {r['id']: r['verdict'] for r in csv.DictReader(f)}

    def ids_of(key):
        return [k if re.fullmatch(r'R\d{4}', k) else numbers.get(k, {}).get('text', '') for k in key.split('+')]
    src = open(os.path.join(HERE, 'article_src.md')).read()
    missing = sorted({k for p, k in TOKEN.findall(src) if not p and k not in numbers}
                     | {k for p, k in TOKEN.findall(src) if p
                        and not all(i in verdict_of for i in ids_of(k))})
    if missing:
        sys.exit('keys not in numbers.csv: ' + ', '.join(missing))
    used = []

    def fill(m):
        kind, key = m.group(1), m.group(2)
        if kind:
            return group_text(ids_of(key), verdict_of, kind == 'Vg')
        used.append(key)
        return numbers[key]['text']

    out = TOKEN.sub(fill, src)
    # Every printed claim that does not simply hold is named in a vg token of its paragraph (a list
    # introduced by a colon counts with the sentence that introduces it). Ids put in by an audit key
    # carry their verdict with them.
    audit_keys = set()
    with open(os.path.join(DATA, 'audit_numbers.csv'), newline='') as f:
        audit_keys = {r['key'] for r in csv.DictReader(f)}
    paras, bad, cited = [], [], set()
    for para in src.split('\n\n'):
        if paras and para.startswith('- ') and paras[-1].rstrip().endswith(':'):
            paras[-1] += '\n\n' + para
        else:
            paras.append(para)
    for para in paras:
        named = {i for p, k in TOKEN.findall(para) if p for i in ids_of(k)}
        rest = TOKEN.sub(lambda m: '' if m.group(1) or m.group(2) in audit_keys
                         else numbers[m.group(2)]['text'], para)
        printed = set(re.findall(r'R\d{4}', rest))
        cited |= printed
        bad += sorted(i for i in printed - named if verdict_of.get(i, 'holds') != 'holds')
    print('claims cited:', len(cited), dict(collections.Counter(verdict_of[i] for i in cited)))
    if bad:
        sys.exit('cited claims that do not simply hold, with no verdict in their paragraph: ' + ', '.join(bad))
    with open(os.path.join(HERE, '..', 'article.md'), 'w') as f:
        f.write(out)
    with open(os.path.join(DATA, 'number_sources.csv'), 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['key', 'text', 'source', 'how', 'uses'])
        for key in sorted(set(used)):
            r = numbers[key]
            w.writerow([key, r['text'], r['source'], r['how'], used.count(key)])
    # The numerals of the prose that are not tokens (front matter, headings' test names, figure
    # paths, citations and code spans aside), for a reader to check.
    body = src.split('\n---\n', 1)[-1]
    body = re.sub(r'`[^`]*`', '', body)
    body = re.sub(r'\[@[^\]]*\]', '', body)
    body = re.sub(r'!\[.*?\]\([^)]*\)\{[^}]*\}', '', body, flags=re.S)
    body = TOKEN.sub('', body)
    bare = re.findall(r'(?<![\w.{-])\d+(?:\.\d+)?(?![\w}])', body)
    print(f'wrote article.md: {len(used)} numbers filled ({len(set(used))} keys); '
          f'{len(bare)} bare numerals left in the prose: {sorted(set(bare), key=lambda x: float(x))}')


if __name__ == '__main__':
    main()
