"""Write the record's numbers that the laws article quotes and the cards do not hold: the screens,
the agreement between the two versions, the parity of the ports and the laws' published defaults.
Standard library only. Copyright 2026 Kevin Cross. MIT license.

    python -I facts.py RECORD SUITE ENGINE STUDY_RUNS RUNNER_FORMAT HELDOUT

RECORD is the results record's folder of the MIMO Sine benchmark effort (with `experiments/`,
`Did_Not_Work.md` and the decisions file beside it as `DECISIONS.md`, or its path in the environment
variable DECISIONS). SUITE is the suite's repository (with `sine/FORMAT_SINE.md`). ENGINE is a clone
of the Hertzforge repository with `origin/main` fetched; it is read with `git show` and `git diff`
only. STUDY_RUNS is read for one card, to name the commit the study ran. RUNNER_FORMAT is the
benchmark runner's `FORMAT_RUN.md`, read for its table of protective settings. HELDOUT is the
held-back problems' folder, read only for the names of its problem folders (no audit run is read). Every value is written with
the file it came from and how it was read. It runs nothing else and reads no audit run.
"""
import collections
import csv
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
LAWS = ['matrix', 'paired', 'ratio', 'steepest_descent', 'secant']
# The screens' records name the candidate laws by their effort codes; these files and the article use
# their names. ../data/README.md maps the two.
RECORD_ARM = {'k2f': 'family_inverse', 'k3': 'followed_poles', 'k3_m9d': 'followed_poles_m9d',
              'k4': 'level_ladder', 'k4_sw': 'level_ladder_sw', 'k5': 'rls_dither',
              'j1': 'pole_trajectory', 'j2': 'amplitude_indexed', 'j3': 'placed_poles', 'j4': 'preview',
              'j4f': 'preview_frozen'}


def arm_id(arm):
    return RECORD_ARM.get(arm, arm)


CRATES = ['crates/hertzforge-mimo-sine-law-math', 'crates/hertzforge-mimo-sine',
          'crates/hertzforge-mimo-sine-laws']


def write_csv(name, header, table):
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, name), 'w', newline='') as file:
        out = csv.writer(file, lineterminator='\n')
        out.writerow(header)
        out.writerows(table)
    print('wrote', name, len(table), 'rows')


def grab(text, pattern, what, group=1):
    m = re.search(pattern.replace(' ', r'\s+'), text, re.S)
    if not m:
        raise SystemExit(f'not found: {what} ({pattern})')
    return m.group(group)


def git(engine, *args):
    return subprocess.run(['git', '-C', engine] + list(args), check=True, capture_output=True,
                          text=True).stdout


