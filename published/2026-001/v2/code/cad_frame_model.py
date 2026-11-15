"""CAD model of the test article of Section 4.1 (seed 0), its service mounting and the lab rig.

Reads ../data/model_nodes.csv, model_elements.csv, model_rig.csv and model_service_forces.csv
(written by extract_model.py). Builds solids with build123d (square aluminum tubes along each
member, blocks for the tip and lumped masses, the host frame, mount pads, suspension cords and
shaker bodies with stingers), exports three STEP files to ../data/cad, and renders Figure 1 to
../figures/fig1_model_views.png from the CAD tessellation.

The geometry is the beam model's: tube centerlines, widths and walls as modeled. Mass blocks are
steel cubes of the modeled mass; shaker bodies, pads and cords are drawn to show position and
direction only and carry no modeled property.

Needs build123d (tested 0.13.0), numpy and matplotlib. Copyright 2026 Kevin Cross and Brandon
Zwink. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from build123d import Box, Compound, Cylinder, Location, Plane, export_step

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
CAD = os.path.abspath(os.path.join(HERE, '..', 'data', 'cad'))  # OCC's STEP writer refuses paths with '..'
os.makedirs(CAD, exist_ok=True)
MM = 1000.0
RIG = '6x12'          # the rig drawn in the lab view: 6 shakers, 12 controls
CONTROLS = 'controls_12'
AXV = {'X': np.array([1.0, 0, 0]), 'Y': np.array([0, 1.0, 0]), 'Z': np.array([0, 0, 1.0])}
HOST_DROP = 60.0      # mm, host frame drawn this far below the article mounts in the service view


def rows(name):
    return list(csv.DictReader(open(os.path.join(DATA, name))))


nodes = {(r['structure'], int(r['node'])): r for r in rows('model_nodes.csv')}
P = {k: np.array([float(r['x_m']), float(r['y_m']), float(r['z_m'])]) * MM for k, r in nodes.items()}
elems = rows('model_elements.csv')
rig = rows('model_rig.csv')
sforces = rows('model_service_forces.csv')


def members(structure):
    """Merge chains of collinear elements of one section into members (one tube solid each)."""
    els = [e for e in elems if e['structure'] == structure]
    deg = {}
    for e in els:
        for n in (int(e['node_i']), int(e['node_j'])):
            deg.setdefault(n, []).append(e)
    used, out = set(), []
    for e in els:
        if e['element'] in used:
            continue
        chain = [int(e['node_i']), int(e['node_j'])]; used.add(e['element'])
        key = (e['tube_width_m'], e['wall_m'], e['group'])
        for end in (0, 1):
            while True:
                n = chain[-1] if end else chain[0]
                d0 = P[(structure, chain[-1])] - P[(structure, chain[-2])] if end else \
                    P[(structure, chain[0])] - P[(structure, chain[1])]
                nxt = None
                for f in deg[n]:
                    if f['element'] in used or (f['tube_width_m'], f['wall_m'], f['group']) != key:
                        continue
                    o = int(f['node_j']) if int(f['node_i']) == n else int(f['node_i'])
                    d1 = P[(structure, o)] - P[(structure, n)]
                    if np.linalg.norm(np.cross(d0, d1)) < 1e-6 * np.linalg.norm(d0) * np.linalg.norm(d1):
                        nxt = (f, o); break
                if nxt is None:
                    break
                used.add(nxt[0]['element'])
                chain = chain + [nxt[1]] if end else [nxt[1]] + chain
        out.append((chain[0], chain[-1], float(e['tube_width_m']) * MM, float(e['wall_m']) * MM, e['group']))
    return out


def frame_plane(p0, p1):
    ex = (p1 - p0) / np.linalg.norm(p1 - p0)
    ref = np.array([0, 0, 1.0]) if abs(ex[2]) < 0.9 else np.array([0, 1.0, 0])
    ez = np.cross(ex, ref); ez /= np.linalg.norm(ez)
    return Plane(origin=tuple((p0 + p1) / 2), x_dir=tuple(ex), z_dir=tuple(ez))


def tube(p0, p1, b, t, extend=0.0):
    L = np.linalg.norm(p1 - p0) + extend
    pl = frame_plane(p0, p1)
    outer = Box(L, b, b); inner = Box(L + 1.0, b - 2 * t, b - 2 * t)
    return pl * (outer - inner)


def block(p, mass_kg, rho=7850.0):
    s = (mass_kg / rho) ** (1 / 3) * MM
    return Location(tuple(p)) * Box(s, s, s)


def rod(p0, p1, r):
    L = np.linalg.norm(p1 - p0); d = (p1 - p0) / L
    ref = np.array([1.0, 0, 0]) if abs(d[0]) < 0.9 else np.array([0, 1.0, 0])
    xd = np.cross(d, ref); xd /= np.linalg.norm(xd)
    return Plane(origin=tuple((p0 + p1) / 2), x_dir=tuple(xd), z_dir=tuple(d)) * Cylinder(r, L)


# ---------------------------------------------------------------- parts (built fresh for each use,
# because an assembly node takes ownership of its children)
drop = np.array([0, 0, -HOST_DROP])
mounts_art = [P[k] for k, r in nodes.items() if k[0] == 'article' and 'mount' in r['role']]
centroid = np.mean([P[k] for k in P if k[0] == 'article'], axis=0)
shk = [r for r in rig if r['role'] == 'shaker' and r['set'] == RIG]


def art_tubes():
    return [tube(P[('article', a)], P[('article', b)], w, t, extend=w) for a, b, w, t, g in members('article')]


def art_masses():
    return [block(P[k], float(r['lumped_mass_kg'])) for k, r in nodes.items()
            if k[0] == 'article' and float(r['lumped_mass_kg']) > 0]


def host_parts():
    return ([tube(P[('host', a)] + drop, P[('host', b)] + drop, w, t, extend=w) for a, b, w, t, g in members('host')]
            + [block(P[k] + drop, float(r['lumped_mass_kg'])) for k, r in nodes.items()
               if k[0] == 'host' and float(r['lumped_mass_kg']) > 0])


def pads():
    return [rod(p + np.array([0, 0, -10.0]), p + drop + np.array([0, 0, 25.0]), 9.0) for p in mounts_art]


def cords():
    return [rod(p, p + np.array([0, 0, -180.0]), 2.0) for p in mounts_art]


shaker_draw = []
for r in shk:
    p = P[('article', int(r['node']))]; a = AXV[r['axis']]
    side = -1.0 if (p - centroid) @ a <= 0 else 1.0     # body on the outside of the article
    shaker_draw.append((p, p + side * a * 15.0, p + side * a * 90.0, p + side * a * 160.0, side * a))


def shakers():
    out = []
    for p, s0, s1, b1, d in shaker_draw:
        out += [rod(s0, s1, 2.0), rod(s1, b1, 32.0)]
    return out


def article():
    return Compound(children=art_tubes() + art_masses(), label='article')


export_step(article(), os.path.join(CAD, 'frame_model_seed0_article.step'))
export_step(Compound(children=[article(), Compound(children=host_parts(), label='host_frame'),
                               Compound(children=pads(), label='mounts')], label='service'),
            os.path.join(CAD, 'frame_model_seed0_service.step'))
export_step(Compound(children=[article(), Compound(children=cords(), label='suspension'),
                               Compound(children=shakers(), label=f'shakers_{RIG}')], label=f'lab_{RIG}'),
            os.path.join(CAD, f'frame_model_seed0_lab_{RIG}.step'))
print('wrote data/cad/frame_model_seed0_article.step, _service.step, _lab_6x12.step')


# ---------------------------------------------------------------- render from the tessellation
LIGHT = np.array([-0.4, -0.6, 0.8]); LIGHT /= np.linalg.norm(LIGHT)


def tris(shape, rgb, tol=0.4):
    v, f = shape.tessellate(tol)
    V = np.array([[p.X, p.Y, p.Z] for p in v]); T = V[np.array(f)]
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    shade = 0.35 + 0.65 * np.abs(n @ LIGHT)
    return T, np.clip(np.array(rgb)[None, :] * shade[:, None], 0, 1)


def draw(ax, parts, elev, azim):
    for shape, rgb in parts:
        T, C = tris(shape, rgb)
        ax.add_collection3d(Poly3DCollection(T, facecolors=C, edgecolors='none', linewidths=0))
    ax.view_init(elev=elev, azim=azim)


def finish(ax, pts, title):
    pts = np.array(pts); lo, hi = pts.min(0), pts.max(0); c = (lo + hi) / 2; r = (hi - lo).max() / 2 * 0.78
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1)); ax.set_axis_off(); ax.set_title(title, fontsize=10)


ALU, STEEL, HOSTC, GRAY = (0.72, 0.75, 0.80), (0.35, 0.35, 0.38), (0.80, 0.70, 0.55), (0.55, 0.55, 0.55)
gauge = {('article', int(r['node'])) for r in rig}
fig = plt.figure(figsize=(14, 5.0))

# (a) the article, with component tips and lumped masses called out
ax = fig.add_subplot(1, 3, 1, projection='3d', computed_zorder=False)
draw(ax, [(Compound(art_tubes()), ALU), (Compound(art_masses()), STEEL)], 22, -58)
for k, r in nodes.items():
    if k[0] != 'article':
        continue
    if 'component_tip' in r['role']:
        ax.scatter(*P[k], marker='^', s=60, color='#E69F00', edgecolors='black', zorder=5)
    if 'mount' in r['role']:
        ax.scatter(*P[k], marker='s', s=45, facecolors='none', edgecolors='black', linewidths=1.5, zorder=5)
ax.scatter([], [], marker='^', s=60, color='#E69F00', edgecolors='black', label='Component tip mass')
ax.scatter([], [], marker='s', s=45, facecolors='none', edgecolors='black', label='Mount point (4)')
ax.plot([], [], 's', color=STEEL, label='Lumped mass (steel block)')
ax.legend(loc='lower left', fontsize=8, frameon=False)
finish(ax, [P[k] for k in P if k[0] == 'article'], '(a) Test article: tube chassis and components')

# (b) service: the article bolted to the host frame, service force points marked
ax = fig.add_subplot(1, 3, 2, projection='3d', computed_zorder=False)
draw(ax, [(Compound(host_parts()), HOSTC), (Compound(pads()), GRAY), (Compound(art_tubes()), ALU),
          (Compound(art_masses()), STEEL)], 28, -58)
seen = set()
for r in sforces:
    k = (r['structure'], int(r['node']))
    if k in seen:
        continue
    seen.add(k)
    p = P[k] + (drop if k[0] == 'host' else 0)
    if k[0] == 'host':
        ax.scatter(*p, marker='*', s=140, color='#D55E00', edgecolors='black', zorder=5)
    else:
        ax.scatter(*p, marker='P', s=80, color='#CC79A7', edgecolors='black', zorder=5)
ax.scatter([], [], marker='*', s=140, color='#D55E00', edgecolors='black', label='Service force on host frame (9)')
ax.scatter([], [], marker='P', s=80, color='#CC79A7', edgecolors='black', label='Weaker force on article (2)')
ax.legend(loc='lower left', fontsize=8, frameon=False)
finish(ax, [P[k] + (drop if k[0] == 'host' else 0) for k in P], '(b) In service: bolted at 4 mounts to the host frame')

# (c) lab: suspension, six shakers, gauges by role
ax = fig.add_subplot(1, 3, 3, projection='3d', computed_zorder=False)
draw(ax, [(Compound(cords()), GRAY), (Compound(art_tubes()), ALU),
          (Compound(art_masses()), STEEL), (Compound(shakers()), (0.25, 0.35, 0.55))], 22, -58)
for p, s0, s1, b1, d in shaker_draw:
    ax.quiver(*(p + d * 70), *(-d * 55), color='black', linewidth=1.4, arrow_length_ratio=0.35, zorder=6)
style = {'control': dict(marker='o', s=55, color='#0072B2', edgecolors='black'),
         'held_out': dict(marker='D', s=50, color='white', edgecolors='#D55E00', linewidths=1.8),
         'component_tip': dict(marker='^', s=60, color='#E69F00', edgecolors='black')}
done = set()
for r in rig:
    role = r['role']
    if role == 'control' and r['set'] != CONTROLS or role not in style:
        continue
    k = ('article', int(r['node']))
    if (role, k) in done:
        continue
    done.add((role, k))
    ax.scatter(*P[k], zorder=7, **style[role])
n_c = sum(1 for r in rig if r['role'] == 'control' and r['set'] == CONTROLS)
n_h = sum(1 for r in rig if r['role'] == 'held_out')
ax.scatter([], [], label=f'Control gauge point ({n_c} channels)', **style['control'])
ax.scatter([], [], label=f'Held-out gauge point ({n_h} channels)', **style['held_out'])
ax.scatter([], [], label='Component tip gauge (never a control)', **style['component_tip'])
ax.plot([], [], color='black', label='Shaker and its force direction (6)')
ax.legend(loc='lower left', fontsize=8, frameon=False)
pts = [P[k] for k in P if k[0] == 'article'] + [b1 for _, _, _, b1, _ in shaker_draw]
finish(ax, pts, '(c) In the lab: soft suspension, 6 shakers, 12 controls')

fig.tight_layout()
out = os.path.join(HERE, '..', 'figures', 'fig1_model_views.png')
fig.savefig(out, dpi=150)
print('wrote', out)
