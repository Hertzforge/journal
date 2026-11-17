"""The independent audit's numbers for claims S1 to S5, the counts of the default checks, and S3 and S4.

    PYTHONDONTWRITEBYTECODE=1 python audit_numbers.py VERDICTS_JSON > ../data/audit_numbers.txt

Reads the audit's verdicts.json (written by the audit's own code and kept with the audit's run records) and copies what this article quotes into
../data/audit_verdicts.csv. Each row is one comparison: the study's median and quartiles over its 20 (or 10)
structures, the audit's over its ten held-back structures, the audit's verdict by its fixed rule, and the count
of held-back structures that agree in sign. Nothing is recomputed here. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
if len(sys.argv) != 2:
    sys.exit('usage: audit_numbers.py VERDICTS_JSON')
SRC = sys.argv[1]
d = json.load(open(SRC))

rows = [r for r in d['numeric'] if str(r['claim']).startswith('S')]
with open(os.path.join(DATA, 'audit_verdicts.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['claim', 'what', 'study_n', 'study_median', 'study_q1', 'study_q3', 'audit_n', 'audit_median', 'audit_q1',
                'audit_q3', 'verdict', 'audit_structures_same_sign'])
    for r in rows:
        s, a = r['study'], r['audit']
        w.writerow([r['claim'], r['what'], s['n'], f"{s['median']:.4f}", f"{s['q1']:.4f}", f"{s['q3']:.4f}", a['n'],
                    f"{a['median']:.4f}", f"{a['q1']:.4f}", f"{a['q3']:.4f}", r['verdict'], r['audit_structures_same_sign']])
        print(f"{r['claim']:3s} {r['what']:60s} study {s['median']:+.2f} [{s['q1']:+.2f}, {s['q3']:+.2f}] | audit "
              f"{a['median']:+.2f} [{a['q1']:+.2f}, {a['q3']:+.2f}] | {r['verdict']} | same sign {r['audit_structures_same_sign']} of {a['n']}")

print('\nS3 and S4 (square = as many shakers as control gauges)')
for who in ('study', 'audit'):
    for cls, v in d['s3_s4'][who].items():
        print(f"  {who:5s} {cls:10s} n {v['n']}: rho control {v['rho_ctrl']:+.2f} held-out {v['rho_held']:+.2f}; summed control "
              f"{v['rho_csum']:+.2f} held-out {v['rho_hsum']:+.2f}; exact-fit flag {v['exact_fit_flag']}; control A or B "
              f"{v['ctrl_A_or_B']}; held-out A or B {v['held_A_or_B']}; stress within 3 dB {v['stress_within_3']}; alarm {v['alarm']}")

print('\nDefault checks')
for who in ('study', 'audit'):
    c = d['counts'][who]
    print(f"  {who:5s} default runs {c['default_passes']}, stopped {c['stopped']} (growing error {c['guards']['divergence']}, drive change "
          f"{c['guards']['cap_divergence']}), completed once widened {c['stopped_then_widened_completed']}; stops at loops {c['loop_min']} "
          f"to {c['loop_max']}, {c['loop7']} at loop 7, {c['by_loop12']} by loop 12; widened runs {c['widened_runs']}, "
          f"{len(c['widened_stopped'])} stopped on the drive voltage")
print(f"\nHeld-back structures: {d.get('structures_audit')}")
