# Audit Verdicts (structures [20, 21, 22, 23, 26, 27, 28, 50, 51, 52])

| Claim | What (dB) | Study median [Q1, Q3] (n) | Audit median [Q1, Q3] (n) | Verdict | Audit structures, same sign |
|---|---|---|---|---|---|
| 4 | square linear: band_average minus pinv_closed, stress | -9.25 [-9.74, -7.50] (20) | -7.71 [-9.67, -6.89] (10) | holds | 10 of 10 |
| 4 | square linear: band_average minus pinv_open, stress | -11.21 [-12.79, -9.83] (20) | -9.07 [-10.47, -7.66] (10) | weaker | 10 of 10 |
| 4 | square linear: band_average minus buzz_match, stress | -9.23 [-10.11, -7.34] (20) | -8.17 [-10.43, -7.43] (10) | holds | 10 of 10 |
| 5 | square none: band_average minus shape_svd, stress | -0.70 [-1.03, -0.29] (20) | -0.49 [-1.51, +0.72] (10) | holds | 6 of 10 |
| 5 | square realistic: band_average minus shape_svd, stress | -0.49 [-0.70, -0.09] (20) | -0.93 [-1.28, -0.30] (10) | weaker | 8 of 10 |
| 5 | square strong: band_average minus shape_svd, stress | +0.73 [+0.02, +1.87] (20) | +0.26 [-0.62, +1.15] (10) | holds | 5 of 10 |
| 6 | non-square linear: band_average minus pinv_closed, stress | -0.56 [-0.89, -0.13] (20) | -0.82 [-1.16, -0.03] (10) | holds | 8 of 10 |
| 6 | non-square linear: band_average minus shape_svd, stress | -0.97 [-1.58, -0.62] (20) | -1.42 [-1.49, -1.13] (10) | holds | 10 of 10 |
| 7 | non-square strong minus linear, buzz_match, stress | +1.91 [+0.89, +2.38] (20) | +1.57 [+0.81, +1.88] (10) | holds | 9 of 10 |
| 7 | non-square strong minus linear, pinv_open, stress | +1.32 [+0.81, +1.69] (20) | +1.41 [+0.98, +1.77] (10) | holds | 10 of 10 |
| 7 | non-square strong minus linear, pinv_closed, stress | +1.16 [+0.25, +1.83] (20) | +1.29 [+0.89, +1.60] (10) | holds | 9 of 10 |
| 7 | non-square strong minus linear, min_drive, stress | +0.93 [+0.45, +1.62] (20) | +0.76 [+0.14, +1.61] (10) | holds | 7 of 10 |
| 7 | non-square strong minus linear, band_average, stress | +0.77 [+0.21, +1.14] (20) | +0.75 [+0.18, +1.45] (10) | holds | 9 of 10 |
| 7 | non-square strong minus linear, shape_svd, stress | -0.28 [-0.87, +0.33] (20) | -0.02 [-0.21, +0.21] (10) | does not hold | 5 of 10 |
| 8 | square strong minus linear, min_drive, stress | +5.79 [+3.40, +6.79] (20) | +4.36 [+3.15, +5.36] (10) | holds | 9 of 10 |
| 8 | square strong minus linear, band_average, stress | +2.27 [+0.59, +3.52] (20) | +1.00 [+0.45, +1.92] (10) | holds | 8 of 10 |
| 8 | square strong minus linear, pinv_open, stress | +1.12 [+0.03, +3.09] (20) | +2.17 [+1.04, +2.55] (10) | holds | 9 of 10 |
| 9 | square realistic minus linear, pinv_closed, stress | -1.72 [-2.43, -1.18] (20) | -2.13 [-2.77, -0.83] (10) | holds | 9 of 10 |
| 9 | square realistic minus linear, buzz_match, stress | -1.50 [-2.08, -1.01] (20) | -1.31 [-2.11, -0.62] (10) | holds | 9 of 10 |
| 9 | square realistic minus linear, min_drive, stress | +1.55 [+0.58, +3.28] (20) | +1.17 [-0.03, +1.77] (10) | holds | 7 of 10 |
| 10 | non-square (6x12) strong softening only minus linear, pinv_closed, stress | +1.97 [+1.02, +2.26] (10) | +1.50 [+0.88, +2.34] (10) | holds | 9 of 10 |
| 10 | non-square (6x12) strong softening only minus linear, pinv_open, stress | +1.32 [+0.75, +2.24] (10) | +1.62 [+0.80, +2.00] (10) | holds | 9 of 10 |
| 10 | non-square (6x12) strong softening only minus linear, buzz_match, stress | +1.17 [+0.69, +2.12] (10) | +1.22 [+0.43, +1.86] (10) | holds | 8 of 10 |
| 10 | non-square (6x12) strong softening only minus linear, min_drive, stress | +0.66 [-0.16, +1.48] (10) | +0.69 [+0.09, +1.27] (10) | holds | 8 of 10 |
| 10 | non-square (6x12) strong softening only minus linear, band_average, stress | +0.59 [+0.10, +1.58] (10) | +0.61 [+0.16, +1.17] (10) | holds | 8 of 10 |
| 10 | square (6x6) strong softening only minus linear, min_drive, stress | +3.72 [+0.97, +4.95] (10) | +3.93 [+1.45, +4.92] (10) | holds | 9 of 10 |
| 10 | square (6x6) strong softening only minus linear, band_average, stress | +1.83 [+1.28, +4.10] (10) | +1.10 [+0.55, +1.82] (10) | weaker | 8 of 10 |
| 11 | square (6x6) none: tuned minus default, pinv_closed, stress | -6.39 [-8.41, -4.50] (10) | -6.30 [-8.18, -5.37] (10) | holds | 10 of 10 |
| 11 | square (6x6) realistic: tuned minus default, pinv_closed, stress | -3.65 [-6.18, -2.96] (10) | -4.71 [-7.27, -2.86] (10) | holds | 10 of 10 |
| 11 | square (6x6) strong: tuned minus default, pinv_closed, stress | -3.11 [-3.76, -2.48] (10) | -4.09 [-5.23, -2.80] (10) | weaker | 10 of 10 |
| 11 | square (6x6) none: tuned minus default, pinv_open, stress | -11.57 [-12.32, -9.26] (10) | -9.09 [-12.12, -6.42] (10) | weaker | 10 of 10 |
| 11 | square (6x6) realistic: tuned minus default, pinv_open, stress | -9.54 [-11.58, -8.26] (10) | -10.24 [-13.40, -7.23] (10) | holds | 10 of 10 |
| 11 | square (6x6) strong: tuned minus default, pinv_open, stress | -8.88 [-13.55, -7.04] (10) | -8.26 [-9.90, -6.73] (10) | holds | 10 of 10 |
| 11 | non-square (6x12) none: tuned minus default, shape_svd, stress | -0.53 [-0.74, -0.43] (10) | -0.88 [-1.16, -0.45] (10) | weaker | 10 of 10 |
| 11 | non-square (6x12) strong: tuned minus default, shape_svd, stress | +0.86 [+0.25, +1.17] (10) | -0.26 [-0.36, +0.02] (10) | does not hold | 3 of 10 |
| 11 | non-square (6x12) strong: tuned minus default, pinv_closed, stress | -0.90 [-1.12, -0.44] (10) | -0.90 [-1.33, -0.23] (10) | holds | 9 of 10 |
| S1 | 6x6 minus 6x12, pinv_closed, ctrl | -2.65 [-3.29, -2.28] (20) | -2.40 [-2.99, -1.82] (10) | holds | 10 of 10 |
| S1 | 6x6 minus 6x12, pinv_closed, held | +3.67 [+2.35, +5.02] (20) | +5.29 [+3.04, +6.07] (10) | weaker | 10 of 10 |
| S1 | 6x6 minus 6x12, pinv_closed, stress | +7.39 [+5.65, +9.05] (20) | +8.71 [+5.30, +9.93] (10) | holds | 10 of 10 |
| S1 | 12x12 minus 12x24, pinv_closed, stress | +9.40 [+7.59, +10.57] (20) | +9.35 [+5.60, +11.89] (10) | holds | 10 of 10 |
| S1 | 6x6 minus 6x12, pinv_open, ctrl | -0.84 [-1.31, +0.28] (20) | -0.99 [-1.64, -0.43] (10) | holds | 8 of 10 |
| S1 | 6x6 minus 6x12, pinv_open, held | +6.15 [+4.30, +7.20] (20) | +7.01 [+4.57, +7.42] (10) | holds | 10 of 10 |
| S1 | 6x6 minus 6x12, pinv_open, stress | +11.50 [+10.04, +13.14] (20) | +10.26 [+7.24, +12.14] (10) | holds | 10 of 10 |
| S1 | 12x12 minus 12x24, pinv_open, stress | +10.26 [+8.04, +13.66] (20) | +8.18 [+6.19, +12.61] (10) | holds | 10 of 10 |
| S1 | 6x6 minus 6x12, shape_svd, ctrl | -0.84 [-1.13, -0.64] (20) | -0.71 [-1.03, -0.22] (10) | holds | 8 of 10 |
| S1 | 6x6 minus 6x12, shape_svd, held | +0.39 [-0.27, +0.87] (20) | +0.48 [-0.47, +1.39] (10) | holds | 7 of 10 |
| S1 | 6x6 minus 6x12, shape_svd, stress | -0.13 [-0.89, +0.22] (20) | -0.54 [-1.16, +0.13] (10) | holds | 6 of 10 |
| S1 | 12x12 minus 12x24, shape_svd, stress | +0.28 [-0.26, +0.78] (20) | -0.24 [-0.50, +0.23] (10) | does not hold | 3 of 10 |
| S1 | 6x6 minus 6x12, buzz_match, ctrl | -2.24 [-2.90, -1.75] (20) | -2.02 [-2.52, -1.34] (10) | holds | 10 of 10 |
| S1 | 6x6 minus 6x12, buzz_match, held | +3.87 [+2.68, +5.13] (20) | +5.22 [+2.89, +6.22] (10) | weaker | 10 of 10 |
| S1 | 6x6 minus 6x12, buzz_match, stress | +8.15 [+5.38, +8.92] (20) | +8.26 [+5.14, +10.45] (10) | holds | 10 of 10 |
| S1 | 12x12 minus 12x24, buzz_match, stress | +9.80 [+7.82, +10.74] (20) | +9.81 [+7.66, +12.00] (10) | holds | 10 of 10 |
| S1 | 6x6 minus 6x12, min_drive, ctrl | -1.63 [-2.13, -1.20] (20) | -1.85 [-2.97, -1.41] (10) | holds | 10 of 10 |
| S1 | 6x6 minus 6x12, min_drive, held | +2.63 [+0.85, +3.15] (20) | +2.47 [+0.86, +3.24] (10) | holds | 9 of 10 |
| S1 | 6x6 minus 6x12, min_drive, stress | +2.61 [+2.19, +3.78] (20) | +2.28 [+0.67, +3.18] (10) | holds | 8 of 10 |
| S1 | 12x12 minus 12x24, min_drive, stress | +2.71 [+1.34, +4.57] (20) | +3.50 [+0.79, +8.14] (10) | holds | 8 of 10 |
| S1 | 6x6 minus 6x12, band_average, ctrl | -2.12 [-2.55, -1.68] (20) | -2.09 [-2.88, -1.70] (10) | holds | 10 of 10 |
| S1 | 6x6 minus 6x12, band_average, held | +1.10 [+0.34, +1.83] (20) | +1.48 [-0.01, +2.42] (10) | holds | 7 of 10 |
| S1 | 6x6 minus 6x12, band_average, stress | +0.39 [-0.42, +0.70] (20) | +0.41 [+0.01, +1.48] (10) | holds | 7 of 10 |
| S1 | 12x12 minus 12x24, band_average, stress | +0.12 [-0.23, +0.56] (20) | +0.07 [-0.37, +0.80] (10) | does not hold | 5 of 10 |
| S2 | 6x6 linear tuned minus default, pinv_closed, ctrl | +0.23 [-0.29, +0.38] (10) | -0.07 [-0.26, +0.35] (10) | does not hold | 5 of 10 |
| S2 | 6x6 linear tuned minus default, pinv_closed, held | -3.05 [-3.32, -2.57] (10) | -3.41 [-4.20, -2.92] (10) | weaker | 10 of 10 |
| S2 | 6x6 linear tuned minus default, pinv_closed, stress | -6.39 [-8.41, -4.50] (10) | -6.30 [-8.18, -5.37] (10) | holds | 10 of 10 |
| S2 | 6x6 linear tuned minus default, pinv_open, ctrl | -0.88 [-1.25, +0.64] (10) | -0.72 [-1.42, +0.33] (10) | holds | 7 of 10 |
| S2 | 6x6 linear tuned minus default, pinv_open, held | -5.03 [-5.50, -3.16] (10) | -4.93 [-6.27, -3.96] (10) | holds | 10 of 10 |
| S2 | 6x6 linear tuned minus default, pinv_open, stress | -11.57 [-12.32, -9.26] (10) | -9.09 [-12.12, -6.42] (10) | weaker | 10 of 10 |
| S5 | 12x12 minus 6x12, pinv_closed, ctrl | -1.21 [-1.90, -0.77] (20) | -0.95 [-1.37, -0.21] (10) | holds | 8 of 10 |
| S5 | 12x12 minus 6x12, pinv_closed, held | +4.78 [+3.97, +5.18] (20) | +3.50 [+2.97, +5.04] (10) | weaker | 10 of 10 |
| S5 | 12x12 minus 6x12, pinv_closed, stress | +8.82 [+8.20, +10.33] (20) | +8.53 [+5.75, +10.74] (10) | holds | 10 of 10 |
| S5 | 12x12 minus 6x12, shape_svd, stress | -0.21 [-0.61, +0.08] (20) | -0.09 [-0.52, +0.03] (10) | does not hold | 7 of 10 |
| S5 | 12x12 minus 6x12, band_average, stress | -0.46 [-0.94, -0.24] (20) | -0.74 [-1.31, -0.17] (10) | holds | 8 of 10 |

