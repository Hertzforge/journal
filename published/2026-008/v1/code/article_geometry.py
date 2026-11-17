"""The parts of the worked example's article, as data for the article figure.

    python article_geometry.py STAGE2_PROBLEM_FOLDER SECTIONS_CSV

STAGE2_PROBLEM_FOLDER   a staged problem (geometry.json, structure.json, problem.json), for example
                        frame-12x6-realistic_s00. Its geometry gives every node, beam element and lumped mass.
SECTIONS_CSV            model_elements.csv of article 2026-001 (Cross and Zwink, 2026, data/), which gives the
                        tube width and wall of every element of the same seed's chassis and components. An
                        element of the problem is given the section of the 2026-001 element with the same two end
                        points; the script stops if a chassis or component element has no such match.

The member's sections are its own: the bracket is a 16 x 16 mm steel square tube with a 4 mm wall (as the
generator builds it), the strips and the mass are as designed (the generator's geometry file, named in
problem.json): the mass's three sizes run along the strips, across them and in their thin direction. The links that join the mass to the strips carry no section and are not drawn.

Writes ../data/fig_article_parts.csv (one row per solid) and ../data/fig_article_rig.csv (shakers and gauges).
Needs NumPy only. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
BRACKET = (0.016, 0.004)


def main(folder, sections_csv):
    geo = json.load(open(os.path.join(folder, 'geometry.json')))
    st = json.load(open(os.path.join(folder, 'structure.json')))
    pm = json.load(open(os.path.join(folder, 'problem.json')))
    gen = json.load(open(os.path.join(DATA, 'member_design.json')))[os.path.basename(os.path.normpath(folder))]['member']
    d = gen['design']
    X = np.array(geo['nodes'])
    old = list(csv.DictReader(open(sections_csv)))
    onodes = {}
    for r in csv.DictReader(open(os.path.join(os.path.dirname(sections_csv), 'model_nodes.csv'))):
        if r['structure'] == 'article':
            onodes[int(r['node'])] = np.array([float(r['x_m']), float(r['y_m']), float(r['z_m'])])
    osec = {}
    for r in old:
        if r['structure'] != 'article':
            continue
        a, b = onodes[int(r['node_i'])], onodes[int(r['node_j'])]
        osec[(tuple(np.round(a, 5)), tuple(np.round(b, 5)))] = (float(r['tube_width_m']), float(r['wall_m']), r['group'])
    parts = []
    for k, e in enumerate(geo['elements']):
        a, b, g = X[e['i']], X[e['j']], e['group']
        if g in ('chassis', 'stalk'):
            key = (tuple(np.round(a, 5)), tuple(np.round(b, 5)))
            sec = osec.get(key) or osec.get(key[::-1])
            if sec is None:
                sys.exit(f'element {k} ({g}) has no element of 2026-001 with the same end points; the article differs')
            parts.append(dict(kind='tube', group=g, element=k, x0=a[0], y0=a[1], z0=a[2], x1=b[0], y1=b[1], z1=b[2],
                              width=sec[0], wall=sec[1], ux='', uy='', uz='', wx='', wy='', wz='', size_u='', size_v='', size_w=''))
        elif g == 'bracket':
            parts.append(dict(kind='tube', group=g, element=k, x0=a[0], y0=a[1], z0=a[2], x1=b[0], y1=b[1], z1=b[2],
                              width=BRACKET[0], wall=BRACKET[1], ux='', uy='', uz='', wx='', wy='', wz='', size_u='', size_v='', size_w=''))
        elif g == 'strip':
            th = np.array(gen['thin'])
            parts.append(dict(kind='plate', group=g, element=k, x0=a[0], y0=a[1], z0=a[2], x1=b[0], y1=b[1], z1=b[2],
                              width=d['b'] / 2, wall=d['t'], ux=th[0], uy=th[1], uz=th[2], wx='', wy='', wz='', size_u='', size_v='', size_w=''))
    mid = int(gen['mid'])
    for m in geo['lumped_masses']:
        p = X[m['node']]
        if m['node'] == mid:           # the member's mass, as designed: along the strips, across, thin
            ax, th = np.array(gen['axis']), np.array(gen['thin'])
            bl = d['block']
            parts.append(dict(kind='block', group='member mass', element='', x0=p[0], y0=p[1], z0=p[2], x1='', y1='', z1='',
                              width='', wall='', ux=ax[0], uy=ax[1], uz=ax[2], wx=th[0], wy=th[1], wz=th[2],
                              size_u=bl['l'], size_v=bl['w'], size_w=bl['h']))
            continue
        s = (m['kg'] / 7850.0) ** (1 / 3)
        grp = 'component tip mass' if m['node'] in geo['tips'] else 'lumped mass'
        parts.append(dict(kind='block', group=grp, element='', x0=p[0], y0=p[1], z0=p[2], x1='', y1='', z1='', width='', wall='',
                          ux=1.0, uy=0.0, uz=0.0, wx=0.0, wy=0.0, wz=1.0, size_u=s, size_v=s, size_w=s))
    rig = []
    for dr in st['drives']:
        rig.append(dict(role='shaker', name=dr['name'], node=dr['node'], axis=dr['direction'], x=dr['xyz'][0], y=dr['xyz'][1], z=dr['xyz'][2]))
    for o in st['outputs']:
        if o['role'] == 'monitor':
            continue
        role = 'control' if o['role'] == 'control' else ('tip' if o['group'] == 'tip' else 'held_out')
        rig.append(dict(role=role, name=o['name'], node=o['node'], axis=o['direction'], x=o['xyz'][0], y=o['xyz'][1], z=o['xyz'][2]))
    for m in geo['mounts']:
        rig.append(dict(role='mount', name='', node=m, axis='', x=X[m][0], y=X[m][1], z=X[m][2]))
    rig.append(dict(role='member mid-span', name='', node=mid, axis='', x=X[mid][0], y=X[mid][1], z=X[mid][2]))
    os.makedirs(DATA, exist_ok=True)
    for name, rows in (('fig_article_parts.csv', parts), ('fig_article_rig.csv', rig)):
        with open(os.path.join(DATA, name), 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    print(f'{len(parts)} parts, {len(rig)} rig rows; member on component {gen["component"]}, mid-span node {mid}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
