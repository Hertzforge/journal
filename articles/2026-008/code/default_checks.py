"""The controller's checks at their defaults: how the study's and the audit's runs at default settings ended.

    python default_checks.py [STUDY_CARDS [AUDIT_CARDS ...]]

Reads every scorecard made with the checks at their defaults (`outcome.protections` is "default"), counts how it
ended (completed, stopped on the growing-error check, stopped on the drive-change check), the loop of each stop, and
whether the same case with the checks widened (the `_divopen` card beside it) completed. Structure 24 of the audit,
which the simulator refused at the strong tier and which counts in no verdict, is left out. With no argument the
script keeps ../data/default_checks.csv as it is. Writes ../data/default_checks.csv (fill_article.py reads it as
chk.*). Needs the standard library only. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'data', 'default_checks.csv')
DROPPED = {'s24'}


def count(folders):
    v = dict(runs=0, completed=0, stopped=0, growing_error=0, drive_change=0, other=0, widened_completed=0,
             loop_min=10 ** 6, loop_max=0, loop_7=0, by_loop_12=0)
    structures = set()
    for folder in folders:
        for name in sorted(os.listdir(folder)):
            if not name.endswith('.json') or name.endswith('_divopen.json') or name.split('_')[0] in DROPPED:
                continue
            o = json.load(open(os.path.join(folder, name))).get('outcome', {})
            if o.get('protections') != 'default':
                continue
            v['runs'] += 1
            structures.add(name.split('_')[0])
            if o.get('completed'):
                v['completed'] += 1
                continue
            v['stopped'] += 1
            stop = o.get('stop') or {}
            g = stop.get('guard')
            v['growing_error'] += g == 'divergence'
            v['drive_change'] += g == 'cap_divergence'
            v['other'] += g not in ('divergence', 'cap_divergence')
            loop = stop.get('loop')
            v['loop_min'], v['loop_max'] = min(v['loop_min'], loop), max(v['loop_max'], loop)
            v['loop_7'] += loop == 7
            v['by_loop_12'] += loop <= 12
            t = os.path.join(folder, name[:-5] + '_divopen.json')
            v['widened_completed'] += os.path.exists(t) and bool(json.load(open(t)).get('outcome', {}).get('completed'))
    v['structures'] = len(structures)
    return v


def main():
    if len(sys.argv) < 2:
        print('default_checks.py: no card folders given; data/default_checks.csv kept')
        return
    rows = [(f'study.{k}', x) for k, x in count([sys.argv[1]]).items()]
    if len(sys.argv) > 2:
        rows += [(f'audit.{k}', x) for k, x in count(sys.argv[2:]).items()]
        # scorecards in each of the audit's batches (every one was scored again from its kept files)
        for i, folder in enumerate(sys.argv[2:], 1):
            rows.append((f'audit.batch{i}_cards', sum(1 for n in os.listdir(folder) if n.endswith('.json'))))
    with open(OUT, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['key', 'value'])
        w.writerows(rows)
    print('default checks:', dict(rows))


if __name__ == '__main__':
    main()