## Counts

```
{
 "study": {
  "default_passes": 990,
  "stopped": 901,
  "share": 0.9101010101010101,
  "guards": {
   "divergence": 840,
   "cap_divergence": 61
  },
  "loop_min": 6,
  "loop_max": 34,
  "loop7": 719,
  "by_loop12": 864,
  "stopped_then_widened_completed": 901,
  "completed_block_A_default_by_law": {
   "pinv_closed": "14 of 75",
   "pinv_open": "22 of 75",
   "shape_svd": "0 of 75",
   "buzz_match": "1 of 75",
   "min_drive": "4 of 75",
   "band_average": "0 of 75"
  },
  "widened_runs": 2803,
  "widened_stopped": [
   [
    "s35_3x12_none_min_drive_default_line_hold_divopen",
    "drive_vrms",
    26,
    "Drive 2 (channel 103) reached 5.646 V rms against its 5.610 V abort."
   ],
   [
    "s7_3x12_none_min_drive_default_line_hold_divopen",
    "drive_vrms",
    15,
    "Drive 2 (channel 103) reached 5.635 V rms against its 5.610 V abort."
   ],
   [
    "s7_3x12_realistic_min_drive_default_line_hold_divopen",
    "drive_vrms",
    14,
    "Drive 2 (channel 178) reached 5.754 V rms against its 5.610 V abort."
   ]
  ],
  "completed_at_defaults": 89
 },
 "audit": {
  "default_passes": 870,
  "stopped": 811,
  "share": 0.9321839080459771,
  "guards": {
   "divergence": 792,
   "cap_divergence": 19
  },
  "loop_min": 6,
  "loop_max": 35,
  "loop7": 654,
  "by_loop12": 785,
  "stopped_then_widened_completed": 810,
  "completed_block_A_default_by_law": {
   "pinv_closed": "12 of 75",
   "pinv_open": "18 of 75",
   "shape_svd": "0 of 75",
   "buzz_match": "0 of 75",
   "min_drive": "1 of 75",
   "band_average": "1 of 75"
  },
  "widened_runs": 1681,
  "widened_stopped": [
   [
    "s23_3x12_none_min_drive_default_line_hold_divopen",
    "drive_vrms",
    10,
    "Drive 0 (channel 101) reached 5.745 V rms against its 5.610 V abort."
   ]
  ],
  "completed_at_defaults": 59
 }
}
```

