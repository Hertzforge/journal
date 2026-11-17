"""What softening and hardening each do (Section 8): the single-effect runs of the law study, pooled over its laws.

    python effects.py [CARDS_FOLDER [AUDIT_CARDS_FOLDER ...]]

Given CARDS_FOLDER (the scorecards of batch main of the MIMO Random law study), the script reads, for structures 0
to 9, the setups with 6 shakers and 12 control gauges and with 6 and 6, the six laws at their default settings with
the measured frequency response kept, every variant: linear (`none`), softening only (`<tier>_soft`), hardening only
(`<tier>_hard`) and both (`<tier>`), and writes one row per run to ../data/effects_runs.csv. With no argument it reads
that file, so the article can be refreshed after the study's files are gone. The run used for a case is the completed
run with the checks widened where it exists, otherwise the completed run with the checks at their defaults (where both
completed they are identical).

The audit's folders, when given, are read the same way for its ten held-back structures (20 to 23, 26 to 28, 50 to
52; 24 was refused by the simulator and is left out) into ../data/effects_runs_audit.csv, and every key is written a
second time with the prefix `audit.`.

Writes:
  ../data/effects_runs.csv       one row per run (the scorecard values this section uses)
  ../data/effects_by_line.csv    change against the same law on the linear structure, per tier, setup, effect and line
  ../data/effects_summary.csv    every number the text quotes, under its key (fill_article.py reads it as eff.*)

Pooled over the laws on purpose: the article names no law. Needs the standard library only.
Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
RUNS = os.path.join(DATA, 'effects_runs.csv')
RUNS_AUDIT = os.path.join(DATA, 'effects_runs_audit.csv')
STUDY_SEEDS = list(range(10))
AUDIT_SEEDS = [20, 21, 22, 23, 26, 27, 28, 50, 51, 52]
LAWS = ['pinv_closed', 'pinv_open', 'shape_svd', 'buzz_match', 'min_drive', 'band_average']
SETUPS = ['6x12', '6x6']
TIERS = ['realistic', 'strong']
EFFECTS = [('soft', '_soft'), ('hard', '_hard'), ('both', '')]
LINES = [('control', 'control_db'), ('heldout', 'heldout_db'), ('stress', 'stress_db')]
FIELDS = ['structure', 'setup', 'variant', 'law', 'card', 'control_db', 'heldout_db', 'stress_db',
          'member_service_pct', 'member_tested_pct', 'soft_modes_tested', 'soft_tested_p50_pct',
          'soft_tested_p90_pct', 'soft_tested_p10_pct', 'soft_modes_service', 'soft_service_p50_pct',
          'other_modes_abs_p90_pct']


def card(folders, seed, rig, variant, law):
    ref = 'banded' if law == 'band_average' else 'line'
    base = f's{seed}_{rig}_{variant}_{law}_default_{ref}_hold'
    for name in (base + '_divopen.json', base + '.json'):
        for folder in folders:
            p = os.path.join(folder, name)
            if os.path.exists(p):
                d = json.load(open(p))
                if d.get('outcome', {}).get('completed') and d.get('scored'):
                    return name, d
    return None, None


def extract(folders, seeds, path):
    rows = []
    for seed in seeds:
        for rig in SETUPS:
            for variant in ['none'] + [t + s for t in TIERS for _, s in EFFECTS]:
                for law in LAWS:
                    name, d = card(folders, seed, rig, variant, law)
                    if d is None:
                        continue
                    r = dict(structure=seed, setup=rig, variant=variant, law=law, card=name,
                             control_db=d['card']['c_b3_rms'], heldout_db=d['card']['h_b3_rms'], stress_db=d['stress']['rms'])
                    ps = d.get('structure_state') or {}             # the scorer's field name; "state as tested" in the text
                    sl = ps.get('service_line') or {}
                    m, s = sl.get('member') or {}, sl.get('softening') or {}
                    r['member_service_pct'] = m.get('change_pct_service', '')
                    r['member_tested_pct'] = m.get('change_pct_played', '')
                    r['soft_modes_tested'] = s.get('modes_played', '')
                    r['soft_modes_service'] = s.get('modes_service', '')
                    p = s.get('change_pct_played_p10_p50_p90') or ['', '', '']
                    r['soft_tested_p10_pct'], r['soft_tested_p50_pct'], r['soft_tested_p90_pct'] = p
                    q = s.get('change_pct_service_p10_p50_p90') or ['', '', '']
                    r['soft_service_p50_pct'] = q[1]
                    modes = (ps.get('signed') or {}).get('modes') or []
                    other = sorted(abs(100 * x['change']) for x in modes if x.get('mode') != m.get('mode'))
                    r['other_modes_abs_p90_pct'] = other[int(0.9 * (len(other) - 1))] if other and variant.endswith('_hard') else ''
                    rows.append(r)
    with open(path, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def q(x):                                             # median and quartiles, as the study's first look takes them
    x = sorted(x)
    n = len(x)
    return st.median(x), x[int(0.25 * (n - 1))], x[int(round(0.75 * (n - 1)))]


def f(v):
    return float(v) if v not in ('', None) else None


def compute(rows):
    seeds = sorted({int(r['structure']) for r in rows})
    get = {(int(r['structure']), r['setup'], r['variant'], r['law']): r for r in rows}
    out, table = {}, []
    out['runs_single_effect'] = sum(1 for r in rows if r['variant'].endswith(('_soft', '_hard')))
    out['structures'] = len({r['structure'] for r in rows})
    out['laws'] = len({r['law'] for r in rows})
    for tier in TIERS:
        for rig in SETUPS:
            for eff, suf in EFFECTS:
                for line, col in LINES:
                    d = []
                    for seed in seeds:
                        for law in LAWS:
                            a, b = get.get((seed, rig, 'none', law)), get.get((seed, rig, tier + suf, law))
                            if a and b:
                                d.append(float(b[col]) - float(a[col]))
                    m, lo, hi = q(d)
                    ab = [abs(x) for x in d]
                    rec = dict(tier=tier, setup=rig, effect=eff, line=line, median_db=m, q1_db=lo, q3_db=hi,
                               abs_median_db=st.median(ab), abs_q1_db=q(ab)[1], abs_q3_db=q(ab)[2], n=len(d),
                               n_abs_over_1=sum(x > 1 for x in ab), n_up=sum(x > 0 for x in d), n_down=sum(x < 0 for x in d))
                    table.append(rec)
                    k = f'{tier}.{rig}.{eff}.{line}'
                    for kk in ('median_db', 'q1_db', 'q3_db', 'abs_median_db', 'n', 'n_abs_over_1', 'n_up', 'n_down'):
                        out[f'{k}.{kk}'] = rec[kk]
            # stress moves most: for each effect, is the stress line's median absolute change the largest of the three?
            for eff, _ in EFFECTS:
                a = {line: out[f'{tier}.{rig}.{eff}.{line}.abs_median_db'] for line, _ in LINES}
                out[f'{tier}.{rig}.{eff}.stress_largest'] = a['stress'] == max(a.values())
            # hardening against softening, stress line, median absolute change
            out[f'{tier}.{rig}.hard_over_soft_stress'] = (out[f'{tier}.{rig}.hard.stress.abs_median_db']
                                                          / out[f'{tier}.{rig}.soft.stress.abs_median_db'])
            # what each effect does to the structure
            hard = [r for r in rows if r['setup'] == rig and r['variant'] == tier + '_hard']
            soft = [r for r in rows if r['setup'] == rig and r['variant'] == tier + '_soft']
            both = [r for r in rows if r['setup'] == rig and r['variant'] == tier]
            svc = {}
            for r in hard:
                svc[int(r['structure'])] = f(r['member_service_pct'])
            tested_by_s = {}
            for r in hard:
                if f(r['member_tested_pct']) is not None:
                    tested_by_s.setdefault(int(r['structure']), []).append(f(r['member_tested_pct']))
            tmed = [st.median(v) for v in tested_by_s.values()]
            sv = list(svc.values())
            k = f'{tier}.{rig}'
            out[f'{k}.member_service_median'], out[f'{k}.member_service_min'], out[f'{k}.member_service_max'] = st.median(sv), min(sv), max(sv)
            out[f'{k}.member_tested_median'], out[f'{k}.member_tested_min'], out[f'{k}.member_tested_max'] = st.median(tmed), min(tmed), max(tmed)
            bt = [f(r['member_tested_pct']) for r in both if f(r['member_tested_pct']) is not None]
            out[f'{k}.member_tested_both_median'] = st.median(bt)
            oth = [f(r['other_modes_abs_p90_pct']) for r in hard if f(r['other_modes_abs_p90_pct']) is not None]
            out[f'{k}.hard_other_modes_abs_p90_max'] = max(oth)
            out[f'{k}.soft_modes_tested_median'] = st.median([f(r['soft_modes_tested']) for r in soft])
            out[f'{k}.soft_modes_service_median'] = st.median([f(r['soft_modes_service']) for r in soft])
            out[f'{k}.soft_tested_p50_median'] = st.median([f(r['soft_tested_p50_pct']) for r in soft])
            out[f'{k}.soft_tested_p90_median'] = st.median([f(r['soft_tested_p90_pct']) for r in soft])
            out[f'{k}.soft_tested_p10_median'] = st.median([f(r['soft_tested_p10_pct']) for r in soft])
            out[f'{k}.soft_service_p50_median'] = st.median([f(r['soft_service_p50_pct']) for r in soft])
            # the structure whose member changes most in service: its hardening-only stress change, every law
            top = max(svc, key=lambda s: svc[s])
            dd = []
            for law in LAWS:
                a, b = get.get((top, rig, 'none', law)), get.get((top, rig, tier + '_hard', law))
                if a and b:
                    dd.append(float(b['stress_db']) - float(a['stress_db']))
            out[f'{k}.top_structure'] = top
            out[f'{k}.top_service'] = svc[top]
            out[f'{k}.top_stress_min'], out[f'{k}.top_stress_max'], out[f'{k}.top_laws'] = min(dd), max(dd), len(dd)
            out[f'{k}.top_all_up'] = all(x > 0 for x in dd)
            # how many structures have every law's stress change of one sign, hardening only
            same = 0
            for seed in seeds:
                d = [float(get[(seed, rig, tier + '_hard', l)]['stress_db']) - float(get[(seed, rig, 'none', l)]['stress_db'])
                     for l in LAWS if (seed, rig, tier + '_hard', l) in get and (seed, rig, 'none', l) in get]
                same += bool(d) and (all(x > 0 for x in d) or all(x < 0 for x in d))
            out[f'{k}.hard_structures_one_sign'] = same
            # law by law (never printed by name): each law's median over structures of the hardening-only stress change
            lm = []
            for l in LAWS:
                d = [float(get[(sd, rig, tier + '_hard', l)]['stress_db']) - float(get[(sd, rig, 'none', l)]['stress_db'])
                     for sd in seeds if (sd, rig, tier + '_hard', l) in get and (sd, rig, 'none', l) in get]
                lm.append(st.median(d))
                out[f'{k}.law{LAWS.index(l)}.hard_stress_median'] = st.median(d)
            out[f'{k}.law_hard_median_abs_max'] = max(abs(x) for x in lm)
    ratios = [out[f'{t}.{r}.hard_over_soft_stress'] for t in TIERS for r in SETUPS]
    out['hard_over_soft_stress_min'], out['hard_over_soft_stress_max'] = min(ratios), max(ratios)
    out['stress_largest_all'] = all(out[f'{t}.{r}.{e}.stress_largest'] for t in TIERS for r in SETUPS for e, _ in EFFECTS)
    return out, table


def main():
    if len(sys.argv) > 1:
        extract([sys.argv[1]], STUDY_SEEDS, RUNS)
    if len(sys.argv) > 2:
        extract(sys.argv[2:], AUDIT_SEEDS, RUNS_AUDIT)
    out, table = compute(list(csv.DictReader(open(RUNS))))
    for r in table:
        r['structures'] = 'study'
    if os.path.exists(RUNS_AUDIT):
        oa, ta = compute(list(csv.DictReader(open(RUNS_AUDIT))))
        for r in ta:
            r['structures'] = 'held-back'
        table += ta
        out.update({f'audit.{k}': v for k, v in oa.items()})
        # the two sets side by side, stress line: does the softening-only change keep its sign at the median?
        for t in TIERS:
            for rig in SETUPS:
                for e, _ in EFFECTS:
                    a, b = out[f'{t}.{rig}.{e}.stress.median_db'], out[f'audit.{t}.{rig}.{e}.stress.median_db']
                    out[f'both_sets.{t}.{rig}.{e}.stress.same_sign'] = (a > 0) == (b > 0)
        for t in TIERS:
            for rig in SETUPS:
                out[f'both_sets.{t}.{rig}.law_hard_sign_agree'] = sum(
                    (out[f'{t}.{rig}.law{i}.hard_stress_median'] > 0) == (out[f'audit.{t}.{rig}.law{i}.hard_stress_median'] > 0)
                    for i in range(len(LAWS)))
        out['law_hard_median_abs_max_12'] = max(out[f'{p}{t}.6x12.law_hard_median_abs_max'] for p in ('', 'audit.') for t in TIERS)
        out['audit.law_hard_median_abs_max_6x6_strong'] = out['audit.strong.6x6.law_hard_median_abs_max']
        hs = [abs(out[f'audit.{t}.{r}.hard.stress.median_db']) for t in TIERS for r in SETUPS]
        out['hard_stress_signed_median_abs_max'] = max(abs(out[f'{t}.{r}.hard.stress.median_db']) for t in TIERS for r in SETUPS)
        out['audit.hard_stress_signed_median_abs_max'] = max(hs)
        out['audit.stress_largest_count'] = sum(bool(out[f'audit.{t}.{r}.{e}.stress_largest'])
                                                for t in TIERS for r in SETUPS for e, _ in EFFECTS)
        out['stress_largest_both_sets'] = None  # filled below
        out['stress_largest_count'] = sum(bool(out[f'{t}.{r}.{e}.stress_largest'])
                                          for t in TIERS for r in SETUPS for e, _ in EFFECTS)
    if 'audit.stress_largest_count' in out:
        out['stress_largest_both_sets'] = out['stress_largest_count'] + out['audit.stress_largest_count']
    else:
        out.pop('stress_largest_both_sets', None)
    with open(os.path.join(DATA, 'effects_by_line.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(table[0]))
        w.writeheader()
        w.writerows(table)
    with open(os.path.join(DATA, 'effects_summary.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['key', 'value'])
        for k, v in out.items():
            w.writerow([k, v])
    print(f'effects: {len(out)} values')


if __name__ == '__main__':
    main()
