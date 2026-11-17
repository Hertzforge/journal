"""Figure 1: the article of structure 0 as a rendered solid, and the five systems on their shakers.

    PYTHONDONTWRITEBYTECODE=1 python fig_setups.py

Reads ../data/fig_setups_parts.csv (the solids of structure 0: every tube with its width and wall, the masses, the
hardening member's bracket, strips and mass; the same file as the benchmark article's data/fig_article_parts.csv,
written there by its code/article_geometry.py from the released problem and article 2026-001's section table) and
../data/fig_setups_rig.csv and ../data/fig_setups_frame.csv (shakers, gauges and mount points of each system,
written by setup_geometry.py from the released problems). Builds solids with build123d and renders them from the
tessellation, the way the benchmark article draws its Figure 3 (its code/fig_article.py, same author, MIT license).
Shakers and suspension cords show position and direction only and carry no modelled property.

Writes ../figures/fig_setups.png. Needs build123d (tested 0.13.0), NumPy and matplotlib.
Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
import numpy as np  # noqa: E402
from build123d import Box, Compound, Cylinder, Plane  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
MM = 1000.0
AXV = {'x': np.array([1.0, 0, 0]), 'y': np.array([0, 1.0, 0]), 'z': np.array([0, 0, 1.0])}
parts = list(csv.DictReader(open(os.path.join(DATA, 'fig_setups_parts.csv'))))
layout = list(csv.DictReader(open(os.path.join(DATA, 'fig_setups_rig.csv'))))
frame = list(csv.DictReader(open(os.path.join(DATA, 'fig_setups_frame.csv'))))
SETUPS = [('3x12', 'b'), ('6x12', 'c'), ('12x24', 'd'), ('6x6', 'e'), ('12x12', 'f')]


def P(r, s=''):
    return np.array([float(r['x' + s]), float(r['y' + s]), float(r['z' + s])]) * MM


def plane_along(p0, p1, up=None):
    ex = (p1 - p0) / np.linalg.norm(p1 - p0)
    if up is None:
        ref = np.array([0, 0, 1.0]) if abs(ex[2]) < 0.9 else np.array([0, 1.0, 0])
        ez = np.cross(ex, ref)
    else:
        ez = np.asarray(up, float)
    ez /= np.linalg.norm(ez)
    return Plane(origin=tuple((p0 + p1) / 2), x_dir=tuple(ex), z_dir=tuple(ez))


def solid(r):
    if r['kind'] == 'tube':
        p0, p1 = P(r, '0'), P(r, '1')
        b, t = float(r['width']) * MM, float(r['wall']) * MM
        L = np.linalg.norm(p1 - p0) + b
        return plane_along(p0, p1) * (Box(L, b, b) - Box(L + 1.0, b - 2 * t, b - 2 * t))
    if r['kind'] == 'plate':
        p0, p1 = P(r, '0'), P(r, '1')
        up = np.array([float(r['ux']), float(r['uy']), float(r['uz'])])
        return plane_along(p0, p1, up) * Box(np.linalg.norm(p1 - p0), float(r['width']) * MM, max(float(r['wall']) * MM, 0.25))
    c = P(r, '0')
    u = np.array([float(r['ux']), float(r['uy']), float(r['uz'])])
    w = np.array([float(r['wx']), float(r['wy']), float(r['wz'])])
    return Plane(origin=tuple(c), x_dir=tuple(u), z_dir=tuple(w)) * Box(float(r['size_u']) * MM, float(r['size_v']) * MM,
                                                                       float(r['size_w']) * MM)


def rod(p0, p1, rad):
    L = np.linalg.norm(p1 - p0)
    d = (p1 - p0) / L
    ref = np.array([1.0, 0, 0]) if abs(d[0]) < 0.9 else np.array([0, 1.0, 0])
    xd = np.cross(d, ref)
    xd /= np.linalg.norm(xd)
    return Plane(origin=tuple((p0 + p1) / 2), x_dir=tuple(xd), z_dir=tuple(d)) * Cylinder(rad, L)


LIGHT = np.array([-0.4, -0.6, 0.8])
LIGHT /= np.linalg.norm(LIGHT)
ALU, STEEL, MEMBER, STRIP, SHAKER, GRAY = (0.72, 0.75, 0.80), (0.35, 0.35, 0.38), (0.90, 0.55, 0.15), \
    (0.85, 0.30, 0.10), (0.25, 0.35, 0.55), (0.55, 0.55, 0.55)
STYLE = {'control': dict(marker='o', s=120, color='#0072B2', edgecolors='black', linewidths=0.8),
         'held_out': dict(marker='D', s=110, color='white', edgecolors='#D55E00', linewidths=2.4),
         'tip': dict(marker='^', s=110, color='#E69F00', edgecolors='black', linewidths=0.8)}


def tris(shape, rgb, tol=0.3):
    v, f = shape.tessellate(tol)
    V = np.array([[p.X, p.Y, p.Z] for p in v])
    T = V[np.array(f)]
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    shade = 0.35 + 0.65 * np.abs(n @ LIGHT)
    return T, np.clip(np.array(rgb)[None, :] * shade[:, None], 0, 1)


def draw(ax, groups, elev=22, azim=-58):
    for T, C in groups:
        ax.add_collection3d(Poly3DCollection(T, facecolors=C, edgecolors='none', linewidths=0))
    ax.view_init(elev=elev, azim=azim)


def finish(ax, pts, title, zoom=0.71):
    pts = np.array(pts)
    lo, hi = pts.min(0), pts.max(0)
    c = (lo + hi) / 2
    r = (hi - lo).max() / 2 * zoom
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.set_title(title, fontsize=15, loc='left')


def article_tris():
    sel = {'tubes': ('chassis', 'stalk'), 'masses': ('lumped mass', 'component tip mass'), 'bracket': ('bracket',),
           'strips': ('strip',), 'member': ('member mass',)}
    rgb = {'tubes': ALU, 'masses': STEEL, 'bracket': GRAY, 'strips': STRIP, 'member': MEMBER}
    out = []
    for k, groups in sel.items():
        shapes = [solid(r) for r in parts if r['group'] in groups and r['kind'] != 'group']
        if shapes:
            out.append(tris(Compound(shapes), rgb[k]))
    return out


ART = article_tris()
art_pts = [P(r, '0') for r in parts]
centroid = np.mean([P(r, '0') for r in parts if r['group'] == 'chassis'], axis=0)
mounts = [P(r, '0') for r in frame if r['kind'] == 'mount']
CORDS = tris(Compound([rod(p, p + np.array([0, 0, -150.0]), 2.0) for p in mounts]), GRAY)


def gauges(ax, rows):
    seen = set()
    for kind in ('tip', 'held_out', 'control'):
        for r in rows:
            if r['kind'] == kind and r['node'] not in seen:
                seen.add(r['node'])
                ax.scatter(*P(r), zorder=7, depthshade=False, **STYLE[kind])


fig = plt.figure(figsize=(16, 10.6))
ax = fig.add_subplot(2, 3, 1, projection='3d', computed_zorder=False)
draw(ax, ART)
for p in mounts:
    ax.scatter(*p, marker='s', s=55, facecolors='none', edgecolors='black', linewidths=1.6, zorder=6, depthshade=False)
gauges(ax, [r for r in layout if r['setup'] == '6x12' and r['kind'] == 'tip'])
finish(ax, art_pts, '(a) The article, structure 0')

for k, (setup, letter) in enumerate(SETUPS):
    ax = fig.add_subplot(2, 3, k + 2, projection='3d', computed_zorder=False)
    rows = [r for r in layout if r['setup'] == setup]
    sh = []
    for r in rows:
        if r['kind'] == 'shaker':
            p, a = P(r), AXV[r['direction']]
            sh.append((p, (-1.0 if (p - centroid) @ a <= 0 else 1.0) * a))
    bodies = []
    for p, d in sh:
        bodies += [rod(p + d * 12, p + d * 70, 1.8), rod(p + d * 70, p + d * 125, 24.0)]
    draw(ax, [CORDS] + ART + [tris(Compound(bodies), SHAKER)])
    for p, d in sh:
        ax.quiver(*(p + d * 62), *(-d * 50), color='black', linewidth=2.4, arrow_length_ratio=0.45, zorder=6)
    gauges(ax, rows)
    ns, nc = setup.split('x')
    finish(ax, art_pts + [p + d * 125 for p, d in sh], f'({letter}) {ns} shakers, {nc} control gauges')

handles = [Line2D([], [], ls='none', marker='o', ms=11, mfc='#0072B2', mec='black', label='Control gauge point'),
           Line2D([], [], ls='none', marker='D', ms=10, mfc='white', mec='#D55E00', mew=2, label='Held-out gauge point (the same 4 points, 12 channels, in every system)'),
           Line2D([], [], ls='none', marker='^', ms=11, mfc='#E69F00', mec='black', label='Tip gauge: 3 component tips and the member mid-span (never controlled)'),
           Line2D([], [], color=SHAKER, lw=9, label='Shaker body'),
           Line2D([], [], color='black', lw=1.5, marker='>', ms=6, label='Force direction of the shaker'),
           Line2D([], [], ls='none', marker='s', ms=8, mfc='none', mec='black', mew=1.6, label='Mount point (bolted in service; hangs on a cord on the shakers)'),
           Line2D([], [], color=MEMBER, lw=7, label='Hardening member (mass on two strips)'),
           Line2D([], [], ls='none', marker='s', ms=9, mfc=STEEL, mec=STEEL, label='Lumped mass (steel block)')]
fig.tight_layout(rect=(0, 0.11, 1, 1), w_pad=0.2, h_pad=0.4)
fig.legend(handles=handles, loc='lower center', ncol=2, fontsize=14, frameon=False)
out = os.path.join(HERE, '..', 'figures', 'fig_setups.png')
fig.savefig(out, dpi=150, facecolor='white')
print('wrote', out)
