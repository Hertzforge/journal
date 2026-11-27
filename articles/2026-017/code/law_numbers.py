"""Write ../data/law_numbers.csv: the percentages, ranges and counts the article's text quotes,
each computed from the other files of ../data and named by the file it came from. Standard library
only. Copyright 2026 Kevin Cross. MIT license.

    python law_numbers.py
"""
import collections
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')


def rows(name):
    with open(os.path.join(DATA, name), newline='') as file:
        return list(csv.DictReader(file))


def pct(a, b):
    return f'{100 * a / b:.0f}' if b else ''


def main():
    out = []

    def add(key, value, source):
        out.append([key, value, source])

    # Completions and readings by job, all tiers and each tier.
    for r in rows('law_readings.csv'):
        k = f"{r['version']}_{r['law']}_{r['test']}_{r['tier']}"
        n = int(r['runs'])
        add(f'{k}_runs', n, 'law_readings.csv')
        add(f'{k}_completed', r['completed'], 'law_readings.csv')
        add(f'{k}_completed_pct', pct(int(r['completed']), n), 'law_readings.csv')
        add(f'{k}_iec_median_pct', f"{100 * float(r['iec_share_median']):.0f}", 'law_readings.csv')
        add(f'{k}_worst_median_db', f"{float(r['worst_over_db_median']):.1f}" if r['worst_over_db_median'] else '', 'law_readings.csv')
        add(f'{k}_inside_cp', r['inside_check_point'], 'law_readings.csv')
        add(f'{k}_inside_cp_pct', pct(int(r['inside_check_point']), n), 'law_readings.csv')
    # Safety.
    for r in rows('law_safety.csv'):
        k = f"{r['version']}_{r['law']}_{r['test']}"
        n, w = int(r['runs']), int(r['with_reading'])
        for t in ('3db', '6db', '12db'):
            add(f'{k}_over_{t}', r[f'over_{t}'], 'law_safety.csv')
            add(f'{k}_over_{t}_pct_of_runs', pct(int(r[f'over_{t}']), n), 'law_safety.csv')
            add(f'{k}_over_{t}_pct_of_scored', pct(int(r[f'over_{t}']), w), 'law_safety.csv')
        add(f'{k}_with_reading', w, 'law_safety.csv')
        add(f'{k}_largest_db', f"{float(r['largest_db']):.1f}", 'law_safety.csv')
    # Pooled safety over every sweep and step, and over every dwell, by version.
    pool = collections.defaultdict(lambda: [0, 0, 0])
    for r in rows('law_safety.csv'):
        kind = 'dwell' if r['test'] == 'T4' else 'sweep_step'
        for key in (f"{r['version']}_{kind}", f"{r['version']}_{r['law']}_{kind}"):
            pool[key][0] += int(r['runs'])
            pool[key][1] += int(r['with_reading'])
            pool[key][2] += int(r['over_6db'])
    for key, (n, w, o) in pool.items():
        add(f'{key}_runs', n, 'law_safety.csv')
        add(f'{key}_over_6db', o, 'law_safety.csv')
        add(f'{key}_over_6db_pct_of_runs', pct(o, n), 'law_safety.csv')
        add(f'{key}_over_6db_pct_of_scored', pct(o, w), 'law_safety.csv')
    # Level claims by shape, and the ranges of the cells' median worst excursions.
    for r in rows('law_level_by_shape.csv'):
        k = f"{r['version']}_{r['law']}_{r['test']}_{r['line']}_{r['shape']}"
        add(f'{k}_inside', r['cells_inside'], 'law_level_by_shape.csv')
        add(f'{k}_cells', r['cells'], 'law_level_by_shape.csv')
        add(f'{k}_first_inside', (r['ids_inside'].split() or [''])[0], 'law_level_by_shape.csv')
        add(f'{k}_first_outside', (r['ids_outside'].split() or [''])[0], 'law_level_by_shape.csv')
    span = collections.defaultdict(list)
    unscored = collections.Counter()
    for r in rows('law_level_claims.csv'):
        k = f"{r['version']}_{r['law']}_{r['test']}_{r['line']}_{r['side']}"
        if r['median_worst_excursion_db'] == '':
            unscored[k] += 1
        else:
            span[k].append(float(r['median_worst_excursion_db']))
    for k, v in span.items():
        add(f'{k}_cells_scored', len(v), 'law_level_claims.csv')
        add(f'{k}_low_db', f'{min(v):.1f}', 'law_level_claims.csv')
        add(f'{k}_high_db', f'{max(v):.1f}', 'law_level_claims.csv')
    for k, n in unscored.items():
        add(f'{k}_cells_median_unscored', n, 'law_level_claims.csv')
    # The default protective settings and the repeats.
    for r in rows('law_defaults_summary.csv'):
        n = int(r['runs'])
        add(f"defaults_{r['set']}_runs", n, 'law_defaults_summary.csv')
        add(f"defaults_{r['set']}_completed", r['completed'], 'law_defaults_summary.csv')
        add(f"defaults_{r['set']}_record_completed", r['record_completed'], 'law_defaults_summary.csv')
        add(f"defaults_{r['set']}_stopped", r['stopped_by_protective_default'], 'law_defaults_summary.csv')
    for r in rows('law_repeats_summary.csv'):
        for key, value in r.items():
            if key != 'version':
                add(f"repeats_{r['version']}_{key}", value, 'law_repeats_summary.csv')
    # Agreement, as percentages.
    for r in rows('law_agreement.csv'):
        if r['test'] == 'all':
            n = int(r['pairs'])
            add(f"agree_{r['arm']}_{r['law']}_pairs", n, 'law_agreement.csv')
            add(f"agree_{r['arm']}_{r['law']}_outcome", r['outcome_agrees'], 'law_agreement.csv')
            add(f"agree_{r['arm']}_{r['law']}_every", r['every_reading_agrees'], 'law_agreement.csv')
        else:
            add(f"agree_{r['arm']}_{r['law']}_{r['test']}_outcome_differs",
                int(r['pairs']) - int(r['outcome_agrees']), 'law_agreement.csv')
    # The pair counts, by key.
    for r in rows('law_pair_counts.csv'):
        k = f"{r['version']}_{r['test']}_{r['law']}_{r['against']}_{r['reading']}"
        add(f'{k}_cells', r['cells'], 'law_pair_counts.csv')
        add(f'{k}_favour_law', r['cells_favour_law'], 'law_pair_counts.csv')
        add(f'{k}_favour_against', r['cells_favour_against'], 'law_pair_counts.csv')
        add(f'{k}_first_id', (r['ids_favour_law'].split() + r['ids_favour_against'].split() + [''])[0],
            'law_pair_counts.csv')
        add(f'{k}_first_id_law', (r['ids_favour_law'].split() or [''])[0], 'law_pair_counts.csv')
        add(f'{k}_first_id_against', (r['ids_favour_against'].split() or [''])[0], 'law_pair_counts.csv')
    # The stepped sine's ends.
    for r in rows('law_steps.csv'):
        k = f"steps_{r['law']}_{r['tier']}"
        for key in ('runs', 'completed', 'aborted', 'aborted_at_m12db', 'aborted_at_0db', 'held', 'law_fault'):
            add(f'{k}_{key}', r[key], 'law_steps.csv')
        add(f'{k}_aborted_at_m12db_pct', pct(int(r['aborted_at_m12db']), int(r['runs'])), 'law_steps.csv')
        add(f'{k}_aborted_at_0db_pct', pct(int(r['aborted_at_0db']), int(r['runs'])), 'law_steps.csv')
    # followed_poles cells: the ranges of the cell medians where a claim favours it.
    fp = collections.defaultdict(list)
    for r in rows('law_followed_poles_cells.csv'):
        if r['claim_favours'] == 'followed_poles':
            fp[(r['test'], r['reading'])].append(float(r['median_followed_poles_less_matrix']))
    for (test, reading), v in fp.items():
        scale = 100 if reading != 'worst_over_db' else 1
        add(f'followed_poles_{test}_{reading}_favoured_low', f'{min(v) * scale:.1f}', 'law_followed_poles_cells.csv')
        add(f'followed_poles_{test}_{reading}_favoured_high', f'{max(v) * scale:.1f}', 'law_followed_poles_cells.csv')
    for reading in ('completion', 'iec_share', 'worst_over_db'):
        v = [float(r['median_followed_poles_less_matrix']) for r in rows('law_followed_poles_cells.csv')
             if r['reading'] == reading and r['median_followed_poles_less_matrix'] != '']
        scale = 100 if reading != 'worst_over_db' else 1
        add(f'followed_poles_cells_{reading}_low', f'{min(v) * scale:.1f}', 'law_followed_poles_cells.csv')
        add(f'followed_poles_cells_{reading}_high', f'{max(v) * scale:.1f}', 'law_followed_poles_cells.csv')
    tiers = collections.Counter(r['tier'] for r in rows('law_followed_poles_cells.csv') if r['claim_favours'] == 'followed_poles')
    add('followed_poles_favoured_claims_all', sum(tiers.values()), 'law_followed_poles_cells.csv')
    for tier, n in tiers.items():
        add(f'followed_poles_favoured_claims_{tier}', n, 'law_followed_poles_cells.csv')
    for r in rows('law_followed_poles_cells.csv'):
        if r['claim_favours'] == 'matrix':
            k = f"followed_poles_matrix_favoured_{r['test']}_{r['reading']}"
            add(f'{k}_id', r['claim'], 'law_followed_poles_cells.csv')
            add(f'{k}_cell', f"{r['system']} {r['kind'].replace('_', ' ')}", 'law_followed_poles_cells.csv')
            add(f'{k}_followed_poles_less_matrix_db', f"{float(r['median_followed_poles_less_matrix']):.1f}", 'law_followed_poles_cells.csv')
    # The screens: each arm against its yardstick, summed over the nonlinear cells (realistic and
    # strong) and over the linear control; the over-test medians' range; and the J rule (more
    # completions, p95 lower on at least 4 of 6, over-test median at most +1 dB) read on every arm.
    facts = {r['key']: r['value'] for r in rows('facts.csv')}
    p95_of, over_db = int(facts['j_rule_p95_of']), float(facts['j_rule_over_db'])
    groups = collections.defaultdict(list)
    for r in rows('screen_cells.csv'):
        part = 'linear' if r['tier'] == 'linear' else 'nonlinear'
        groups[(r['screen'], r['arm'], r['yardstick'], part)].append(r)
        if r['tier'] != part:
            groups[(r['screen'], r['arm'], r['yardstick'], r['tier'])].append(r)
    for (screen, arm, yard, part), cells in groups.items():
        k = f'screen_{screen}_{arm}_vs_{yard}_{part}'
        for key in ('completed', 'completed_yardstick', 'gained', 'lost', 'ends', 'ends_yardstick',
                    'p95_lower_on', 'p95_n', 'iec_higher_on', 'over_test_higher_on', 'over_test_n'):
            add(f'{k}_{key}', sum(int(c[key] or 0) for c in cells), 'screen_cells.csv')
        add(f'{k}_runs', len(cells) * int(facts['screen_cell_structures']), 'screen_cells.csv')
        over = [float(c['over_test_paired_median_db']) for c in cells if int(c['over_test_n'] or 0)]
        p95 = [float(c['p95_paired_median_db']) for c in cells if int(c['p95_n'] or 0)]
        if over:
            add(f'{k}_over_low_db', f'{min(over):+.1f}', 'screen_cells.csv')
            add(f'{k}_over_high_db', f'{max(over):+.1f}', 'screen_cells.csv')
        if p95:
            add(f'{k}_p95_low_db', f'{min(p95):+.1f}', 'screen_cells.csv')
            add(f'{k}_p95_high_db', f'{max(p95):+.1f}', 'screen_cells.csv')
        if part == 'nonlinear':
            rule = [c for c in cells if c['test'] in ('T1', 'T2', 'T5')
                    and int(c['completed']) > int(c['completed_yardstick'])
                    and int(c['p95_lower_on']) >= p95_of
                    and int(c['over_test_n'] or 0) and float(c['over_test_paired_median_db']) <= over_db]
            add(f'{k}_j_rule_cells', len(rule), 'screen_cells.csv')
    for r in rows('screen_cells.csv'):
        k = f"screen_{r['screen']}_{r['arm']}_vs_{r['yardstick']}_{r['test']}_{r['tier']}"
        for key in ('completed', 'completed_yardstick', 'ends', 'ends_yardstick', 'p95_lower_on', 'p95_n'):
            add(f'{k}_{key}', r[key], 'screen_cells.csv')
        add(f'{k}_over_db', f"{float(r['over_test_paired_median_db']):+.2f}" if r['over_test_paired_median_db'] else '', 'screen_cells.csv')
        add(f'{k}_p95_db', f"{float(r['p95_paired_median_db']):+.2f}" if r['p95_paired_median_db'] else '', 'screen_cells.csv')
    # Level claims by job and line, and summed over the sweeps and steps.
    total = collections.defaultdict(lambda: [0, 0])
    for r in rows('law_level_counts.csv'):
        k = f"level_{r['version']}_{r['law']}_{r['test']}_{r['line']}"
        add(f'{k}_inside', r['cells_inside'], 'law_level_counts.csv')
        add(f'{k}_cells', r['cells'], 'law_level_counts.csv')
        add(f'{k}_first_inside', (r['ids_inside'].split() or [''])[0], 'law_level_counts.csv')
        if r['test'] != 'T4':
            for key in (f"{r['version']}_{r['line']}", f"all_{r['line']}"):
                total[key][0] += int(r['cells_inside'])
                total[key][1] += int(r['cells'])
    for key, (inside, cells) in total.items():
        add(f'level_sweeps_steps_{key}_inside', inside, 'law_level_counts.csv')
        add(f'level_sweeps_steps_{key}_cells', cells, 'law_level_counts.csv')
    # The sizes of the defaults and the repeats sets.
    d = rows('law_defaults.csv')
    add('defaults_structures', len({r['structure'] for r in d}), 'law_defaults.csv')
    add('defaults_jobs_each', max(collections.Counter((r['set'], r['job']) for r in d).values()), 'law_defaults.csv')
    rp = rows('law_repeats.csv')
    add('repeats_structures', len({r['structure'] for r in rp}), 'law_repeats.csv')
    add('repeats_sets_each', len({r['set'] for r in rp if r['set'].startswith('hertzforge')}), 'law_repeats.csv')
    # The guide's testbed counts, one number a key (facts.csv holds them as one string).
    for law in ('matrix', 'steepest_descent'):
        for i, v in enumerate(facts[f'testbed_{law}'].split(), 1):
            add(f'testbed_{law}_{i}', v, 'facts.csv')
    path = os.path.join(DATA, 'law_numbers.csv')
    with open(path, 'w', newline='') as file:
        w = csv.writer(file, lineterminator='\n')
        w.writerow(['key', 'value', 'source'])
        w.writerows(out)
    print('wrote law_numbers.csv', len(out), 'rows')


if __name__ == '__main__':
    main()