def main(record, suite, engine, study_runs, runner_format, heldout):
    facts = []

    def add(key, value, source, how):
        facts.append([key, value, source, how])

    # The code the study ran, and main.
    card = json.load(open(sorted(glob.glob(os.path.join(study_runs, 'study', '*', '*', 'card.json')))[0]))
    run_commit = card['run']['code_commit']
    main_commit = git(engine, 'rev-parse', 'origin/main').strip()
    changed = [line for line in git(engine, 'diff', '--name-only', run_commit, 'origin/main', '--', *CRATES)
               .splitlines() if line.strip()]
    add('run_commit', run_commit, 'study card run.code_commit', 'the first card of the study set')
    add('main_commit', main_commit, 'git rev-parse origin/main', '')
    for name, version in (('study', 'hertzforge'), ('study_py', 'python')):
        shas = collections.Counter(json.load(open(p))['run'].get('runner_sha256') for p in
                                   glob.glob(os.path.join(study_runs, name, '*', '*', 'card.json')))
        add(f'runner_sha256_{version}', ' '.join(f'{s}' for s, _ in shas.most_common()),
            f'cards of {name}, run.runner_sha256', f'{len(shas)} distinct over {sum(shas.values())} cards')
    add('run_base', git(engine, 'merge-base', run_commit, 'origin/main').strip(), 'git merge-base run_commit origin/main', 'where the runner branch leaves main')
    runner_dir = 'crates/sds-control/examples/msnb_run'
    on_main = subprocess.run(['git', '-C', engine, 'cat-file', '-e', f'origin/main:{runner_dir}'], capture_output=True).returncode == 0
    add('runner_on_main', 'yes' if on_main else 'no', f'git cat-file -e origin/main:{runner_dir}', '')
    add('law_crate_files_changed', len(changed), 'git diff --name-only run_commit origin/main -- the three MIMO Sine crates', '')
    guide = git(engine, 'show', 'origin/main:docs/control-laws.md')
    add('matrix_carry_default', grab(guide, r'`carry` \| The weight on the carry, 0 to 1; 0 is the correction alone \(default ([0-9.]+)', 'carry'),
        'docs/control-laws.md on main', '`matrix` key table, carry')
    add('matrix_fixed_gain', grab(guide, r'`fixed_gain` \| The gain when the rule is fixed \(default ([0-9.]+)', 'fixed gain'),
        'docs/control-laws.md on main', 'key table, fixed_gain')
    add('matrix_regularization', grab(guide, r'Regularization of the inverse, relative to its largest singular value \(default ([0-9.]+)\)', 'reg'),
        'docs/control-laws.md on main', 'key table, regularization')
    add('matrix_smoothing_lines', grab(guide, r'identification lines \(default ([0-9]+)\)', 'smoothing'),
        'docs/control-laws.md on main', 'key table, smoothing_lines')
    add('paired_settle_db', grab(guide, r'within ([0-9.]+) dB, at most ([0-9]+) rounds', 'paired settle'),
        'docs/control-laws.md on main', '`paired` first drive')
    add('paired_settle_rounds', grab(guide, r'within ([0-9.]+) dB, at most ([0-9]+) rounds', 'paired rounds', 2),
        'docs/control-laws.md on main', '`paired` first drive')
    add('secant_first_probe', grab(guide, r"The probe's weight at the start \(default ([0-9.]+)\)", 'probe'),
        'docs/control-laws.md on main', '`secant` key table')
    add('secant_settle_factor', grab(guide, r"delays \(default ([0-9]+)\)", 'settle factor'),
        'docs/control-laws.md on main', '`secant` key table')
    add('ratio_compression', grab(guide, r'larger is gentler \(default ([0-9.]+)\)', 'compression'),
        'docs/control-laws.md on main', '`ratio` key table')
    add('law_file_rounding_matrix', grab(guide, r'modal model within about ([0-9e.-]+),', 'law file rounding'),
        'docs/control-laws.md on main', 'law file against the native law, `matrix`')
    for law, pattern in (
            ('matrix', r'On the testbed\'s linear\s+four-by-four structure it completed (\d+) of (\d+) dwells at the lightest resonance, (\d+) of (\d+) stepped sines\s+\(12 steps an octave, 30 to 120 Hz\) and (\d+) of (\d+) sweeps'),
            ('steepest_descent', r'it completed (\d+) of (\d+) dwells, (\d+) of (\d+) stepped sines and none of (\d+)\s+sweeps')):
        m = re.search(pattern, guide, re.S)
        if not m:
            raise SystemExit(f'not found: testbed line for {law}')
        add(f'testbed_{law}', ' '.join(m.groups()), 'docs/control-laws.md on main', 'the guide\'s testbed counts, in order')

    # The suite's format: parity of the Python laws and the pipeline.
    fmt = open(os.path.join(suite, 'sine', 'FORMAT_SINE.md')).read()
    rule = open(os.path.join(suite, 'sine', 'make_claims.py')).read()
    add('claims_rule_side_in_10', grab(rule, r'at least (\d+) in 10 of the cell', 'side'), 'sine/make_claims.py', 'pairs beyond the threshold on the median\'s side, in 10')
    add('claims_rule_other_in_10', grab(rule, r'at most (\d+) in 10 on the other side', 'other'), 'sine/make_claims.py', 'pairs beyond it on the other side, in 10')
    add('parity_runs', grab(fmt, r'copied from the Hertzforge\s+repository at [0-9a-f]+\): (\d+) runs', 'parity runs'),
        'sine/FORMAT_SINE.md section 13', 'the parity vectors the Python laws are held to')
    add('parity_largest', grab(fmt, r'largest relative difference of drive and controls ([0-9.e-]+)', 'parity largest'),
        'sine/FORMAT_SINE.md section 13', '')
    add('parity_other_law', grab(fmt, r'a different law is shown to fail by more than ([0-9.]+)\)', 'other law'),
        'sine/FORMAT_SINE.md section 13', '')
    for key, pattern, group in (
            ('band_low_hz', r'The band is (\d+) to (\d+) Hz', 1), ('band_high_hz', r'The band is (\d+) to (\d+) Hz', 2),
            ('t1_seconds', r'\| T1 \| Log sweep up, 20 to 2000 Hz, one octave a minute \| ([0-9.]+) s \|', 1),
            ('t2_seconds', r'\| T2 \| Log sweep up, four octaves a minute \| ([0-9.]+) s \|', 1),
            ('t3_steps_per_octave', r'\| T3 \| Stepped sine, (\d+) steps an octave', 1),
            ('t3_steps', r'and 2000 Hz \((\d+) steps\)', 1),
            ('t3_step_time_constants', r'`step_s` = (\d+) time constants', 1),
            ('t4_time_constants', r'Held (\d+) time constants of the dwell mode, at least (\d+) s; the first (\d+) not judged', 1),
            ('t4_least_s', r'Held (\d+) time constants of the dwell mode, at least (\d+) s; the first (\d+) not judged', 2),
            ('t4_not_judged', r'Held (\d+) time constants of the dwell mode, at least (\d+) s; the first (\d+) not judged', 3),
            ('ladder_levels', r'`levels_db` \[([-0-9, ]+)\]', 1),
            ('ladder_rung_s', r'`rung` `\{"seconds": (\d+)\}`', 1),
            ('ceiling_over_ideal_db', r'The ceiling, `drives.ceiling_vpk`, is (\d+) dB over it', 1),
            ('check_point_low_pct', r'\| Check point \(each control\) \| \+/-(\d+) % up to (\d+) Hz, \+/-(\d+) % above', 1),
            ('check_point_corner_hz', r'\| Check point \(each control\) \| \+/-(\d+) % up to (\d+) Hz, \+/-(\d+) % above', 2),
            ('check_point_high_pct', r'\| Check point \(each control\) \| \+/-(\d+) % up to (\d+) Hz, \+/-(\d+) % above', 3),
            ('reference_point_pct', r'the average of the check points\) \| \+/-(\d+) %', 1),
            ('composite_pct', r'minimum of the control channels\) \| \+/-(\d+) %', 1)):
        add(key, grab(fmt, pattern, key, group), 'sine/FORMAT_SINE.md', 'the suite\'s constants')
    add('pipeline_samples', grab(fmt, r'The drive reaches the structure (\d+) samples after it is written', 'pipeline'),
        'sine/FORMAT_SINE.md section 13', '')
    add('engine_frames_ahead', grab(fmt, r"the engine's (\d+) frames ahead", 'frames ahead'),
        'sine/FORMAT_SINE.md section 13', '')
    add('sim_block_frames', grab(fmt, r'one (\d+)-frame block of the simulator station', 'block'),
        'sine/FORMAT_SINE.md section 13', '')
    add('followed_poles_window', grab(fmt, r'`window` (\d+)', 'followed_poles window'), 'sine/FORMAT_SINE.md section 14', 'followed_poles defaults')
    add('followed_poles_near_bw', grab(fmt, r'`near_bw` (\d+)', 'followed_poles near'), 'sine/FORMAT_SINE.md section 14', 'followed_poles defaults')
    add('followed_poles_step_bw', grab(fmt, r'`step_bw` ([0-9.]+)', 'followed_poles step'), 'sine/FORMAT_SINE.md section 14', 'followed_poles defaults')
    add('followed_poles_gate_ratio', grab(fmt, r'`gate_ratio` (\d+)', 'followed_poles gate'), 'sine/FORMAT_SINE.md section 14', 'followed_poles defaults')
    add('carried_g', grab(fmt, r'`g` ([0-9.]+) with the\s+loop-speed rule', 'carried g'), 'sine/FORMAT_SINE.md section 14', 'the carried loop under followed_poles')
    add('m7d_orders', grab(fmt, r'M7d: half-octave pLSCF fit ranges overlapping a quarter octave, orders (\d+ to \d+)', 'orders'),
        'sine/FORMAT_SINE.md section 14', 'M7d')
    add('m7d_cluster_freq_pct', grab(fmt, r'poles clustered over the orders \((\d+) %\s+in frequency', 'cluster f'),
        'sine/FORMAT_SINE.md section 14', 'M7d')
    add('m7d_cluster_damp_pct', grab(fmt, r'in frequency, (\d+) % in damping', 'cluster z'), 'sine/FORMAT_SINE.md section 14', 'M7d')
    add('m7d_mac', grab(fmt, r'participation MAC ([0-9.]+)', 'mac'), 'sine/FORMAT_SINE.md section 14', 'M7d')
    add('block_delay_linear', grab(fmt, r'on the linear tier, (\d+) samples', 'linear delay'), 'sine/FORMAT_SINE.md section 14', '')
    add('block_delay_jointed', grab(fmt, r"`half_taps`, (\d+) on the\s+jointed tiers", 'jointed delay'), 'sine/FORMAT_SINE.md section 14', '')
    add('lag_less_pipeline_a', grab(fmt, r'cross-correlation\'s peak, (\d+) samples on frame-6x6-realistic s00 and (\d+) on frame-12x6 s00', 'lag', 1),
        'sine/FORMAT_SINE.md section 14', '')
    add('lag_less_pipeline_b', grab(fmt, r'cross-correlation\'s peak, (\d+) samples on frame-6x6-realistic s00 and (\d+) on frame-12x6 s00', 'lag', 2),
        'sine/FORMAT_SINE.md section 14', '')

    # The held-back problems: how many, and which structures.
    names = [n for n in os.listdir(heldout) if os.path.isdir(os.path.join(heldout, n))]
    seeds = sorted({int(n.rsplit('_s', 1)[1]) for n in names})
    add('heldout_problems', len(names), 'held-back problem folders', 'folder names only')
    runs, start = [], 0
    for i in range(1, len(seeds) + 1):
        if i == len(seeds) or seeds[i] != seeds[i - 1] + 1:
            part = seeds[start:i]
            runs += [f'{part[0]} to {part[-1]}'] if len(part) > 2 else [str(x) for x in part]
            start = i
    add('heldout_structures', ', '.join(runs[:-1]) + ' and ' + runs[-1], 'held-back problem folders', 'the structure numbers')

    # The runner's protective settings, default and widened.
    run_fmt = open(runner_format).read()
    for key, label in (('alarm', 'Control alarm band'), ('abort', 'Control abort band')):
        m = re.search(r'\| ' + label + r' \| \+/-([0-9.]+) dB \| \+/-([0-9.]+) dB \|', run_fmt)
        add(f'protective_{key}_default_db', m.group(1), 'FORMAT_RUN.md, protective', '')
        add(f'protective_{key}_widened_db', m.group(2), 'FORMAT_RUN.md, protective', '')
    m = re.search(r'before the abort \(`abort_ticks`\) \| (\d+) \| (\d+) \|', run_fmt)
    add('protective_ticks_default', m.group(1), 'FORMAT_RUN.md, protective', '')
    add('protective_ticks_widened', m.group(2), 'FORMAT_RUN.md, protective', '')
    m = re.search(r'before the divergence stop \(`divergence_s`\) \| (\d+) \| (\d+) \|', run_fmt)
    add('protective_divergence_default_s', m.group(1), 'FORMAT_RUN.md, protective', '')
    add('protective_divergence_widened_s', m.group(2), 'FORMAT_RUN.md, protective', '')

    # The agreement between the versions (Packages D and F).
    exp = os.path.join(record, 'experiments')
    f = json.load(open(os.path.join(exp, 'F', 'agreement_f_output.json')))
    d = json.load(open(os.path.join(exp, 'D', 'final_sets_output.json')))
    for arm in ('a', 'b'):
        add(f'agree_{arm}_pairs', f[arm]['pairs'], 'experiments/F/agreement_f_output.json', '')
        add(f'agree_{arm}_outcome', f[arm]['outcome_agrees'], 'experiments/F/agreement_f_output.json', '')
        add(f'agree_{arm}_every', f[arm]['both_agree'], 'experiments/F/agreement_f_output.json', 'outcome and every reading')
        add(f'agree_{arm}_outcome_nopipeline', d[arm]['outcome_agrees'], 'experiments/D/final_sets_output.json', 'before the pipeline was restated')
        add(f'agree_{arm}_every_nopipeline', d[arm]['both_agree'], 'experiments/D/final_sets_output.json', '')
    agree = []
    for arm in ('a', 'b'):
        rows = json.load(open(os.path.join(exp, 'F', f'f_{arm}.json')))
        add(f'agree_{arm}_structures', len({r['problem'] for r in rows}), f'experiments/F/f_{arm}.json', 'structures in the sample')
        for law in LAWS:
            g = [r for r in rows if r['law'] == law]
            agree.append([arm, law, 'all', len(g), sum(r['outcome_agrees'] for r in g),
                          sum(r['outcome_agrees'] and r['readings_agree'] for r in g)])
            for test in ('T1', 'T2', 'T3', 'T4', 'T5'):
                h = [r for r in g if r['test'] == test]
                if h:
                    agree.append([arm, law, test, len(h), sum(r['outcome_agrees'] for r in h),
                                  sum(r['outcome_agrees'] and r['readings_agree'] for r in h)])
        for law in ('paired', 'ratio'):
            h = [r for r in rows if r['law'] == law and r['test'] == 'T3']
            add(f'agree_{arm}_{law}_T3_runs', len(h), f'experiments/F/f_{arm}.json', '')
            add(f'agree_{arm}_{law}_T3_hf_aborted', sum(r['outcome'][0] == 'aborted' for r in h), f'experiments/F/f_{arm}.json', 'the Hertzforge run aborted')
            add(f'agree_{arm}_{law}_T3_py_aborted', sum(r['outcome'][1] == 'aborted' for r in h), f'experiments/F/f_{arm}.json', 'the Python run aborted')
            add(f'agree_{arm}_{law}_T3_both_aborted', sum(r['outcome'] == ['aborted', 'aborted'] for r in h), f'experiments/F/f_{arm}.json', '')
    write_csv('law_agreement.csv', ['arm', 'law', 'test', 'pairs', 'outcome_agrees', 'every_reading_agrees'], agree)

    # The screens (Packages G and J).
    screen = []
    g = json.load(open(os.path.join(exp, 'G', 'screen_report_output.json')))
    add('g_runs', g['states']['card'], 'experiments/G/screen_report_output.json', 'carded runs')
    for key, v in sorted(g['rule'].items()):
        arm, test, tier = key.split('|')
        p = v['paired']
        screen.append(['G', arm_id(arm), test, tier, arm_id(v['yardstick']), v['completed'], v['completed_yard'],
                       v['completions_gained'], v['completions_lost'], v.get('ends'), v.get('ends_yard'),
                       p['p95']['median'], p['p95']['cand_lower'], p['p95']['n'],
                       p['iec_share']['median'], p['iec_share']['cand_higher'],
                       p['over_test']['median'], p['over_test']['cand_higher'], p['over_test']['n'],
                       v['passes'], v['counts_for_rule'], g['post_hoc_completed'].get(key, '')])
    j = json.load(open(os.path.join(exp, 'J', 'screen_report_output.json')))
    add('j_runs', j['states']['card'], 'experiments/J/screen_report_output.json', 'carded runs')
    for key, v in sorted(j['rule'].items()):
        arm, test, tier, yard = key.split('|')
        p = v['paired']
        screen.append(['J', arm_id(arm), test, tier, arm_id(yard), v['completed'], v['completed_yard'],
                       v['completions_gained'], v['completions_lost'], v.get('ends'), v.get('ends_yard'),
                       p['p95']['median'], p['p95']['cand_lower'], p['p95']['n'],
                       p['iec_share']['median'], p['iec_share']['cand_higher'],
                       p['over_test']['median'], p['over_test']['cand_higher'], p['over_test']['n'],
                       v['passes'], v['counts_for_rule'], ''])
    write_csv('screen_cells.csv', ['screen', 'arm', 'test', 'tier', 'yardstick', 'completed',
                                   'completed_yardstick', 'gained', 'lost', 'ends', 'ends_yardstick',
                                   'p95_paired_median_db', 'p95_lower_on', 'p95_n',
                                   'iec_inside_paired_median', 'iec_higher_on',
                                   'over_test_paired_median_db', 'over_test_higher_on', 'over_test_n',
                                   'passes', 'counts_for_rule', 'post_hoc_completion_reading'], screen)
    # Completions and passes per arm on the nonlinear cells, and the controls.
    for name, rep in (('G', g), ('J', j)):
        arms = sorted({k.split('|')[0] for k in rep['cells']})
        for arm in arms:
            cells = [v for k, v in rep['cells'].items() if k.split('|')[0] == arm and k.split('|')[2] != 'linear']
            add(f'{name}_{arm_id(arm)}_completed_nonlinear', sum(c['completed'] for c in cells), f'experiments/{name}/screen_report_output.json', 'cells, realistic and strong')
            add(f'{name}_{arm_id(arm)}_runs_nonlinear', sum(c['runs'] for c in cells), f'experiments/{name}/screen_report_output.json', '')
            lin = [v for k, v in rep['cells'].items() if k.split('|')[0] == arm and k.split('|')[2] == 'linear']
            add(f'{name}_{arm_id(arm)}_completed_linear', sum(c['completed'] for c in lin), f'experiments/{name}/screen_report_output.json', 'the linear control')
            add(f'{name}_{arm_id(arm)}_runs_linear', sum(c['runs'] for c in lin), f'experiments/{name}/screen_report_output.json', '')
            ends = [v.get('ends', 0) for k, v in rep['cells'].items() if k.split('|')[0] == arm and k.split('|')[2] != 'linear' and k.split('|')[1] in ('T1', 'T2', 'T3', 'T5')]
            add(f'{name}_{arm_id(arm)}_ends_nonlinear_sweeps_steps', sum(ends), f'experiments/{name}/screen_report_output.json', 'runs ending in tolerance, sweeps and steps')
    for arm, v in j['verdicts'].items():
        add(f'J_{arm_id(arm)}_cells_vs_matrix', len(v['passes_vs_matrix']), 'experiments/J/screen_report_output.json', 'cells passing the rule against matrix')
        add(f'J_{arm_id(arm)}_cells_vs_followed_poles', len(v['passes_vs_k3']), 'experiments/J/screen_report_output.json', 'cells passing against followed_poles')
    add('G_post_hoc_followed_poles_cells', sum(1 for k, v in g['post_hoc_completed'].items() if k.startswith('k3|') and v),
        'experiments/G/screen_report_output.json', 'post hoc completion reading')
    for key, v in sorted(j['control'].items()):
        arm, test = key.split('|')
        add(f'J_control_{arm_id(arm)}_{test}_p95_vs_followed_poles', v['p95']['median'], 'experiments/J/screen_report_output.json', 'linear control, paired median p95 lead less followed_poles, dB')
    # The matrix's own ends in tolerance on the screen's sweeps and steps (linear control apart).
    for key, v in sorted(g['cells'].items()):
        arm, test, tier = key.split('|')
        if arm == 'matrix':
            add(f'G_matrix_{test}_{tier}_ends', v.get('ends'), 'experiments/G/screen_report_output.json', 'runs ending in tolerance of 6')
    # M9d against M7d on the screen's two structures: the clock.
    runs = list(csv.DictReader(open(os.path.join(exp, 'G', 'screen_runs.csv'))))
    m9 = {(r['problem'], r['test']): float(r['clock_s']) for r in runs if r['arm'] == 'k3_m9d'}
    m7 = {(r['problem'], r['test']): float(r['clock_s']) for r in runs if r['arm'] == 'k3'}
    ratios = sorted(m9[k] / m7[k] for k in m9 if k in m7)
    add('G_m9d_clock_ratio_low', round(ratios[0]), 'experiments/G/screen_runs.csv', 'followed_poles on M9d, clock over followed_poles on M7d')
    add('G_m9d_clock_ratio_high', round(ratios[-1]), 'experiments/G/screen_runs.csv', '')
    add('G_m9d_structures', len(ratios), 'experiments/G/screen_runs.csv', '')

    # The record's words that hold a number the files above do not.
    dnw = open(os.path.join(record, 'Did_Not_Work.md')).read()
    add('preview_t1_start_error_db', grab(dnw, r'the error at the sweep\'s start \(([0-9.]+) dB in 30 to 50 Hz', 'preview start'),
        'Did_Not_Work.md, the preview row', '')
    add('preview_t1_start_band', grab(dnw, r'dB in (30 to 50) Hz on frame-6x6 s00', 'preview band'), 'Did_Not_Work.md, the preview row', '')
    add('preview_t1_start_followed_poles_db', grab(dnw, r'30 to 50 Hz on frame-6x6 s00, K3 ([0-9.]+) dB', 'preview, followed_poles'), 'Did_Not_Work.md, the preview row', '')
    add('g1_lag_fit_error', grab(dnw, r'in-band error was ([0-9.]+) and ([0-9.]+), worse than taking no delay out \(([0-9.]+), ([0-9.]+)\); with the block\'s delay ([0-9.]+) and ([0-9.]+)', 'fit errors', 0),
        'Did_Not_Work.md, the block delay row', 'the whole phrase')
    # The two screens' pass rules, as written before their runs.
    gs = open(os.path.join(record, 'G_Screen.md')).read()
    add('g_rule_over_db', grab(gs, r"not worse than `matrix`'s by more than (\d+) dB in the median over those cases", 'g rule'),
        'G_Screen.md section 3', 'the lead\'s pass rule')
    add('screen_cell_structures', grab(gs, r'its cases are the (\d+) structures of that tier', 'cell structures'),
        'G_Screen.md section 3', 'structures a cell')
    add('screen_structure_numbers', grab(gs, r'\*\*Structures\.\*\* Seeds ([0-9, ]+) of frame-6x6 and frame-12x6', 'screen seeds'),
        'G_Screen.md section 2', 'the screen\'s structures')
    add('screen_structures_nonlinear', grab(gs, r'realistic and strong: (\d+) structures, the study\'s own', 'screen n'), 'G_Screen.md section 2', '')
    add('screen_structures_all', grab(gs, r'(\d+) structures in all', 'screen all'), 'G_Screen.md section 2', '')
    js = open(os.path.join(record, 'J_Screen.md')).read()
    add('j_rule_cells', grab(js, r'on at least (two) nonlinear cells', 'j cells'), 'J_Screen.md section 2', 'the lead\'s rule, verbatim')
    add('j_rule_p95_of', grab(js, r'on at least (\d+) of the (\d+) structures', 'j p95'), 'J_Screen.md section 2', '')
    add('j_rule_p95_structures', grab(js, r'on at least (\d+) of the (\d+) structures', 'j p95 n', 2), 'J_Screen.md section 2', '')
    add('j_rule_over_db', grab(js, r"not worse than\s*> `matrix`'s by more than (\d+) dB", 'j over'), 'J_Screen.md section 2', '')
    add('family_inverse_expected_drop', grab(fmt, r'`expected_drop` ([0-9.]+) \(a drop', 'family_inverse drop'), 'sine/FORMAT_SINE.md section 14', 'family_inverse default')
    add('rls_dither_dither', grab(fmt, r'`dither` ([0-9.]+) on the response', 'rls_dither dither'), 'sine/FORMAT_SINE.md section 14', 'rls_dither default')
    add('rls_dither_lam', grab(fmt, r'`lam` ([0-9.]+)', 'rls_dither lam'), 'sine/FORMAT_SINE.md section 14', 'rls_dither default')
    decisions = os.environ.get('DECISIONS') or os.path.join(record, '..', '..', 'DECISIONS.md')
    dec = open(decisions).read()
    add('followed_poles_rust_lines', grab(dec, r'Its Rust build \(about ([0-9,]+ to [0-9,]+) lines', 'rust lines'), 'DECISIONS.md, 2026-11-25, the row admitting followed_poles', '')
    # Kevin's words name the law by its effort code; the article quotes them with its name in brackets.
    add('followed_poles_quote', grab(dec, r'Kevin: "(Include) K3"', 'quote') + ' [followed poles]',
        'DECISIONS.md, 2026-11-25', "Kevin's words, the law's name in brackets for its code")
    add('leads_quote', grab(dec, r'Kevin: "(Don\'t add any of the four)"', 'quote'), 'DECISIONS.md, 2026-11-25', '')
    write_csv('facts.csv', ['key', 'value', 'source', 'how_read'], facts)


if __name__ == '__main__':
    if len(sys.argv) != 7:
        sys.exit(__doc__)
    main(*sys.argv[1:])
