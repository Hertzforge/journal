"""Write the article from its template, with every number taken from data/.

    python fill_article.py [PROBLEM_FOLDER_FOR_SIZES]

Reads ../article_template.md and the CSV files in ../data written by example_run.py and stage2_known.py, and
writes ../article.md and ../data/article_numbers.csv (every number the text quotes, under its key).

In the template a number is written {{key}} or {{key:format}}, for example {{s1.12x6.declared_deviation_rms_db:.1f}};
[[if key: text]] keeps the text only when the value is not zero, [[ifnot key: text]] only when it is; a format
that starts with abs prints the size without its sign, for a sentence that says "falls" or "rises".
Keys:
  s1.<rig>.<column>          stage1_scorecard_summary.csv and stage1_problems.csv (rig 12x6 or 6x6)
  s2.<rig>.<tier>.<column>   stage2_known.csv (tier realistic or strong)
  member.<tier>.<column>     stage2_member.csv
  set.<key>                  set_summary.csv
  run.<key>                  closed_loop_summary.csv (the stage 2 closed-loop example, Section 7.4)
  eff.<key>                  effects_summary.csv (what softening and hardening each do, Section 8)
  chk.<key>                  default_checks.csv (the controller's checks at their defaults, study and audit)
  size.<file>                the size of a file of PROBLEM_FOLDER_FOR_SIZES, in words (for the folder table)
A column holding a share (0 to 1) also has <key>_pct, in percent. A key the data does not hold stops the script.
Needs the standard library only. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
SHARE = ('share', 'inside', 'within')


def num(v):
    if v in ('True', 'False'):
        return v == 'True'
    try:
        return float(v)
    except ValueError:
        return v


def rig_of(problem):
    return problem.split('/')[0].replace('frame-', '').split('-')[0]


def put(out, key, v):
    out[key] = num(v)
    if any(s in key.rsplit('.', 1)[1] for s in SHARE) and isinstance(out[key], float):
        out[key + '_pct'] = 100 * out[key]


def human(n):
    for unit, k in (('MB', 1 << 20), ('kB', 1 << 10)):
        if n >= k:
            return f'{n / k:.1f} {unit}' if n < 10 * k else f'{n / k:.0f} {unit}'
    return f'{n} B'


def gather(folder):
    out = {}
    for name in ('stage1_scorecard_summary.csv', 'stage1_problems.csv'):
        for r in csv.DictReader(open(os.path.join(DATA, name))):
            for k, v in r.items():
                put(out, f's1.{rig_of(r["problem"])}.{k}', v)
    for r in csv.DictReader(open(os.path.join(DATA, 'stage2_known.csv'))):
        for k, v in r.items():
            put(out, f's2.{rig_of(r["problem"])}.{r["tier"]}.{k}', v)
    for r in csv.DictReader(open(os.path.join(DATA, 'stage2_member.csv'))):
        for k, v in r.items():
            put(out, f'member.{r["tier"]}.{k}', v)
    for r in csv.DictReader(open(os.path.join(DATA, 'set_summary.csv'))):
        put(out, f'set.{r["key"]}', r['value'])
    for r in csv.DictReader(open(os.path.join(DATA, 'closed_loop_summary.csv'))):
        put(out, f'run.{r["key"]}', r['value'])
    for r in csv.DictReader(open(os.path.join(DATA, 'effects_summary.csv'))):
        put(out, f'eff.{r["key"]}', r['value'])
    for r in csv.DictReader(open(os.path.join(DATA, 'default_checks.csv'))):
        put(out, f'chk.{r["key"]}', r['value'])
    a, b = out['s1.6x6.drive_rms_n_total'], out['s1.12x6.drive_rms_n_total']
    out['s1.force_ratio'] = a / b
    if folder:
        for root, _, files in os.walk(folder):
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), folder)
                out[f'size.{rel}'] = human(os.path.getsize(os.path.join(root, f)))
        sc = sum(os.path.getsize(os.path.join(folder, 'scoring', f)) for f in os.listdir(os.path.join(folder, 'scoring')))
        out['size.scoring'] = human(sc)
    return out


def render(template, values):
    used, missing = {}, []

    def sub(m):
        key, fmt = m.group(1), m.group(2)
        if key not in values:
            missing.append(key)
            return m.group(0)
        v = values[key]
        if isinstance(v, bool):
            s = 'yes' if v else 'no'
        elif fmt and fmt.startswith('abs'):          # the size of a change whose direction the sentence states
            s = format(abs(v), fmt[3:])
        elif fmt:
            s = format(v, fmt)
            if s.startswith('-'):
                s = '-' + s[1:]
        else:
            s = str(v)
        used[m.group(0)] = s
        return s
    def cond(m):                                      # [[if key: text]] and [[ifnot key: text]]
        key = m.group(2)
        if key not in values:
            missing.append(key)
            return ''
        on = bool(values[key]) and values[key] != 0
        return m.group(3) if on == (m.group(1) == 'if') else ''
    template = re.sub(r'\[\[(if|ifnot) ([\w.\-/]+): (.*?)\]\]', cond, template, flags=re.S)
    text = re.sub(r'\{\{([\w.\-/]+)(?::([^}]*))?\}\}', sub, template)
    return text, used, missing


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else None
    values = gather(folder)
    tpl = open(os.path.join(HERE, '..', 'article_template.md')).read()
    text, used, missing = render(tpl, values)
    if missing:
        sys.exit('fill_article.py: the data holds no value for ' + ', '.join(sorted(set(missing))))
    with open(os.path.join(HERE, '..', 'article.md'), 'w') as fh:
        fh.write(text)
    with open(os.path.join(DATA, 'article_numbers.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['placeholder', 'as printed'])
        for k, v in used.items():
            w.writerow([k, v])
    print(f'article.md written: {len(used)} distinct numbers from data/')


if __name__ == '__main__':
    main()
