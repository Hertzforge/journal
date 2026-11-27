The code that writes the data of Sections 2 to 7 and draws Figures 2 to 8. It is published under the
MIT license. Every number it writes is pooled over the laws or carries a claim identifier; no law is
named. Figure 1 is reproduced from 2026-008, whose code draws it.

1. `suite_results.py` (NumPy) reads the study's run folders, its readings and claims files, the
   problem folders, the held-back problem folders and the comparison of the two versions, and writes
   every file in `../data` but the two copied for Figure 1. It runs nothing; it imports the problem
   folder's own `sine_model.py` for the suite's constants and nothing else of the suite:
   `python suite_results.py STUDY_RUNS PROBLEMS HELDOUT_PROBLEMS AGREEMENT`, where STUDY_RUNS is the
   study's run folder with its `claims` and `rescore` folders (results record, DOI
   10.5281/zenodo.24594793), PROBLEMS and HELDOUT_PROBLEMS the
   suite's draft 0.1 problem folders (DOI 10.5281/zenodo.24594791) and the held-back problem folders, and AGREEMENT the folder of
   the comparison's pair files and outputs. It refuses an audit run folder.
2. `fig2_tests.py`, `fig3_before.py`, `fig4_agreement.py`, `fig5_tiers.py`, `fig6_levels.py` and
   `fig7_defaults_repeats.py` (Matplotlib) draw Figures 2 to 7 from those files into `../figures`, as
   PNG and PDF. `style.py` holds their shared colors and axes.
3. `check_numbers.py` checks that every number in the article's text is a number `suite_results.py`
   wrote to `numbers.csv`, apart from names (claim identifiers, systems, problems, structures,
   standards, clauses, sections, hashes and DOIs): `python check_numbers.py [ARTICLE]`. It exits 1
   and lists the numbers it cannot find. It checks that a number exists, not that it is attached to
   the right statement.
4. `article_src.md` is the article's source since the audit: the article with every audit number as
   a slot `[AUDIT: key ...]`. Edit it, never `../article.md`. `audit_fill.py CLAIMS VERDICTS
   AUDIT_READINGS --report R_AUDIT_MD --apply article_src.md` writes `../data/audit_numbers.csv` and
   `../data/audit_verdicts.csv` (without the claims' text, which names the laws), and writes
   `../article.md` from the source with every slot filled. A slot `vg_R2340_R2364` is the held-back
   verdict of the claims named, grouped by verdict. R_AUDIT_MD is read only for its list of the
   verdicts that turn on rounding; each is checked to read "weaker" with its audit median on a stored
   quartile. The tool exits 1 if a slot is left unfilled or if a claim identifier the article prints,
   whose verdict is not "holds", has no `vg_` slot in its paragraph. `fig_audit.py` draws Figure 8 from
   `audit_verdicts.csv` and `effects.csv`. `check_numbers.py` also reads `audit_numbers.csv`.

Run in the article's folder, in this order:

    python3 code/suite_results.py STUDY_RUNS PROBLEMS HELDOUT_PROBLEMS AGREEMENT
    python3 code/fig2_tests.py   # and fig3 to fig7 the same way
    nice -n 10 python3 code/audit_fill.py CLAIMS_JSON VERDICTS_CSV AUDIT_READINGS_CSV \
        --report R_AUDIT_MD --apply code/article_src.md
    python3 code/fig_audit.py
    python3 code/check_numbers.py
