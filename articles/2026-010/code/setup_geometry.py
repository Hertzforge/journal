"""The structure of structure 0 (seed 0) and the five setups, as data for the setup figure.

    PYTHONDONTWRITEBYTECODE=1 python setup_geometry.py PROBLEMS_DIR

PROBLEMS_DIR is the problems/ folder of the data set, version 0.2 (DOI 10.5281/zenodo.24310742). Reads the five linear problem folders of seed 0 (frame-<controls>x<shakers>_s00: geometry.json, structure.json)
and writes ../data/fig_setups_frame.csv (one row per beam element and lumped mass) and ../data/fig_setups_rig.csv
(one row per shaker and gauge of each setup). Also prints which shaker points and control gauges two setups share.

Needs NumPy only. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
if len(sys.argv) != 2:
    sys.exit('usage: setup_geometry.py PROBLEMS_DIR')
PROBLEMS = sys.argv[1]
SETUPS = [(3, 12), (6, 12), (12, 24), (6, 6), (12, 12)]           # (shakers, control gauges)


def folder(ns, nc):
    return os.path.join(PROBLEMS, f'frame-{nc}x{ns}_s00')


def main():
    geo = json.load(open(os.path.join(folder(6, 12), 'geometry.json')))
    X = geo['nodes']
    with open(os.path.join(DATA, 'fig_setups_frame.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['kind', 'group', 'x0', 'y0', 'z0', 'x1', 'y1', 'z1', 'kg'])
        for e in geo['elements']:
            a, b = X[e['i']], X[e['j']]
            w.writerow(['element', e['group']] + [f'{v:.6f}' for v in a + b] + [''])
        for m in geo['lumped_masses']:
            a = X[m['node']]
            w.writerow(['mass', 'mass'] + [f'{v:.6f}' for v in a + a] + [f'{m["kg"]:.3f}'])
        for n in geo['mounts']:
            a = X[n]
            w.writerow(['mount', 'mount'] + [f'{v:.6f}' for v in a + a] + [''])
    sets = {}
    with open(os.path.join(DATA, 'fig_setups_rig.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['setup', 'kind', 'name', 'node', 'direction', 'x', 'y', 'z'])
        for ns, nc in SETUPS:
            st = json.load(open(os.path.join(folder(ns, nc), 'structure.json')))
            tag = f'{ns}x{nc}'
            sets[tag] = dict(drives={(d['node'], d['direction']) for d in st['drives']},
                             controls={(o['node'], o['direction']) for o in st['outputs'] if o['role'] == 'control'})
            for d in st['drives']:
                w.writerow([tag, 'shaker', d['name'], d['node'], d['direction']] + [f'{v:.6f}' for v in d['xyz']])
            for o in st['outputs']:
                if o['role'] == 'control':
                    kind = 'control'
                elif o['role'] == 'held_out':
                    kind = 'held_out' if o['group'] == 'gauge' else 'tip'
                else:
                    continue
                w.writerow([tag, kind, o['name'], o['node'], o['direction']] + [f'{v:.6f}' for v in o['xyz']])
    for a, b in (('6x6', '6x12'), ('12x12', '12x24'), ('3x12', '6x12'), ('6x12', '12x12')):
        A, B = sets[a], sets[b]
        print(f'{a} against {b}: shakers shared {len(A["drives"] & B["drives"])} of {len(A["drives"])} and {len(B["drives"])}; '
              f'control gauges shared {len(A["controls"] & B["controls"])} of {len(A["controls"])} and {len(B["controls"])}')


if __name__ == '__main__':
    main()
