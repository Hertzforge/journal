# Data of the What-Did-Not-Work Article

Every file here is written by `../code/dnw_data.py` (or, for `number_sources.csv`, by
`../code/fill_article.py`; for `audit_numbers.csv` and `audit_verdicts.csv`, by
`../code/audit_numbers.py`). CC BY 4.0. Rows of screen readings and study run outcomes are readings,
not claims of the study's rule; the claim lists are the study's claims, cited by id.

| File | Rows | What |
|---|---|---|
| `numbers.csv` | 478 | Every number the text quotes: key, text as printed, raw value, source file, how it was read |
| `audit_numbers.csv` | 21 | The audit's numbers the text quotes, in the layout of `numbers.csv`: verdict counts of the 96 stepped-sine pair claims with `matrix` and of the 63 claims of followed poles, the ids that do not hold, and the count and decimals of the rounding verdicts |
| `audit_verdicts.csv` | 2,544 | The audit's verdict on every claim of the study: id, kind, verdict, held-back median and count, the study's median and quartiles |
| `number_sources.csv` | 351 | The keys the article uses, with their text, source and how many times each is used |
| `fig1_mode_shift.csv` | 850 | Every in-band mode of the twelve nonlinear screen structures: low-level frequency and damping, change of frequency and damping factor at full level, shift in low-level bandwidths (Fig 1) |
| `screen_cells.csv` | 147 | Both screens, one row per variant, yardstick, test and tier: runs, completions, gains and losses, ends in tolerance, paired median p95 and worst over-test, IEC share, rule passes (Figs 2, 4) |
| `fig3_whole_sweep_stops.csv` | 72 | Each whole-sweep-rung sweep of the level ladder and `matrix`: outcome, level and frequency where it stopped (Fig 3) |
| `fig4_leads.csv` | 90 | The second screen's rows used by Fig 4 |
| `fig5_start_error.csv` | 1240 | The largest control error along the linear 6 x 6 structure 0 sweep up for followed poles, preview control, preview on a frozen model and `matrix` (Fig 5) |
| `fig6_stepped_runs.csv` | 2280 | Each study stepped sine (T3) and dwell (T4) of `matrix`, `paired` and `ratio`, Hertzforge version: outcome, level, frequency, coverage (Fig 6a) |
| `fig6_coupling.csv` | 380 | For each study structure, the share of steps where the paired shaker is the largest path to its control, against one over the number of shakers (Fig 6b) |
| `fig7_stepped_trace.csv` | 23919 | One stepped sine (linear 6 x 6 structure 0) of the three laws, update by update, with the judged updates marked (Fig 7) |
| `fig8_fits.csv` | 39 | Modes found and within 10 percent by fit method on four frame sets, and the in-band model error under four delay treatments (Fig 8) |
| `stepped_pair_claims.csv` | 142 | The study's stepped-sine pair claims involving `paired` or `ratio` |
| `followed_poles_pair_claims.csv` | 63 | The study's claims of followed poles against the Python `matrix`, with the side of followed poles |
| `sweep_effect_claims.csv` | 145 | The study's sweep-effect claims |

Source folders: the benchmark's research record and the research round's, the problems (the suite,
DOI 10.5281/zenodo.24594791), the screen runs and the study runs (the results record, DOI
10.5281/zenodo.24594793; not the audit's runs), and the modal fits' outputs. `numbers.csv` names the file behind each number.

## The Candidate Laws' Names and the Effort's Codes

The study's claims file (`claims.json`), the screens' run tables and the run records name the
candidate laws by the effort's codes. These files, the article and its figures use the names. To
match a claim, a screen run or a run file with these files, read its code across this table.

| Code in the records | Id in these files | Name in the article |
|---|---|---|
| `K2f` (`k2f`) | `family_inverse` | the family inverse |
| `K3` (`k3`) | `followed_poles` | followed poles |
| `K4` (`k4`), 2 s rungs | `level_ladder` | the level ladder, on the suite's short rungs |
| `K4` (`k4_sw`), whole-sweep rungs | `level_ladder_sw` | the level ladder, on whole-sweep rungs |
| `K5` (`k5`) | `rls_dither` | the dither identification (recursive least squares on a dither at the dwell) |
| `j1` | `pole_trajectory` | pole trajectory |
| `j2` | `amplitude_indexed` | amplitude-indexed poles |
| `j3` | `placed_poles` | placed poles |
| `j4` | `preview` | preview control |
| `j4f` | `preview_frozen` | preview on a frozen model, the check run (a control run, not a variant to recommend) |