## S3 and S4

```
{
 "study": {
  "square": {
   "n": 240,
   "rho_ctrl": 0.24814666921300713,
   "rho_held": 0.8501284744526814,
   "rho_csum": -0.08773676626330316,
   "rho_hsum": 0.9072492577996144,
   "exact_fit_flag": 1,
   "ctrl_A_or_B": 238,
   "held_A_or_B": 74,
   "stress_within_3": 41,
   "alarm": 240
  },
  "non-square": {
   "n": 358,
   "rho_ctrl": 0.7169677911468971,
   "rho_held": 0.5544540718202906,
   "rho_csum": 0.6728739767798313,
   "rho_hsum": 0.6306025623707102,
   "exact_fit_flag": 0,
   "ctrl_A_or_B": 304,
   "held_A_or_B": 253,
   "stress_within_3": 129,
   "alarm": 358
  }
 },
 "audit": {
  "square": {
   "n": 120,
   "rho_ctrl": 0.27244947565803174,
   "rho_held": 0.8082644628099173,
   "rho_csum": -0.1616640044447531,
   "rho_hsum": 0.8799361066740744,
   "exact_fit_flag": 0,
   "ctrl_A_or_B": 120,
   "held_A_or_B": 43,
   "stress_within_3": 17,
   "alarm": 120
  },
  "non-square": {
   "n": 179,
   "rho_ctrl": 0.625463980080765,
   "rho_held": 0.7067896972359969,
   "rho_csum": 0.6417320528110811,
   "rho_hsum": 0.6828845228380724,
   "exact_fit_flag": 0,
   "ctrl_A_or_B": 159,
   "held_A_or_B": 138,
   "stress_within_3": 57,
   "alarm": 179
  }
 }
}
```

## Claim 13

```
{
 "study": {
  "3x12": -0.136880390763372,
  "6x12": 0.5654086906414224,
  "12x24": 1.0981958908556355,
  "6x6": 3.4126897394852307,
  "12x12": 2.2130934538880043,
  "softening_played_median": -4.724424591352908,
  "softening_service_median": -3.0234438739489695,
  "structures_member_service_under_1pct": 10,
  "structures": 20
 },
 "audit": {
  "3x12": 0.20873644412462422,
  "6x12": 1.381464637219998,
  "12x24": 2.017443798566215,
  "6x6": 3.8364417785928584,
  "12x12": 3.908700502858753,
  "softening_played_median": -4.681402653450636,
  "softening_service_median": -3.0174144258707374,
  "structures_member_service_under_1pct": 6,
  "structures": 10
 }
}
```
