# Code

The scripts that write the article's data and draw its figures. None runs a control law or a
Hertzforge binary. Run each from this folder with `PYTHONDONTWRITEBYTECODE=1 python3 NAME.py`.
Copyright 2026 Kevin Cross and Norman Hunter. MIT license.

- `style.py`: the shared look of the figures (series colors, hatches, the laws' order and names, paths).
- `law_results.py`: reads the study and held-back scorecards and writes the `study_*` and `audit_*` CSV files in `../data`.
- `tuning_results.py`: reads the tuning scorecards and writes `../data/tuning_points.csv` and `../data/tuning_points_first_commit.csv`.
- `make_claims.py`: writes the claims about a law from the study's tables by one rule, before its held-back runs are read, and appends them to `../data/claims.json`; it reads no held-back result.
- `claims_check.py`: sets the claims written before the held-back runs were read beside the held-back results and writes `../data/audit_verdicts.csv`.
- `fig_broyden_example.py`: draws `fig_broyden_example.png`, the worked examples of Hunter's Broyden description, from `law_broyden_example.csv`.
- `fig_tuning_points.py`: draws `fig_tuning_points.png`, every setting tried in the tuning, from `tuning_points.csv`.
- `fig_tuning_independent.py`: draws `fig_tuning_independent.png`, the independent drive law solved three ways on the tuning cases, from `tuning_points.csv`.
- `fig_tuning_broyden_parts.py`: draws `fig_tuning_broyden_parts.png`, the Broyden law with the learning off and with phase steering off, from `tuning_points.csv`.
- `fig_checks.py`: draws `fig_checks.png`, what the controller's default checks did with each law, from `study_outcomes.csv`.
- `fig_scores_by_law.py`: draws `fig_scores_by_law.png`, each law's errors on the linear structures, from `study_scores.csv`.
- `fig_level_by_law.py`: draws `fig_level_by_law.png`, each law's level on the linear structures, from `study_scores.csv`.
- `fig_stages_by_law.py`: draws `fig_stages_by_law.png`, each law's stress error by stage, from `study_scores.csv`.
- `fig_settings.py`: draws `fig_settings.png`, the three laws at their other settings on the study structures, from `study_settings_scores.csv`.
- `fig_held_back.py`: draws `fig_held_back.png`, every claim set beside the held-back structures, from `audit_verdicts.csv`.

## Where the Scorecards Are

`law_results.py` and `tuning_results.py` read scorecards, which are not in this bundle. They are in
two Zenodo records: the three laws' scorecards in "Hertzforge Open Benchmark Set, MIMO Random Suite:
Results of the Study of Independent Drive Laws and a Broyden Congruence Law"
(DOI 10.5281/zenodo.24407972), and the six laws' in "Hertzforge Open Benchmark Set, MIMO Random
Suite: Results of the Control Law Study and Its Independent Audit" (DOI 10.5281/zenodo.24310746).
With both unpacked, `NEW` the `cards` folder of the first and `SIX` the `cards` folder of the
second, these four commands write the `study_*`, `audit_*` and `tuning_*` files of `../data` again,
byte for byte (checked 2026-11-20):

```sh
L=independent,nearly_independent,broyden_congruence
python3 law_results.py six=$SIX/main $L=$NEW/main
python3 law_results.py six=$SIX/audit,$SIX/audit2 $L=$NEW/held_back --audit
python3 tuning_results.py $L=$NEW/tuning
python3 tuning_results.py --out tuning_points_first_commit.csv independent=$NEW/tuning_first_commit
```
