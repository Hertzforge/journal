# Code

`make_data.py <study folder>` writes the files in `../data` from the study's output files. All four are
published in the study's scorecards record (DOI 10.5281/zenodo.24563639): put `study_tables_output.json` and
`claims_study_output.json` in `<study folder>/experiments/`, and `a1_verdicts.json` and the audit's report
`A1_Audit_2026-11-26.md` in `<study folder>/audit/`. `default_checks.csv` copies the report's defaults table,
whose rows are those of the record's cards in `defaults.zip` (checks at their defaults) and `pilot.zip` (checks
widened). Each `fig_*.py` draws one figure into `../figures` from `../data`; `style.py` holds the shared
look, the names and the readers. Python 3.11 with numpy and matplotlib. `fig_setups.png` is not drawn here: it is reproduced from
article 2026-010.
