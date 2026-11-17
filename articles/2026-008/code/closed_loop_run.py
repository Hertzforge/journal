"""Stage 2 closed-loop example (Section 7.4): one run, read from its scorecard.

    python closed_loop_run.py [SCORECARD.json]

The run is pinv_closed at its defaults, seed 0, frame-12x6-strong/line, from batch main of the MIMO Random law study.
Given SCORECARD.json, the script copies it into ../data/ first; with no argument it reads the copy already there, so
the article can be refreshed after the study's files are gone. Writes:

  ../data/closed_loop_summary.csv      every number Section 7.4 quotes, under its key (fill_article.py reads it as run.*)
  ../data/fig_closed_loop_modes.csv    each fitted mode: small-signal frequency, change and damping factor as played
                                       and under the reference drive (the figure's data)

Every number is read from the scorecard; nothing is computed here but percentages and a sign test.
Needs the standard library only. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
CARD = os.path.join(DATA, 'closed_loop_scorecard_s0_6x12_strong_pinv_closed.json')


def main():
    if len(sys.argv) > 1:
        shutil.copyfile(sys.argv[1], CARD)
    c = json.load(open(CARD))
    rc, st, ps = c['report_card'], c['stress'], c['structure_state']
    sl, soft = ps['service_line'], ps['signed']['by_effect']['softening']
    mem, alls = sl['member'], ps['signed']['all']
    nostr = c['by_drive_route']['stress']
    ds = c.get('default_stop') or {}
    v = {
        'problem': c['problem']['id'], 'seed': c['problem']['seed'], 'law': c['run']['law'],
        'law_parameters_given': len(c['run']['law_parameters']), 'model': c['run']['model'],
        'protections': c['outcome']['protections'], 'completed': c['outcome']['completed'],
        'loops_recorded': c['outcome']['record']['loops_recorded'], 'loops_asked': c['outcome']['record']['loops_asked'],
        'loops_total': c['runner_outcome']['loops_total'], 'full_level_loops': c['outcome']['full_level_loops'],
        'record_frames': c['outcome']['record']['frames'], 'frames_per_loop': c['run']['frames_per_loop'],
        'kept_mb': c['batch']['kept_bytes'] / (1 << 20),
        'software_commit': c['run']['software_commit'], 'scorer_version': c['scorer']['version'],
        'set_version': c['set']['version'], 'set_suite': c['set']['suite'],
        'default_stop_guard': ds.get('guard', ''), 'default_stop_loop': ds.get('loop', 0),
        'default_stop_error_db': ds.get('error_db', 0), 'default_stop_consecutive': ds.get('consecutive_loops', 0),
        'default_stop_full_level_loops_done': ds.get('full_level_loops_done', 0),
        # state as played, in service, and under the reference drive
        'member_change_played': mem['change_pct_played'], 'member_change_service': mem['change_pct_service'],
        'member_change_target': mem['change_pct_target'], 'member_change_diff': mem['difference_pct_points'],
        'member_zfac_played': mem['zfac_played'], 'member_zfac_service': mem['zfac_service'],
        'member_zfac_target': [m for m in ps['signed']['modes'] if m['effect'] == 'hardening'][0]['target_zfac'],
        'member_f0_hz': mem['f0_hz'],
        'soft_modes_played': sl['softening']['modes_played'], 'soft_modes_service': sl['softening']['modes_service'],
        'soft_change_played_p50': sl['softening']['change_pct_played_p10_p50_p90'][1],
        'soft_change_service_p50': sl['softening']['change_pct_service_p10_p50_p90'][1],
        'soft_change_target_p50': soft['target_change_pct_p10_p50_p90'][1],
        'soft_zfac_played_p50': sl['softening']['zfac_played_p10_p50_p90'][1],
        'soft_zfac_service_p50': sl['softening']['zfac_service_p10_p50_p90'][1],
        'soft_zfac_target_p50': soft['target_zfac_p10_p50_p90'][1],
        'modes_fitted': alls['modes_fitted'], 'sign_right_share': alls['sign_right_share'],
        'abs_error_pct_points_p50': alls['abs_error_pct_points_p50'],
        # report card
        'level_mean_db': rc['line_1_level']['mean_error_db'],
        'held_summed_db': rc['line_2_pattern']['held_out']['summed_rms_db'],
        'held_per_gauge_db': rc['line_2_pattern']['held_out']['per_channel_rms_db'],
        'held_grade': rc['line_2_pattern']['held_out']['grade'],
        'ctrl_summed_db': rc['line_2_pattern']['controls']['summed_rms_db'],
        'ctrl_per_gauge_db': rc['line_2_pattern']['controls']['per_channel_rms_db'],
        'ctrl_grade': rc['line_2_pattern']['controls']['grade'],
        'worst_band_db': rc['line_3_over_test']['worst_band_db'],
        'share_bands_over_alarm': rc['line_3_over_test']['share_of_bands_over_alarm'],
        'held_under3_share': rc['line_4_under_test']['share_of_held_out_bands_more_than_3_db_under'],
        'declared_deviation_db': rc['line_5_declared']['declared_deviation_rms_db'],
        'law_error_db': rc['line_5_declared']['law_error_rms_db'],
        'drives': rc['line_6_rig']['drives'], 'controls': rc['line_6_rig']['controls'],
        'condition_median': rc['line_6_rig']['condition_median'],
        'control_residual_db': rc['line_6_rig']['control_residual_rms_db'],
        'exact_fit_flag': rc['line_6_rig']['exact_fit_flag'],
        'stress_rms_db': st['rms'], 'stress_bias_db': st['bias'], 'stress_within3': st['in3'], 'stress_max_db': st['max'],
        'unmoved_stress_rms_db': nostr['rms'], 'unmoved_stress_bias_db': nostr['bias'], 'unmoved_stress_within3': nostr['in3'],
    }
    # The checks at their defaults across the same study: every run at default settings made with the checks at their
    # defaults, how it ended, and whether the same case with the checks widened completed. Read from the card folder
    # when the card is given; otherwise carried over from the summary already in data/.
    old = os.path.join(DATA, 'closed_loop_summary.csv')
    if len(sys.argv) > 1:
        folder = os.path.dirname(os.path.abspath(sys.argv[1]))
        n = done = div = cap = other = twin_ok = 0
        for name in sorted(os.listdir(folder)):
            if not name.endswith('.json') or name.endswith('_divopen.json'):
                continue
            o = json.load(open(os.path.join(folder, name))).get('outcome', {})
            if o.get('protections') != 'default':
                continue
            n += 1
            if o.get('completed'):
                done += 1
                continue
            g = (o.get('stop') or {}).get('guard')
            div += g == 'divergence'
            cap += g == 'cap_divergence'
            other += g not in ('divergence', 'cap_divergence')
            t = os.path.join(folder, name[:-5] + '_divopen.json')
            twin_ok += os.path.exists(t) and bool(json.load(open(t)).get('outcome', {}).get('completed'))
        v.update(checks_default_runs=n, checks_default_completed=done, checks_default_stopped=n - done,
                 checks_stopped_divergence=div, checks_stopped_cap=cap, checks_stopped_other=other,
                 checks_stopped_widened_completed=twin_ok)
    elif os.path.exists(old):
        for r in csv.DictReader(open(old)):
            if r['key'].startswith('checks_'):
                v[r['key']] = r['value']
    with open(os.path.join(DATA, 'closed_loop_summary.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['key', 'value'])
        for k, x in v.items():
            w.writerow([k, x])
    with open(os.path.join(DATA, 'fig_closed_loop_modes.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['mode', 'effect', 'f0_hz', 'change_pct_played', 'change_pct_target', 'zfac_played', 'zfac_target'])
        for m in ps['signed']['modes']:
            w.writerow([m['mode'], m['effect'], m['f0_hz'], 100 * m['change'], 100 * m['target_change'],
                        m['zfac'], m['target_zfac']])
    print(f'closed-loop example: {len(v)} values, {len(ps["signed"]["modes"])} modes')


if __name__ == '__main__':
    main()
