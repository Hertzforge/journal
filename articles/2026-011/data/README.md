# Data

The data behind the article's figures, tables and numbers. Every file is final: all the runs are
finished. A structure's value is the mean over the systems of its class (more control gauges than
shakers, or square) that have a result; medians and quartiles are over structures. One case has no
result: `min_drive` on structure 7 of the 3 x 12 system at the linear and realistic stages, so that
structure's value for `min_drive` is the mean over the other two systems of its class. In the
paired files the counts are of structures on which the difference is more than 0.2 dB each way.

The scorecards these files are written from are in two Zenodo records: the three laws' in
DOI 10.5281/zenodo.24407972 and the six laws' in DOI 10.5281/zenodo.24310746 (`../code/README.md`
gives the commands).

- `law_broyden_example.csv`: the RMS error over the control gauges, cycle by cycle, of the two worked examples printed in Hunter's Broyden description, as the build's tests reproduce them (not a benchmark result).
- `tuning_points.csv`: every setting tried in the tuning of the three laws on structures 30 and 31, one row a setting and a system, mean over four cases; `independent` and `broyden_congruence` on the second commit, `nearly_independent` on the first; column `chosen` marks the setting the tuning rule chose.
- `tuning_points_first_commit.csv`: the tuning of `independent` on the first commit, where its default still had the weighting by the target (the row `solve_weighting = none` is what became the default).
- `study_scores.csv`: each law's scores at its defaults on the study structures 0 to 9, by class of system and stage, all structures and without the flagged ones.
- `study_scores_by_structure.csv`: the same, structure by structure.
- `study_pairs.csv`: paired differences between laws on the same structure and system, over all five systems of a class.
- `study_pairs_two.csv`: the same on the 6 x 12 and 6 x 6 systems alone, the systems of the held-back sample.
- `study_outcomes.csv`: how each run ended under the controller's checks, at their defaults (structures 0 to 4) and widened (the widened counts are over structures 0 to 9).
- `study_settings_scores.csv`: the three laws at their defaults and other settings on the 6 x 12 and 6 x 6 systems, structures 0 to 9; the six laws of the earlier study are there too, at their defaults and at their tuned settings.
- `study_settings_change.csv`: those settings paired case by case with the defaults (setting minus defaults); for the six laws, their tuned settings.
- `audit_scores.csv`, `audit_scores_by_structure.csv`, `audit_pairs.csv`, `audit_outcomes.csv`: the same tables on the held-back structures 20, 21, 22, 23 and 52 (6 x 12 and 6 x 6 systems, defaults).
- `claims.json`: every claim about the three laws, written by `code/make_claims.py` from the study's tables before any held-back scorecard of the law was read, with the time each was written. The exception: the 29 claims that set `nearly_independent` against `independent` or `broyden_congruence` were written after the held-back scorecards of `nearly_independent` had been read (the article, Sections 4 and 5.7).
- `audit_verdicts.csv`: each claim beside the held-back structures, with the study figure on the same system, the held-back figure and the verdict (written by `code/claims_check.py`).
