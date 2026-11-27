# Code of the What-Did-Not-Work Article

Copyright 2026 Kevin Cross. MIT license. Python 3 with NumPy and Matplotlib. Run one process at a time under `nice -n 10`.

- `dnw_data.py`: reads the record and the run folders and writes every data file in `../data/`,
  with `numbers.csv` (each number of the text: key, text as printed, raw value, source file, how it
  was read). Arguments: `--effort` (the benchmark's research record), `--research` (the research round's
  record), `--problems` (the suite's problem folders, DOI 10.5281/zenodo.24594791), `--g-runs`,
  `--j-runs`, `--study` (the study's run folder, results record, DOI 10.5281/zenodo.24594793) and `--fits`
  (the modal fits' outputs). It refuses any path
  under `audit_runs/`, and stops on a duplicate key or a missing value. It cross-checks its screen
  tallies against the screens' own report files and stops if they differ. Run with `-I`.
  The record names the candidate laws by the effort's codes; `RECORD_ARM` maps each code to the
  id these files use (`family_inverse`, `followed_poles` and so on, the table in
  `../data/README.md`) as the runs and claims are read, and `ARM_CODE` maps back to find a run's
  files. The record's own text is still matched by its codes.
- `style.py`: the figures' shared colors, markers, hatches and labels (after the laws draft), so no
  figure needs color to be read.
- `fig1_mode_shift.py` to `fig8_fits.py`: one figure each, PNG and PDF to `../figures/`. Each reads
  only the files named in its docstring and in the figure's `data=` attribute. Run with `-s` from
  this folder (they import `style`).
- `audit_numbers.py VERDICTS_CSV R_AUDIT_MD` (run with `-I`): writes `../data/audit_numbers.csv`
  (in the layout of `numbers.csv`: the verdict counts of the stepped-sine pair claims with `matrix`
  and of the claims of followed poles, with their verbs, and the claim ids that do not hold) and
  `../data/audit_verdicts.csv` (every claim's verdict, without the claims' text). The claim sets are
  read from `../data/stepped_pair_claims.csv` and `../data/followed_poles_pair_claims.csv`. The
  report is read only for its list of the verdicts that turn on rounding; the script asserts that
  none is among the claims counted here, and that every claim counted was tested.
- `fill_article.py`: fills every `{{key}}` of `article_src.md` from `../data/numbers.csv` and
  `../data/audit_numbers.csv` (it stops on a key in both), and `{{vg:id+id}}` with the held-back
  verdicts of the claims named; writes `../article.md` and `../data/number_sources.csv`, stops on an
  unknown key or on a claim id it prints, whose verdict is not "holds", with no `vg` token in its
  paragraph, and lists the numerals left in the prose that are not tokens (all labels).
- `article_src.md`: the article's source. Edit this, not `../article.md`.

Rebuild order: `dnw_data.py`, the eight figure scripts, `audit_numbers.py`, `fill_article.py`.
