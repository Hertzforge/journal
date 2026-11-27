# Data for the MIMO Sine Laws Article

CC BY 4.0. Written by the scripts in `code/` (see `code/README.md`); do not edit by hand.

- `law_scope.csv`: the study's size (problems, runs by version, cells by test, claims by kind).
- `law_readings.csv`: by version, law, test and tier: runs, outcomes, completion, the medians and
  quartiles of the IEC share and the worst over-test, runs over 3 and 6 dB, runs inside the check
  point at every judged update.
- `law_safety.csv`, `law_worst_runs.csv`: over-test counts by job, and every scored run's worst
  over-test (Fig 4).
- `law_level_claims.csv`, `law_level_counts.csv`, `law_level_by_shape.csv`: the rule's level claims,
  their counts by job and line (Fig 2), and by system shape (square or more controls than shakers).
- `law_pair_claims.csv`, `law_pair_counts.csv`: the rule's paired claims between laws, and their
  counts by test, pair of laws and reading, with the claim ids (Fig 3).
- `law_followed_poles_cells.csv`: followed poles against the Python `matrix`, cell by cell, with the
  claim where there is one (Fig 5).
- `law_steps.csv`: where each stepped sine ended, by law and tier (Fig 6).
- `law_defaults.csv`, `law_defaults_summary.csv`: the 12 structures run at the engine's default
  protective settings, against their runs of record (Fig 4b).
- `law_repeats.csv`, `law_repeats_summary.csv`: the repeats, against their runs of record.
- `law_agreement.csv`: the two versions' agreement by law and test, comparisons (a) and (b) (Fig 7).
- `screen_cells.csv`: both screens, arm against yardstick by test and tier (Figs 8 and 9).
- `facts.csv`: constants, defaults, commits, hashes and screen facts, each with its source.
- `law_numbers.csv`: the derived numbers the text quotes, each with the file it came from.
- `audit_numbers.csv`: the numbers of the audit on the held-back structures the text quotes, each
  with its source (`verdicts.csv` or the audit's `readings.csv`).
- `audit_verdicts.csv`: the audit's verdict on every claim of the study, with its version, law (the
  candidate law by its name), test, reading or line, side, and the held-back and study medians.
- `number_sources.csv`: every number put into `article.md`: its line, token, value and file.

They are computed from the results record of the study and its audit (DOI 10.5281/zenodo.24594793); the
problems are the MIMO Sine suite, draft 0.1 (DOI 10.5281/zenodo.24594791).

## The Candidate Laws' Names and the Effort's Codes

The study's claims file (`claims.json`) and its run records name the candidate laws by the effort's
codes. These files, the article and its figures use the names. To match a claim of the candidate
law in `claims.json`, or a screen run, with these files, read its code across this table.

| Code in the records | Id in these files | Name in the article |
|---|---|---|
| `K2f` (`k2f`) | `family_inverse` | the family inverse |
| `K3` (`k3`) | `followed_poles` | followed poles |
| `k3_m9d` | `followed_poles_m9d` | followed poles on the M9d fit (screen runs only) |
| `K4` (`k4`), 2 s rungs | `level_ladder` | the level ladder, on short rungs |
| `K4` (`k4_sw`), whole-sweep rungs | `level_ladder_sw` | the level ladder, on whole-sweep rungs |
| `K5` (`k5`) | `rls_dither` | the dither identification (recursive least squares on a dither at the dwell) |
| `j1` | `pole_trajectory` | pole trajectory |
| `j2` | `amplitude_indexed` | amplitude-indexed poles |
| `j3` | `placed_poles` | placed poles |
| `j4` | `preview` | preview control |
| `j4f` | `preview_frozen` | preview on a frozen model (a control run, not a lead) |

