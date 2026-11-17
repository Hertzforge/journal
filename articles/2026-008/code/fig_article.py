"""Figure: the worked example's article (seed 0) with the hardening member on it, and the article on the shakers.

Reads ../data/fig_article_parts.csv and ../data/fig_article_rig.csv (written by article_geometry.py). Builds
solids with build123d and renders them from the tessellation, the way article 2026-001 drew its Figure 1
(its code/cad_frame_model.py, same author, MIT license). Tubes are the beam model's centrelines, widths and
walls; the strips and the member's mass are as designed; the other masses are steel cubes of the modelled
mass. Shakers and suspension cords show position and direction only and carry no modelled property.

Needs build123d (tested 0.13.0), NumPy and matplotlib. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from build123d import Box, Compound, Cylinder, Plane

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
MM = 1000.0
AXV = {'x': np.array([1.0, 0, 0]), 'y': np.array([0, 1.0, 0]), 'z': np.array([0, 0, 1.0])}
parts = list(csv.DictReader(open(os.path.join(DATA, 'fig_article_parts.csv'))))
rig = list(csv.DictReader(open(os.path.join(DATA, 'fig_article_rig.csv'))))


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
    u = np.array([float(r['ux']), float(r['uy']), float(r['uz'])])      # first size along u, third along w
    w = np.array([float(r['wx']), float(r['wy']), float(r['wz'])])
    pl = Plane(origin=tuple(c), x_dir=tuple(u), z_dir=tuple(w))
    return pl * Box(float(r['size_u']) * MM, float(r['size_v']) * MM, float(r['size_w']) * MM)


def rod(p0, p1, rad):
    L = np.linalg.norm(p1 - p0); d = (p1 - p0) / L
    ref = np.array([1.0, 0, 0]) if abs(d[0]) < 0.9 else np.array([0, 1.0, 0])
    xd = np.cross(d, ref); xd /= np.linalg.norm(xd)
    return Plane(origin=tuple((p0 + p1) / 2), x_dir=tuple(xd), z_dir=tuple(d)) * Cylinder(rad, L)


LIGHT = np.array([-0.4, -0.6, 0.8]); LIGHT /= np.linalg.norm(LIGHT)


def tris(shape, rgb, tol=0.3):
    v, f = shape.tessellate(tol)
    V = np.array([[p.X, p.Y, p.Z] for p in v]); T = V[np.array(f)]
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    shade = 0.35 + 0.65 * np.abs(n @ LIGHT)
    return T, np.clip(np.array(rgb)[None, :] * shade[:, None], 0, 1)


def draw(ax, groups, elev, azim):
    for shapes, rgb in groups:
        if not shapes:
            continue
        T, C = tris(Compound(shapes), rgb)
        ax.add_collection3d(Poly3DCollection(T, facecolors=C, edgecolors='none', linewidths=0))
    ax.view_init(elev=elev, azim=azim)


def finish(ax, pts, title, zoom=0.78):
    pts = np.array(pts); lo, hi = pts.min(0), pts.max(0); c = (lo + hi) / 2; r = (hi - lo).max() / 2 * zoom
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1)); ax.set_axis_off(); ax.set_title(title, fontsize=10)


ALU, STEEL, MEMBER, STRIP, SHAKER, GRAY = (0.72, 0.75, 0.80), (0.35, 0.35, 0.38), (0.90, 0.55, 0.15), (0.85, 0.30, 0.10), \
    (0.25, 0.35, 0.55), (0.55, 0.55, 0.55)


def groups():
    tubes = [solid(r) for r in parts if r['kind'] == 'tube' and r['group'] in ('chassis', 'stalk')]
    bracket = [solid(r) for r in parts if r['group'] == 'bracket']
    strips = [solid(r) for r in parts if r['group'] == 'strip']
    masses = [solid(r) for r in parts if r['group'] in ('lumped mass', 'component tip mass')]
    member = [solid(r) for r in parts if r['group'] == 'member mass']
    return [(tubes, ALU), (masses, STEEL), (bracket, GRAY), (strips, STRIP), (member, MEMBER)]


art_pts = [P(r, '0') for r in parts]
mid = next(P(r) for r in rig if r['role'] == 'member mid-span')
centroid = np.mean([P(r, '0') for r in parts if r['group'] == 'chassis'], axis=0)
fig = plt.figure(figsize=(15, 5.2))

# (a) the article
ax = fig.add_subplot(1, 3, 1, projection='3d', computed_zorder=False)
draw(ax, groups(), 22, -58)
for r in rig:
    if r['role'] == 'mount':
        ax.scatter(*P(r), marker='s', s=45, facecolors='none', edgecolors='black', linewidths=1.5, zorder=5)
tips = {(r['node']) for r in rig if r['role'] == 'tip'}
for r in parts:
    if r['group'] == 'component tip mass':
        ax.scatter(*P(r, '0'), marker='^', s=60, color='#E69F00', edgecolors='black', zorder=5)
ax.scatter(*mid, marker='*', s=220, color='#D55E00', edgecolors='black', zorder=6)
ax.scatter([], [], marker='*', s=160, color='#D55E00', edgecolors='black', label='Hardening member (mass on two strips)')
ax.scatter([], [], marker='^', s=60, color='#E69F00', edgecolors='black', label='Cantilevered component, tip mass (3)')
ax.scatter([], [], marker='s', s=45, facecolors='none', edgecolors='black', label='Mount point (4)')
ax.plot([], [], 's', color=STEEL, label='Lumped mass (steel block)')
ax.legend(loc='lower left', fontsize=8, frameon=False)
finish(ax, art_pts, '(a) The article: tube chassis, components, member')

# (b) close-up of the member
ax = fig.add_subplot(1, 3, 2, projection='3d', computed_zorder=False)
near = [r for r in parts if np.linalg.norm(P(r, '0') - mid) < 70]
keep = lambda rows, g: [solid(r) for r in rows if r['group'] == g]
draw(ax, [([solid(r) for r in near if r['group'] == 'chassis'], ALU), (keep(near, 'bracket'), GRAY),
          (keep(near, 'strip'), STRIP), (keep(near, 'member mass'), MEMBER)], 38, -62)
def label(p, text, off):
    q = p + np.array(off)
    ax.plot(*np.c_[p, q], color='black', lw=0.8, zorder=8)
    ax.text(*q, text, fontsize=8, zorder=9, ha='center', va='bottom', bbox=dict(fc='white', ec='none', alpha=0.8, pad=1))


strip_mid = np.mean([(P(r, '0') + P(r, '1')) / 2 for r in near if r['group'] == 'strip'][:2], axis=0)
br = [P(r, '1') for r in near if r['group'] == 'bracket']
ch = [P(r, '0') for r in near if r['group'] == 'chassis']
label(mid + np.array([0, 0, 10.0]), 'Tuned mass', [0, 0, 25])
label(strip_mid, 'Two thin strips', [-10, -25, 20])
label(max(br, key=lambda q: np.linalg.norm(q - mid)), 'Steel bracket (clamp post)', [-20, 0, -30])
label(max(ch, key=lambda q: np.linalg.norm(q - mid)), 'Chassis tube', [15, 15, -20])
finish(ax, [mid + np.array(v) for v in ([-45, -45, -35], [45, 45, 25])], '(b) The member, close up', zoom=1.0)

# (c) on the shakers
ax = fig.add_subplot(1, 3, 3, projection='3d', computed_zorder=False)
mounts = [P(r) for r in rig if r['role'] == 'mount']
cords = [rod(p, p + np.array([0, 0, -180.0]), 2.0) for p in mounts]
sh = []
for r in rig:
    if r['role'] != 'shaker':
        continue
    p, a = P(r), AXV[r['axis']]
    side = -1.0 if (p - centroid) @ a <= 0 else 1.0
    sh.append((p, side * a))
bodies = []
for p, d in sh:
    bodies += [rod(p + d * 15, p + d * 90, 2.0), rod(p + d * 90, p + d * 160, 32.0)]
draw(ax, [(cords, GRAY)] + groups() + [(bodies, SHAKER)], 22, -58)
for p, d in sh:
    ax.quiver(*(p + d * 70), *(-d * 55), color='black', linewidth=1.4, arrow_length_ratio=0.35, zorder=6)
style = {'control': dict(marker='o', s=55, color='#0072B2', edgecolors='black'),
         'held_out': dict(marker='D', s=50, color='white', edgecolors='#D55E00', linewidths=1.8),
         'tip': dict(marker='^', s=60, color='#E69F00', edgecolors='black')}
seen = set()
for r in rig:
    if r['role'] in style and (r['role'], r['node']) not in seen:
        seen.add((r['role'], r['node']))
        ax.scatter(*P(r), zorder=7, **style[r['role']])
n = {k: sum(1 for r in rig if r['role'] == k) for k in style}
ax.scatter([], [], label=f'Control gauge point ({n["control"]} channels)', **style['control'])
ax.scatter([], [], label=f'Held-out gauge point ({n["held_out"]} channels)', **style['held_out'])
ax.scatter([], [], label=f'Tip gauge, member mid-span included ({n["tip"]} channels)', **style['tip'])
ax.plot([], [], color='black', label=f'Shaker and its force direction ({len(sh)})')
ax.legend(loc='lower left', fontsize=8, frameon=False)
finish(ax, art_pts + [p + d * 160 for p, d in sh], f'(c) On the shakers: {len(sh)} shakers, {n["control"]} controls')

fig.tight_layout()
out = os.path.join(HERE, '..', 'figures', 'fig_article.png')
fig.savefig(out, dpi=150)
print('wrote', out)
