"""Write ../article.md from article_src.md, putting every number in the text in from the files of
../data, and write ../data/number_sources.csv, one row for each number put in: the line of the
article, the token, the value and the file it was read from. Standard library only. Copyright 2026
Kevin Cross. MIT license.

    python fill_article.py

A token is `{{key}}` (a key of law_numbers.csv), `{{f:key}}` (facts.csv), `{{s:key}}`
(law_scope.csv), or `{{pct:a:b}}` (the key a over the key b of law_numbers.csv, in whole percent), or `{{r1:key}}`
(a key of law_numbers.csv rounded to 1 place; r0 and r2 likewise), or `{{fpct:key}}` (a key of
facts.csv times 100, a fraction as a percentage), or `{{a:key}}` (audit_numbers.csv, the audit on
the held-back structures). `{{vg:k1+k2}}` (or `{{Vg:...}}`, capitalized) is the held-back verdict of
the claims named, each a claim id, a key of law_numbers.csv holding one or a key of audit_numbers.csv
holding a group of them (`pair_ids_...`), grouped by verdict from
audit_verdicts.csv ("on the held-back structures, R0012 holds weaker (...) and the other one holds").
After filling, every claim id the article prints outside a `vg` or `a:` token whose verdict is not
"holds" must be named in a `vg` token of the same paragraph, or the script stops. Whole numbers of four digits
or more are written with commas, as 4,140.
A missing key, or a key with no value, stops the script. It then lists the numerals left in the
text outside tokens (section, figure and equation numbers, standards' and systems' names, test
names, claim ids, years and the like), so they can be read over by eye.
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
TOKEN = re.compile(r'\{\{([A-Za-z0-9]+:)?([A-Za-z0-9_.:+-]+)\}\}')
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


def table(name, key='key', value='value'):
    with open(os.path.join(DATA, name), newline='') as file:
        return {r[key]: r[value] for r in csv.DictReader(file)}


def main():
    sources = {'': ('law_numbers.csv', table('law_numbers.csv')),
               'f:': ('facts.csv', table('facts.csv')),
               's:': ('law_scope.csv', table('law_scope.csv')),
               'a:': ('audit_numbers.csv', table('audit_numbers.csv'))}
    verdict_of = table('audit_verdicts.csv', 'id', 'verdict')
    numbers = sources[''][1]
    text = open(os.path.join(HERE, 'article_src.md')).read()
    used, missing = [], []

    def ids_of(key):
        """Claim ids, keys of law_numbers.csv holding one, or keys of audit_numbers.csv holding a
        group of them."""
        out = []
        for k in key.split('+'):
            if re.fullmatch(r'R\d{4}', k):
                out.append(k)
            elif k in numbers:
                out.append(numbers[k])
            else:
                out += sources['a:'][1].get(k, '').split() or ['']
        return out

    def put(match, line):
        kind, key = match.group(1) or '', match.group(2)
        if kind in ('vg:', 'Vg:'):
            ids = ids_of(key)
            if not all(i in verdict_of for i in ids):
                missing.append(kind + key)
                return match.group(0)
            value = group_text(ids, verdict_of, kind == 'Vg:')
            used.append([line, match.group(0), value, 'audit_verdicts.csv'])
            return value
        if kind in ('r0:', 'r1:', 'r2:'):
            file, values = sources['']
            if not values.get(key):
                missing.append(kind + key)
                return match.group(0)
            value = f'{float(values[key]):.{kind[1]}f}'
            used.append([line, match.group(0), value, file])
            return value
        if kind == 'fpct:':
            file, values = sources['f:']
            if not values.get(key):
                missing.append(kind + key)
                return match.group(0)
            value = f'{100 * float(values[key]):g}'
            used.append([line, match.group(0), value, file])
            return value
        if kind == 'pct:':
            a, b = key.split(':')
            file, values = sources['']
            if not values.get(a) or not values.get(b):
                missing.append(key)
                return match.group(0)
            value = f'{100 * float(values[a]) / float(values[b]):.0f}'
            used.append([line, match.group(0), value, file])
            return value
        file, values = sources[kind]
        if key not in values or values[key] == '':
            missing.append(kind + key)
            return match.group(0)
        value = values[key]
        if re.fullmatch(r'\d{4,}', value):
            value = f'{int(value):,}'
        used.append([line, match.group(0), value, file])
        return value

    out = []
    for n, line in enumerate(text.split('\n'), 1):
        out.append(TOKEN.sub(lambda m: put(m, n), line))
    if missing:
        sys.exit('missing or empty: ' + ', '.join(sorted(set(missing))))
    # Every printed claim that does not simply hold is named in a vg token of its paragraph.
    bad, cited = [], set()
    paras = []
    for para in text.split('\n\n'):
        # A list introduced by a colon belongs to the sentence that introduces it.
        if paras and para.startswith('- ') and paras[-1].rstrip().endswith(':'):
            paras[-1] += '\n\n' + para
        else:
            paras.append(para)
    for para in paras:
        named = {i for m in TOKEN.finditer(para) if m.group(1) in ('vg:', 'Vg:') for i in ids_of(m.group(2))}
        # Ids put in by a vg token or an audit token (lists of claims that do not hold) carry
        # their verdict with them.
        rest = TOKEN.sub(lambda m: '' if m.group(1) in ('vg:', 'Vg:', 'a:') else m.group(0), para)
        printed = set(re.findall(r'R\d{4}', TOKEN.sub(lambda m: put(m, 0), rest)))
        cited |= printed
        bad += sorted(i for i in printed - named if verdict_of.get(i, 'holds') != 'holds')
    used[:] = [u for u in used if u[0] != 0]
    counts = {v: sum(verdict_of[i] == v for i in cited) for v in VERDICTS if any(verdict_of[i] == v for i in cited)}
    print('claims cited:', len(cited), counts)
    if bad:
        sys.exit('cited claims that do not simply hold, with no verdict in their paragraph: ' + ', '.join(bad))
    with open(os.path.join(HERE, '..', 'article.md'), 'w') as file:
        file.write('\n'.join(out))
    with open(os.path.join(DATA, 'number_sources.csv'), 'w', newline='') as file:
        w = csv.writer(file, lineterminator='\n')
        w.writerow(['article_line', 'token', 'value', 'file'])
        w.writerows(used)
    print('wrote article.md with', len(used), 'numbers from data/')
    # The numerals outside tokens, for reading over.
    body = TOKEN.sub('', text.split('\n## References')[0])
    bare = re.findall(r'(?<![A-Za-z0-9_.@-])\d[\d,.]*', body)
    print('numerals outside tokens:', len(bare))


if __name__ == '__main__':
    main()
