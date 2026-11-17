The data behind the article. CC BY 4.0.

- `runs_of_record.csv`: one row per case of the study used here (structure, setup, stage, law,
  setting, how the frequency response was treated, which checks the run had), with its scorecard
  figures. Errors in dB. `control_mean` and `held_mean` (the signed mean band error at the control
  and the held-out gauges) are filled for the linear runs at default settings only.
- `setup_analysis.txt`: every result printed by `code/setup_analysis.py`.
- `paired_changes.csv`: each paired change, structure by structure.
- `by_setup_linear.csv`: medians and quartiles by setup and law, linear structures, default settings.
- `s3_correlations.csv`: the rank correlations with the stress error, by stage and kind of setup.
- `warning_signs.csv`: the counts of the warning-sign table and the same for the other setups.
- `fig_setups_frame.csv`, `fig_setups_rig.csv`: the structure and the setups of structure 0.
- `fig_setups_parts.csv`: the solids of structure 0 (tubes with width and wall, masses, the hardening
  member's bracket, strips and mass), the same file as the benchmark article's `fig_article_parts.csv`.
- `fig_paired_setups.csv`, `fig_what_tracks.csv`: the points of the two result figures.
