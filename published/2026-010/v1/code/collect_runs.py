"""Collect the result of record of every study run this article uses into one table.

    PYTHONDONTWRITEBYTECODE=1 python collect_runs.py CARDS_DIR RUNS_DIR PROBLEMS_DIR

CARDS_DIR is the study's scorecards (cards/main of the results record, DOI 10.5281/zenodo.24310746), PROBLEMS_DIR the
data set's problems/ (DOI 10.5281/zenodo.24310742), and RUNS_DIR the study's run folders, which hold the played spectra (kept with the study's run
records; the release does not carry them).

The result of record of a case (one structure, one setup, one law, one setting, one way of treating the measured
frequency response, one stage) is the run with the controller's checks widened if that run completed, else the run
with the checks at their defaults if it completed. A case with neither has no result and is left out (three cases
in the study, all on the setup with three shakers). Only scorecards are read, except for the signed mean band error
at the control gauges and at the held-out gauges, which the scorecard does not hold: for the runs at each law's
default settings on the linear structures it is recomputed from the run's played response (response_psd_played.f4)
and the problem's service response of unit A (scoring/service_a_psd.f8), in one-third-octave bands grouped as
round(3 log2(f / 1000)), which is the grouping of the study's own independent check. These spectra carry the
simulator's noise floor, while at the linear stage the scorer scores the played drive through the structure's
small-signal model, which carries none; on a run reading about 20 dB under its target the noise floor lifts the
recomputed reading (one run, s9_3x12_none_min_drive, differs from the scorer's level line by 2.3 dB). No result
in the article depends on this difference.

Writes ../data/runs_of_record.csv. Needs NumPy. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
args = sys.argv[1:]
if len(args) != 3:
    sys.exit('usage: collect_runs.py CARDS_DIR RUNS_DIR PROBLEMS_DIR')
CARDS, RUNS, PROBLEMS = args


def arr(folder, e):
    return np.fromfile(os.path.join(folder, e['file']), e['dtype']).reshape(e['shape'])


def signed_means(run_id, seed, ns, nc, variant):
    """Mean dB band error at the control gauges and at the held-out gauges (not the tips), from the played record."""
    name = f'frame-{nc}x{ns}' + ('' if variant == 'none' else f'-{variant}') + f'_s{seed:02d}'
    pf, rf = os.path.join(PROBLEMS, name), os.path.join(RUNS, run_id)
    meta = json.load(open(os.path.join(pf, 'problem.json')))
    st = json.load(open(os.path.join(pf, meta['structure']['file'])))
    roles = [(o['role'], o.get('group')) for o in st['outputs']]
    ic = [i for i, r in enumerate(roles) if r[0] == 'control']
    ih = [i for i, r in enumerate(roles) if r == ('held_out', 'gauge')]
    g = meta['grid']
    f = (g['lo_line'] + np.arange(g['n_lines'])) * g['fs_hz'] / g['nfft']
    psd = np.fromfile(os.path.join(rf, 'response_psd_played.f4'), '<f4').astype(float).reshape(g['n_lines'], -1)
    GA = arr(pf, meta['scoring']['service_a_psd'])          # (control + held-out gauges, lines), in that order
    band = np.round(3 * np.log2(f / 1000)).astype(int)
    out = []
    for idx, rows in ((ic, slice(0, len(ic))), (ih, slice(len(ic), len(ic) + len(ih)))):
        E = np.array([10 * np.log10(psd[band == b][:, idx].mean(0) / GA[rows][:, band == b].mean(1)) for b in np.unique(band)])
        out.append(float(E.mean()))
    return out


def main():
    best = {}
    for p in sorted(glob.glob(os.path.join(CARDS, '*.json'))):
        d = json.load(open(p))
        j = d['job']
        if not (d.get('scored') and d['outcome'].get('completed')):
            continue
        key = (j['seed'], j['rig'], j['variant'], j['law'], j['setting'], j['frf'])
        widened = p.endswith('_divopen.json')
        if key in best and best[key][0] and not widened:
            continue
        best[key] = (widened, d)
    rows = []
    for key, (widened, d) in sorted(best.items(), key=lambda kv: str(kv[0])):
        j, rc, c, s = d['job'], d['report_card'], d['card'], d['stress']
        row = dict(seed=j['seed'], setup=j['rig'], shakers=j['ns'], control_gauges=j['nc'], same_count=int(j['ns'] == j['nc']),
                   stage_variant=j['variant'], law=j['law'], setting=j['setting'], frf=j['frf'],
                   checks='widened' if widened else 'default', run_id=j['id'],
                   control_band_rms=c['c_b3_rms'], control_summed_rms=c['c_sum3_rms'],
                   held_band_rms=c['h_b3_rms'], held_summed_rms=c['h_sum3_rms'], level_mean_all=c['level_mean'],
                   worst_band_over=c['worst_over_b3'], share_bands_over6=c['share_over6_b3'],
                   control_grade=rc['line_2_pattern']['controls']['grade'], held_grade=rc['line_2_pattern']['held_out']['grade'],
                   level_within=int(rc['line_1_level']['within']), alarm=int(rc['line_3_over_test']['alarm']),
                   exact_fit_flag=int(rc['line_6_rig']['exact_fit_flag']), condition_median=rc['line_6_rig']['condition_median'],
                   declared_rms=c['declared_b3_rms'], law_error_rms=c['vs_declared_b3_rms'],
                   stress_rms=s['rms'], stress_mean=s['bias'], stress_p95=s['p95'], stress_in3=s['in3'],
                   tip_q10_mean=d['ers']['q10_tip']['mean'] if d.get('ers') else '',
                   control_mean='', held_mean='')
        if j['variant'] == 'none' and j['setting'] == 'default' and j['frf'] == 'hold':
            row['control_mean'], row['held_mean'] = signed_means(j['id'], j['seed'], j['ns'], j['nc'], j['variant'])
        rows.append(row)
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, 'runs_of_record.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (f'{v:.6g}' if isinstance(v, float) else v) for k, v in r.items()})
    print(f'{len(rows)} cases of record written')


if __name__ == '__main__':
    main()
