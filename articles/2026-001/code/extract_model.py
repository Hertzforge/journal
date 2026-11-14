"""Write the test model of Section 4.1 (seed 0) to ../data, for Figures 1 to 4 and the CAD model.

Usage:
    python extract_model.py EXPERIMENTS_DIR

EXPERIMENTS_DIR may also be given in the environment variable MM_EXPERIMENTS. It is the folder
holding the study's own frame_model.py and x1_random_study.py, which are not part of this bundle:
this script is the record of how the model_*.csv files were made. It imports the two files
unchanged and rebuilds seed 0 exactly as study MM-X1 builds it: the article geometry, the host frame, the service loads, the rig (held-out gauges, controls by
Effective Independence, shakers by greedy conditioning), the modes of the three configurations,
and one example of target, achieved and drive spectra with the line law. Unit perturbation 1
(3 percent), the case the article's examples use. One seed, a few seconds of compute.

Needs numpy, scipy and the two study files. Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
import csv
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
EXP = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('MM_EXPERIMENTS')
if not EXP:
    sys.exit('usage: python extract_model.py EXPERIMENTS_DIR  (the study files; not in this bundle)')
sys.path.insert(0, os.path.abspath(EXP))
import frame_model as fm  # noqa: E402
import x1_random_study as x1  # noqa: E402

SEED, PERT = 0, 1
AX = 'XYZ'


def write(name, header, rows):
    with open(os.path.join(DATA, name), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow([f'{v:.6g}' if isinstance(v, (float, np.floating)) else v for v in r])
    print(f'wrote data/{name} ({len(rows)} rows)')


def tube(sec):
    b = 2 * sec['c']; bi = np.sqrt(max(b * b - sec['A'], 0.0))
    return b, (b - bi) / 2


# ---------------------------------------------------------------- build seed 0 as MM-X1 does
art_nom = fm.make_article(SEED)
units = {u: fm.make_article(SEED, np.random.default_rng([SEED, u, PERT]), PERT) for u in (1, 2)}
host = fm.make_host(SEED, art_nom.meta['dims'])
zbase = fm.DampingField(SEED)
zs = {u: zbase.unit(np.random.default_rng([SEED, u, PERT, 9]), 0.3 * PERT) for u in (1, 2)}
mlab_nom = fm.Modal(*fm.suspend(art_nom), zbase)
held, ctrls, shakers = x1.choose_rig(SEED, art_nom, mlab_nom)
m = art_nom.meta
A, B = 1, 2  # unit A sets the targets in service; unit B is the unit tested

# ---------------------------------------------------------------- geometry
X = np.array(art_nom.xyz)
role = {n: [] for n in range(art_nom.nn)}
for n in m['mounts']:
    role[n].append('mount')
for n in m['bases']:
    role[n].append('component_base')
for n in m['tips']:
    role[n].append('component_tip')
for n in m['lumped']:
    role[n].append('lumped_mass')
rows = []
for n in range(art_nom.nn):
    mass = art_nom.lump.get(n, (0.0, 0.0))[0]
    rows.append(['article', n, *X[n], ';'.join(role[n]), mass])
XH = np.array(host.xyz)
for n in range(host.nn):
    r = ['mount'] if n in host.meta['mounts'] else []
    if n in host.lump:
        r.append('lumped_mass')
    rows.append(['host', n, *XH[n], ';'.join(r), host.lump.get(n, (0.0, 0.0))[0]])
write('model_nodes.csv', ['structure', 'node', 'x_m', 'y_m', 'z_m', 'role', 'lumped_mass_kg'], rows)

rows = []
for k, e in enumerate(art_nom.el):
    b, t = tube(e['sec'])
    rows.append(['article', k, e['i'], e['j'], e['group'], b, t])
for k, e in enumerate(host.el):
    b, t = tube(e['sec'])
    rows.append(['host', k, e['i'], e['j'], 'host', b, t])
write('model_elements.csv', ['structure', 'element', 'node_i', 'node_j', 'group', 'tube_width_m',
                             'wall_m'], rows)

# ---------------------------------------------------------------- rig: shakers and gauges
rows = []
for d in held:
    rows.append(['held_out', 'all', d // 6, AX[d % 6]])
for nc, c in ctrls.items():
    for d in c:
        rows.append(['control', f'controls_{nc}', d // 6, AX[d % 6]])
for (ns, nc), s in shakers.items():
    for k, d in enumerate(s):
        rows.append(['shaker', f'{ns}x{nc}', d // 6, AX[d % 6]])
for n in m['tips']:
    for a in AX:
        rows.append(['component_tip', 'all', n, a])
write('model_rig.csv', ['role', 'set', 'node', 'axis'], rows)

# ---------------------------------------------------------------- service loads (unit A)
Ka, Ma = units[A].assemble()
Kc, Mc, na = fm.couple(units[A], host)
mdA = fm.Modal(Kc, Mc, zs[A])
dofs, Fin = x1.service_forces(SEED, units[A], host, na)
rows = []
for k, d in enumerate(dofs):
    struct = 'host' if d >= na else 'article'
    node = (d - na) // 6 if d >= na else d // 6
    G = (np.abs(Fin[k]) ** 2).sum(0)
    rows.append([k, struct, node, AX[d % 6], float(np.sqrt(G.sum() * x1.DF))])
write('model_service_forces.csv', ['input', 'structure', 'node', 'axis', 'force_rms_relative'], rows)
# force autospectra summed over axes per force point, and coherence between host force points
pts = {}
for k, d in enumerate(dofs):
    key = ('host' if d >= na else 'article', (d - na) // 6 if d >= na else d // 6)
    pts.setdefault(key, []).append(k)
keys = list(pts)
idx = np.arange(0, x1.NF, 8)
rows = []
for i, k in enumerate(keys):
    G = (np.abs(Fin[pts[k]]) ** 2).sum((0, 1))
    for j in idx:
        rows.append([k[0], k[1], x1.F[j], G[j]])
write('model_service_force_spectra.csv', ['structure', 'node', 'f_hz', 'force_psd_relative'], rows)
host_pts = [i for i, k in enumerate(keys) if k[0] == 'host']
coh = []
for a_ in range(len(host_pts)):
    for b_ in range(a_ + 1, len(host_pts)):
        fa, fb = Fin[pts[keys[host_pts[a_]]]], Fin[pts[keys[host_pts[b_]]]]
        # coherence between the x components of two host force points
        ga, gb = fa[0], fb[0]
        cab = (np.conj(ga) * gb).sum(0); aa = (np.abs(ga) ** 2).sum(0); bb = (np.abs(gb) ** 2).sum(0)
        coh.append(np.abs(cab) ** 2 / np.maximum(aa * bb, 1e-300))
coh = np.array(coh)
print(f'service: {len(host_pts)} host force points, {len(keys) - len(host_pts)} article force points; '
      f'pairwise coherence between host points: median {np.median(coh):.2f}, '
      f'10th to 90th percentile {np.percentile(coh, 10):.2f} to {np.percentile(coh, 90):.2f}')

# ---------------------------------------------------------------- modes of the three configurations
mlab = fm.Modal(*fm.suspend(units[B]), zs[B])
KaB, MaB = units[B].assemble()
# kinetic-energy share of each mode carried by the component stalks (all stalk nodes but the base)
stalk_nodes = sorted({e['j'] for e in units[B].el if e['group'] == 'stalk'})
sd = np.array([6 * n + d for n in stalk_nodes for d in range(6)])


def comp_share(Phi, Mfull):
    return np.einsum('im,im->m', Phi[sd], (Mfull @ Phi)[sd])


rows = []
cs = comp_share(mlab.Phi, MaB)
for k in range(mlab.fn.size):
    rows.append(['lab_free', k + 1, mlab.fn[k], mlab.zeta[k], 1.0, cs[k]])
KcB, McB, naB = fm.couple(units[B], host)
mdB = fm.Modal(KcB, McB, zs[B])
share = np.einsum('im,ij,jm->m', mdB.Phi[:naB], MaB, mdB.Phi[:naB])
cs = comp_share(mdB.Phi[:naB], MaB)
for k in range(mdB.fn.size):
    rows.append(['service_mounted', k + 1, mdB.fn[k], mdB.zeta[k], share[k], cs[k]])
mf = fm.Modal(KaB, MaB, zs[B], fixed=fm.fixed_base_dofs(units[B]))
cs = comp_share(mf.Phi, MaB)
for k in range(mf.fn.size):
    rows.append(['rigid_base', k + 1, mf.fn[k], mf.zeta[k], 1.0, cs[k]])
write('model_modes.csv', ['configuration', 'mode', 'f_hz', 'damping_ratio', 'article_mass_share',
                          'component_energy_share'], rows)

# mode shapes, lab free-free, unit B: the first elastic mode (a component mode), the first two
# modes carried mostly by the chassis (component share under 0.1), and the first component mode
# above 300 Hz
csl = comp_share(mlab.Phi, MaB)
chassis_modes = [k for k in range(6, mlab.fn.size) if csl[k] < 0.1][:2]
high_comp = [k for k in range(6, mlab.fn.size) if mlab.fn[k] > 300 and csl[k] > 0.5][:1]
pick = [6] + chassis_modes + high_comp
tipd = np.array([6 * n + d for n in m['tips'] for d in range(3)])
chd = np.array([6 * n + d for n in m['chassis'] for d in range(3)])
rows = []
for k in pick:
    ph = mlab.Phi[:, k]; s = np.abs(ph[chd.tolist() + tipd.tolist()]).max()
    for n in range(units[B].nn):
        rows.append([k + 1, mlab.fn[k], csl[k], n, *(ph[6 * n:6 * n + 3] / s)])
write('model_mode_shapes.csv', ['mode', 'f_hz', 'component_energy_share', 'node', 'ux', 'uy', 'uz'], rows)

# ---------------------------------------------------------------- example spectra, line law
mnt_all = np.array([6 * n + d for n in m['mounts'] for d in range(3)])
U = np.unique(np.concatenate([ctrls[12], held, mnt_all]))
pos = {d: i for i, d in enumerate(U)}
YA_u = x1.acc(mdA, U, x1.modal_q(mdA, dofs, Fin))  # unit A in service, at the gauges used here
GA_u = x1.auto(YA_u)
YA = {d: YA_u[pos[d]] for d in U}; GA = {d: GA_u[pos[d]] for d in U}
rows, drows = [], []
ex_ctrl, ex_held = None, int(held[0])
for ns, nc in ((6, 12), (12, 12)):
    shk = shakers[(ns, nc)]; c = ctrls[nc]
    Hall = np.einsum('um,mf,sm->usf', mlab.Phi[U], mlab.h(x1.F) * -x1.W ** 2, mlab.Phi[shk], optimize=True)
    ci = np.array([pos[d] for d in c])
    Fd = x1.line_law(Hall[ci], YA_u[ci])
    G = x1.auto(np.einsum('usf,srf->urf', Hall, Fd, optimize=True))
    if ex_ctrl is None:
        ex_ctrl = int(c[np.argmax(GA_u[ci].sum(1))])  # the loudest control of the 12
    for kind, d in (('control', ex_ctrl), ('held_out', ex_held)):
        for j in range(x1.NF):
            rows.append([f'{ns}x{nc}', kind, d // 6, AX[d % 6], x1.F[j], GA[d][j], G[pos[d], j]])
    for k, d in enumerate(shk):
        Gd = (np.abs(Fd[k]) ** 2).sum(0)
        for j in range(0, x1.NF, 2):
            drows.append([f'{ns}x{nc}', k + 1, d // 6, AX[d % 6], x1.F[j], Gd[j]])
write('model_example_spectra.csv', ['rig', 'gauge', 'node', 'axis', 'f_hz', 'target_psd', 'achieved_psd'], rows)
write('model_example_drive.csv', ['rig', 'shaker', 'node', 'axis', 'f_hz', 'drive_psd_relative'], drows)

# ---------------------------------------------------------------- single-axis specification, Z
mnt = np.array([6 * n + 2 for n in m['mounts']])
GAm = np.array([GA[d] for d in mnt])
spec = x1.envelope(GAm)
Bm = x1.BANDS[3]; fc = np.exp(Bm @ np.log(x1.F)); band = GAm @ Bm.T
rows = []
for j in range(0, x1.NF, 2):
    rows.append(['spec', '', x1.F[j], spec[j]])
    rows.append(['mount_mean', '', x1.F[j], GAm[:, j].mean()])
for i, n in enumerate(m['mounts']):
    for j in range(0, x1.NF, 4):
        rows.append(['mount_line', n, x1.F[j], GAm[i, j]])
    for b in range(fc.size):
        rows.append(['mount_band', n, fc[b], band[i, b]])
write('model_single_axis_z.csv', ['curve', 'mount_node', 'f_hz', 'psd'], rows)

# ---------------------------------------------------------------- summary for the text
art_mass = units[B].rigid_translation(0) @ MaB @ units[B].rigid_translation(0)
Kh, Mh = host.assemble()
host_mass = host.rigid_translation(0) @ Mh @ host.rigid_translation(0)
print(f'seed 0: dims {np.round(m["dims"], 3)} m; article nodes {art_nom.nn}, elements {len(art_nom.el)}, '
      f'mass {art_mass:.2f} kg; host mass {host_mass:.1f} kg')
for e in (art_nom.el[0],):
    print('chassis tube width, wall (mm):', np.round(np.array(tube(e['sec'])) * 1e3, 2))
vert = [e for e in art_nom.el if abs(X[e['i']][2] - X[e['j']][2]) > 1e-6 and e['group'] == 'chassis']
print('post tube width, wall (mm):', np.round(np.array(tube(vert[0]['sec'])) * 1e3, 2))
for nb, nt, ft in zip(m['bases'], m['tips'], m['f_target']):
    L = np.linalg.norm(X[nt] - X[nb]); st = [e for e in art_nom.el if e['group'] == 'stalk' and e['j'] == nt][0]
    print(f'component at node {nb}: length {L * 1e3:.0f} mm, tube {tube(st["sec"])[0] * 1e3:.1f} mm, '
          f'tip mass {art_nom.lump[nt][0]:.3f} kg, design first mode {ft:.0f} Hz')
print('lumped masses (kg):', [round(art_nom.lump[n][0], 2) for n in m['lumped']])
print('host masses (kg):', [round(v[0], 1) for v in host.lump.values()])
print(f'modes to 4 kHz: lab {mlab.fn.size}, service {mdB.fn.size}, rigid base {mf.fn.size}')
print('lab elastic f (Hz):', np.round(mlab.fn[6:16], 1))
print('rigid-body f (Hz):', np.round(mlab.fn[:6], 2))
print('rigid-base f (Hz):', np.round(mf.fn[:10], 1))
print('service f (Hz), article share:', [(round(float(f), 1), round(float(v), 2)) for f, v in zip(mdB.fn[:20], share[:20])])
print('example control gauge', ex_ctrl // 6, AX[ex_ctrl % 6], '; held-out gauge', ex_held // 6, AX[ex_held % 6])
print('mode-shape modes:', [k + 1 for k in pick])

# ---------------------------------------------------------------- the numbers quoted in Section 4.1
S = [('article_length_m', m['dims'][0]), ('article_width_m', m['dims'][1]), ('article_height_m', m['dims'][2]),
     ('article_nodes', art_nom.nn), ('article_elements', len(art_nom.el)), ('article_mass_kg', art_mass),
     ('components', len(m['tips'])), ('lumped_masses', len(m['lumped'])), ('host_mass_kg', host_mass),
     ('host_force_points', len(host_pts)), ('article_force_points', len(keys) - len(host_pts)),
     ('host_force_coherence_median', np.median(coh)), ('host_force_coherence_p10', np.percentile(coh, 10)),
     ('host_force_coherence_p90', np.percentile(coh, 90)),
     ('modes_to_4khz_lab_free', mlab.fn.size), ('modes_to_4khz_service', mdB.fn.size),
     ('modes_to_4khz_rigid_base', mf.fn.size), ('rigid_body_f_min_hz', mlab.fn[0]), ('rigid_body_f_max_hz', mlab.fn[5])]
write('model_summary.csv', ['quantity', 'value'], [[k, float(v)] for k, v in S])
