"""Worked example, stage 2: what is known about a stage 2 problem before any control law runs.

    python stage2_known.py PROBLEM_FOLDER [PROBLEM_FOLDER ...]

Reads only the problem folders (problem.json, structure.json, target_line.c16, scoring/) and, for the
member's design, ../data/member_design.json (the generator's record of the member, kept with the article). Writes to
../data:

  stage2_known.csv     one row per problem: the article in service (unit B at the fixed point of its level
                       rule), the member's mode in service, the same modes on the shakers under the reference
                       drive (level_targets), what the rig can reach at its controls (declared deviation, from
                       the small-signal model), the control level, and the checks the folder carries
  stage2_member.csv    the member as designed, one row per tier (strip, mass, tuned frequency, its first modes,
                       the strip's cubic stiffness ratio)
  fig_level_rule.csv   the rule of the member's mode and of the article's median softening mode, sampled over
                       the amplitude ratio r, for the level figure (the 6 x 12 rig, both tiers)
  fig_member.csv       the strip pair's own stiffening (sine backbone at amplitude A, and the random-drive
                       equivalent at RMS A), from its cubic stiffness ratio, for the member figure

No control law, no run and no simulator are involved. Needs NumPy only. Copyright 2026 Kevin Cross. MIT license.
"""
import argparse
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scorer as sc  # noqa: E402
import reference_model as rm  # noqa: E402

DATA = os.path.join(HERE, '..', 'data')
MEMBER = json.load(open(os.path.join(DATA, 'member_design.json')))   # the member's design, one entry per problem
G0 = 9.80665


def declared(pr):
    """What the rig can reach at its controls against the target (the scorer's line 5), dB RMS over controls and bands."""
    Hc = pr.frf(pr.i_c)
    Z, s = sc.pinv_trunc(Hc)
    P = Hc @ Z
    gp = np.real(np.einsum('fii->if', P @ pr.GA_full @ sc.herm(P)))
    dev = sc.db10(gp @ pr.B3.T, pr.GA_c @ pr.B3.T)
    return float(np.sqrt(np.mean(dev ** 2))), float(np.median(s[:, 0] / s[:, -1]))


def member_mode(st):
    """The member's translation mode: the mode with the largest rise term."""
    rise = np.array([m['level']['rise'] for m in st['modes']])
    return int(np.argmax(rise))


