"""Worked example, stage 1: score one reference run on each of two stage 1 problems.

    python example_run.py PROBLEM_FOLDER [PROBLEM_FOLDER ...] --runs RUN_ROOT

For each problem folder it
  1. computes a reference drive straight from the structure's own frequency response: at every line the
     drive spectral matrix is  D = Z G Z^H,  with G the line target at the controls and Z the inverse of
     the control frequency response that ignores every way of moving the controls weaker than 1/1000 of
     the strongest (the same rule the scorer uses for "what the rig can reach");
  2. writes that as a run result (manifest.json and drive_sdm_played.c16) under RUN_ROOT;
  3. scores the run result with the scorer beside this file (scorer.py, version 0.2-draft);
  4. writes the scorecard and the data behind the article's stage 1 figures and tables to ../data.

The reference run is not a fair entry and not a baseline. A fair entry sees the structure only through
identification, climbs the level ladder and runs closed loop with noise. This run has none of that. It is
here because anyone can reproduce it with NumPy alone, and it shows what a scorecard holds. It applies to
stage 1 only: on a structure that changes with level the drive would change the structure, and the
scorer reads such a run from played records.

Needs NumPy only. Copyright 2026 Kevin Cross. MIT license.
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

DATA = os.path.join(HERE, '..', 'data')
LAW_ID = 'reference_inverse'
G0 = 9.80665


def reference_drive(pr):
    """D = Z G Z^H on every line, (lines, drives, drives), V^2/Hz."""
    Z, _ = sc.pinv_trunc(pr.frf(pr.i_c))
    return Z @ pr.GA_full @ sc.herm(Z)


def write_run(folder, pr, D):
    os.makedirs(folder, exist_ok=True)
    g = pr.meta['grid']
    manifest = dict(
        what=('Reference run for the worked example: the drive is computed directly from the structure\'s '
              'frequency response. No identification, no level ladder, no loop, no noise. Not a fair entry.'),
        case_id=f"{pr.meta['structure']['id']}_s{int(pr.meta['structure']['seed']):02d}_{LAW_ID}",
        grid=dict(lo_line=g['lo_line'], n_lines=g['n_lines'], df_hz=g['df_hz']),
        law=dict(id=LAW_ID, params_given=dict(condition_limit=sc.COND, target='line')),
        frf_mode='exact', sim_seed=None, code_commit=None,
        outcome=dict(completed=True, record_window_status='not a time record', record_frames_drive=None,
                     record_loops_recorded=None, record_loops_asked=None, loops_at_full=None))
    with open(os.path.join(folder, 'manifest.json'), 'w') as fh:
        json.dump(manifest, fh, indent=1)
    D.astype('<c16').tofile(os.path.join(folder, 'drive_sdm_played.c16'))


def band_centres(pr):
    idx = np.unique(np.round(3 * np.log2(pr.f / 1000.0)).astype(int))
    return 1000.0 * 2.0 ** (idx / 3.0)


def channel_names(pr, rows):
    return [(pr.structure['outputs'][int(i)]['name'], pr.structure['outputs'][int(i)]['node'],
             pr.structure['outputs'][int(i)]['direction'].upper()) for i in rows]


def control_g_rms(pr):
    """The target's RMS acceleration at each control, g, over the band."""
    return np.sqrt(pr.GA_c.sum(1) * pr.df) / G0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('problems', nargs='+')
    ap.add_argument('--runs', required=True, help='where the run results are written (keep it out of a synced folder)')
    a = ap.parse_args()
    os.makedirs(DATA, exist_ok=True)
    band_rows, stress_rows, summary_rows, problem_rows = [], [], [], []
    for folder in a.problems:
        pr = sc.Problem(folder)
        assert pr.stage == 1, f'{folder} is not a stage 1 problem; the reference run is for stage 1 only'
        pid = f"{pr.meta['structure']['id']}/line"
        seed = int(pr.meta['structure']['seed'])
        tag = f"{pr.meta['structure']['id']}_s{seed:02d}"
        D = reference_drive(pr)
        run = os.path.join(a.runs, tag + '_' + LAW_ID)
        write_run(run, pr, D)
        card = sc.score(pr, run, target='line')
        with open(os.path.join(DATA, f'stage1_scorecard_{tag}.json'), 'w') as fh:
            json.dump(card, fh, indent=1)

        Fd = sc.factor(D)
        lab = sc.element_stress(*sc.stress_moments_drive(pr, Fd))
        _, G_c, G_h, _ = sc.score_drive(pr, D)
        fc = band_centres(pr)
        for group, G, Gref, rows in (('control', G_c, pr.GA_c, pr.i_c), ('held_out', G_h, pr.GA_h, pr.i_h)):
            E = sc.db10(G @ pr.B3.T, Gref @ pr.B3.T)
            for (name, node, axis), e in zip(channel_names(pr, rows), E):
                for f, v in zip(fc, e):
                    band_rows.append(dict(problem=pid, seed=seed, group=group, channel=name, node=node, axis=axis,
                                          band_centre_hz=f'{f:.4g}', error_db=f'{v:.4f}'))
        x = 20 * np.log10(lab['rms'] / pr.truth['rms'])
        groups = [e['group'] for e in json.load(open(os.path.join(folder, 'geometry.json')))['elements']]
        for k, v in enumerate(x):
            stress_rows.append(dict(problem=pid, seed=seed, element=k, group=groups[k], rms_stress_error_db=f'{v:.4f}'))

        rc, st = card['report_card'], card['stress']
        summary_rows.append(dict(
            problem=pid, seed=seed,
            level_mean_db=rc['line_1_level']['mean_error_db'],
            held_out_summed_db=rc['line_2_pattern']['held_out']['summed_rms_db'],
            held_out_grade=rc['line_2_pattern']['held_out']['grade'],
            held_out_per_channel_db=rc['line_2_pattern']['held_out']['per_channel_rms_db'],
            controls_summed_db=rc['line_2_pattern']['controls']['summed_rms_db'],
            controls_grade=rc['line_2_pattern']['controls']['grade'],
            controls_per_channel_db=rc['line_2_pattern']['controls']['per_channel_rms_db'],
            worst_band_db=rc['line_3_over_test']['worst_band_db'],
            share_of_bands_over_alarm=rc['line_3_over_test']['share_of_bands_over_alarm'],
            share_held_out_bands_3db_under=rc['line_4_under_test']['share_of_held_out_bands_more_than_3_db_under'],
            declared_deviation_rms_db=rc['line_5_declared']['declared_deviation_rms_db'],
            law_error_rms_db=rc['line_5_declared']['law_error_rms_db'],
            condition_median=rc['line_6_rig']['condition_median'], condition_max=rc['line_6_rig']['condition_max'],
            exact_fit_flag=rc['line_6_rig']['exact_fit_flag'],
            stress_rms_db=st['rms'], stress_mean_db=st['bias'], stress_p5_db=st['p5'], stress_p95_db=st['p95'],
            stress_share_within_3db=st['in3'], stress_worst_element_db=st['max'],
            stress_strip_mean_db=float(np.mean([v for v, g in zip(x, groups) if g == 'strip'])),
            r1_control_lines_inside=rc['reference_r1']['share_of_control_lines_inside'],
            drive_rms_n_min=min(card['drive']['rms_n']), drive_rms_n_max=max(card['drive']['rms_n']),
            drive_rms_n_total=float(np.sqrt(np.sum(np.square(card['drive']['rms_n']))))))
        el = pr.fn[pr.structure.get('rigid_modes', 6):]
        g = control_g_rms(pr)
        problem_rows.append(dict(
            problem=pid, seed=seed, stage=pr.stage, drives=pr.dshape.shape[1], controls=pr.i_c.size,
            held_out_gauges=pr.i_h.size, tips=pr.i_t.size, modes=pr.fn.size, elements=pr.truth['rms'].size,
            first_elastic_mode_hz=f'{el[0]:.1f}', elastic_modes_in_band=int(((el >= pr.f[0]) & (el <= pr.f[-1])).sum()),
            control_g_rms_median=f'{np.median(g):.2f}', control_g_rms_min=f'{g.min():.2f}', control_g_rms_max=f'{g.max():.2f}',
            lines=pr.f.size, band_lo_hz=pr.f[0], band_hi_hz=pr.f[-1], structure_sha256=pr.meta['structure']['sha256']))
        print(f"{pid} seed {seed}: declared {rc['line_5_declared']['declared_deviation_rms_db']:.4f} dB, "
              f"controls {rc['line_2_pattern']['controls']['per_channel_rms_db']:.3f} dB, "
              f"held out {rc['line_2_pattern']['held_out']['per_channel_rms_db']:.3f} dB, "
              f"stress mean {st['bias']:+.2f} dB rms {st['rms']:.2f} dB, exact-fit flag {rc['line_6_rig']['exact_fit_flag']}")

    def dump(name, rows):
        with open(os.path.join(DATA, name), 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    dump('fig_stage1_band_errors.csv', band_rows)
    dump('fig_stage1_element_stress.csv', stress_rows)
    dump('stage1_scorecard_summary.csv', summary_rows)
    dump('stage1_problems.csv', problem_rows)


if __name__ == '__main__':
    main()