def softening_modes(pr, st):
    """Elastic modes in the band whose target is a drop."""
    tc = np.array(st['level_targets']['frequency_change'])
    el = np.arange(len(st['modes'])) >= st.get('rigid_modes', 6)
    inband = (pr.fn >= pr.f[0]) & (pr.fn <= pr.f[-1])
    return np.flatnonzero(el & inband & (tc < 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('problems', nargs='+')
    a = ap.parse_args()
    os.makedirs(DATA, exist_ok=True)
    rows, members, rule_rows, backbone_rows = [], {}, [], []
    for folder in a.problems:
        pr = sc.Problem(folder)
        assert pr.stage == 2, f'{folder} is not a stage 2 problem'
        meta, st = pr.meta, pr.structure
        sid, seed = meta['structure']['id'], int(meta['structure']['seed'])
        tier = meta['structure']['variant']
        lt, ss = st['level_targets'], meta['service_state']
        tc, tz = np.array(lt['frequency_change']), np.array(lt['damping_factor'])
        m = member_mode(st)
        soft = softening_modes(pr, st)
        dd, cond = declared(pr)
        g = np.sqrt(pr.GA_c.sum(1) * pr.df) / G0
        ck = meta['provenance']['checks']
        stm = rm.load_structure(folder)
        fmax = float(np.max(rm.max_frequency(stm)))
        q = lambda v, p: float(np.percentile(v, p))
        rows.append(dict(
            problem=sid, seed=seed, tier=tier, drives=pr.dshape.shape[1], controls=pr.i_c.size, effects='+'.join(pr.effects),
            modes=pr.fn.size, modes_softening_in_band=int(soft.size),
            control_g_rms_median=float(np.median(g)), control_g_rms_min=float(g.min()), control_g_rms_max=float(g.max()),
            declared_deviation_rms_db=dd, condition_median=cond,
            service_member_f0_hz=ss['member']['f0_hz'], service_member_change_pct=100 * ss['member']['frequency_change'],
            service_member_damping_factor=ss['member']['damping_factor'], service_member_share_in_strips=ss['member']['e_H'],
            service_member_mid_span_rms_mm=1e3 * ss['member']['mid_span_rms_m'],
            service_article_modes=ss['article']['modes'],
            service_article_change_pct_p10=100 * ss['article']['frequency_change_p10_p50_p90'][0],
            service_article_change_pct_p50=100 * ss['article']['frequency_change_p10_p50_p90'][1],
            service_article_change_pct_p90=100 * ss['article']['frequency_change_p10_p50_p90'][2],
            service_article_damping_p50=ss['article']['damping_factor_p10_p50_p90'][1],
            shakers_member_f0_hz=float(pr.fn[m]), shakers_member_target_change_pct=100 * float(tc[m]),
            shakers_member_target_damping_factor=float(tz[m]),
            shakers_soft_target_change_pct_p10=100 * q(tc[soft], 10), shakers_soft_target_change_pct_p50=100 * q(tc[soft], 50),
            shakers_soft_target_change_pct_p90=100 * q(tc[soft], 90), shakers_soft_target_damping_p50=q(tz[soft], 50),
            shakers_soft_target_damping_max=float(tz[soft].max()),
            member_rule_rise=st['modes'][m]['level']['rise'], member_rule_rise_cap=st['modes'][m]['level']['rise_cap'],
            tier_member_rise=lt['at_full_level']['hardening_rise'], tier_member_rms_mm=1e3 * lt['at_full_level']['member_rms_m'],
            highest_reachable_hz=fmax, nyquist_hz=meta['grid']['fs_hz'] / 2,
            check_frf_parity=ck['frf_parity']['value'], check_stress_parity=ck['stress_frf_parity']['value'],
            check_runner_case_equal=ck['runner_structure_equal'],
            check_step_residual_db_median=ck['equalized_step_residual']['db_median'],
            check_step_residual_db_p95=ck['equalized_step_residual']['db_p95'],
            check_step_residual_db_max=ck['equalized_step_residual']['db_max'],
            structure_sha256=meta['structure']['sha256']))

        # the member as designed (one per tier), from the generator's record kept in data/member_design.json
        md = MEMBER.get(os.path.basename(os.path.normpath(folder)))
        if tier not in members and md is not None:
            d = md['member']['design']
            mf = md['fe']
            members[tier] = dict(tier=tier, seed=seed, strips=2, strip_length_mm=1e3 * d['L'],
                                 strip_width_each_mm=1e3 * d['b'] / 2, strip_thickness_mm=1e3 * d['t'],
                                 strip_spacing_mm=1e3 * d['s'], strip_material='301 stainless, full hard',
                                 mass_kg=d['M'], mass_material=d['block']['material'], mass_along_mm=1e3 * d['block']['l'],
                                 mass_across_mm=1e3 * d['block']['w'], mass_thin_mm=1e3 * d['block']['h'],
                                 tuned_hz=d['f_tuned'], k1_n_per_m=d['k1'], k3_n_per_m3=d['k3'], gamma_per_m2=d['gamma'],
                                 translation_hz=mf.get('translation_hz'), rocking_hz=mf.get('rocking_hz'), pitch_hz=mf.get('pitch_hz'),
                                 replaced_component=md['member']['component'])
            for A in np.linspace(0, 0.5e-3, 101):                    # the strip pair alone: sine backbone and random equivalent
                backbone_rows.append(dict(tier=tier, amplitude_mm=1e3 * A,
                                          sine_change_pct=100 * (np.sqrt(1 + 0.75 * d['gamma'] * A ** 2) - 1),
                                          random_rms_change_pct=100 * (np.sqrt(1 + 3 * d['gamma'] * A ** 2) - 1)))

        # the rule, sampled, for the level figure (one structure per tier: the 6 x 12 rig)
        if sid.startswith('frame-12x6-'):
            k = soft[np.argsort([st['modes'][i]['level']['drop'] for i in soft])[soft.size // 2]]
            for r in np.linspace(0, 2.5, 201):
                f, z = rm.level_state(stm, r)
                for mode, curve in ((m, 'member'), (k, 'softening')):
                    rule_rows.append(dict(tier=tier, curve=curve, mode=int(mode), f0_hz=float(pr.fn[mode]), r=float(r),
                                          change_pct=100 * float(f[mode] / pr.fn[mode] - 1),
                                          damping_factor=float(z[mode] / pr.zeta[mode])))
            lk, lv = st['modes'][k]['level'], st['modes'][m]['level']
            print(f'{sid}: member mode {m} ({pr.fn[m]:.1f} Hz) rise {lv["rise"]:.5f} cap {lv["rise_cap"]:.3f}; median softening '
                  f'mode {k} ({pr.fn[k]:.1f} Hz): drop {lk["drop"]:.4f}, damping gain {lk["damping_gain"]:.3f}')
        print(f'{sid} s{seed}: service member {100 * ss["member"]["frequency_change"]:+.2f} %, shakers member target '
              f'{100 * tc[m]:+.2f} %, softening p50 {100 * q(tc[soft], 50):+.2f} %, declared {dd:.2f} dB, controls {np.median(g):.1f} g RMS')

    def dump(name, rr):
        with open(os.path.join(DATA, name), 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rr[0].keys()))
            w.writeheader()
            w.writerows(rr)
    dump('stage2_known.csv', rows)
    dump('stage2_member.csv', list(members.values()))
    dump('fig_level_rule.csv', rule_rows)
    dump('fig_member.csv', backbone_rows)


if __name__ == '__main__':
    main()
