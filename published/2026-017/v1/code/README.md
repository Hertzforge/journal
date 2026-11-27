# Code for the MIMO Sine Laws Article

Python 3 with NumPy and Matplotlib. Copyright 2026 Kevin Cross. MIT license. Run from the article's
folder, one script at a time; the order matters, since each step reads what the one before wrote.

1. `law_results.py STUDY_RUNS PROBLEMS` (run with `-I`): reads the study's run cards, the frozen
   `readings.csv` and `claims.json`, and writes the `law_*.csv` files of `data/` (readings by job and
   tier, safety, worst runs, level and pair claims and their counts, the cells of followed poles, stepped-sine
   endings, the defaults and repeats sets, the scope). Runs nothing and reads no audit run.
   STUDY_RUNS is the study's run folder of the results record (DOI 10.5281/zenodo.24594793) and
   PROBLEMS the suite's draft 0.1 problem folders (DOI 10.5281/zenodo.24594791).
2. `facts.py SINE_BENCHMARK SUITE_REPO HERTZFORGE_REPO STUDY_RUNS RUNNER_FORMAT HELDOUT_PROBLEMS`
   (run with `-I`): writes `data/facts.csv`, `data/law_agreement.csv` and `data/screen_cells.csv`: the
   suite's constants (from `sine/FORMAT_SINE.md` and `sine/make_claims.py`), the laws' defaults (from
   Hertzforge's `docs/control-laws.md` on main), the commits (read-only git: `rev-parse`,
   `merge-base`, `cat-file -e`, `diff --name-only`), the runners' SHA-256 from the run cards, the protective
   settings, the agreement sample and both screens' records. Of the held-back problems it reads only
   the folder names.
3. `law_numbers.py`: writes `data/law_numbers.csv`, every percentage, range, count and first claim id
   the text quotes, each row naming the file it came from.
4. `fig1_readings.py` to `fig9_screen_j.py`, with `style.py`: the nine figures, PNG and PDF, into
   `figures/`. Each reads only the files named in its figure's `data=` attribute.
The study's records name the candidate laws by the effort's codes; `law_results.py` (`RECORD_LAW`)
and `facts.py` (`RECORD_ARM`) give each its name as they read, so every file in `data/` and every
figure uses the names. `data/README.md` maps the two.

4a. `audit_numbers.py CLAIMS_JSON VERDICTS_CSV AUDIT_READINGS_CSV R_AUDIT_MD` (run with `-I`): writes
   `data/audit_numbers.csv` (key, value, source: the verdict counts by law, kind, job, line and test,
   the claim ids that do not hold, the held-back readings computed as `law_results.py` and
   `law_numbers.py` compute the study's, and the rounding count) and `data/audit_verdicts.csv` (every
   claim's verdict, with its version, law, test, reading or line and side). It reads of the audit
   only its verdicts and readings, and its report for the list of verdicts that turn on rounding. It
   checks 112 of its formulas on the study's readings against `law_numbers.csv`, and asserts the
   statements the text makes in words (for example that no Hertzforge sweep or step level claim
   fails).

5. `fill_article.py`:
 writes `../article.md` from `article_src.md`, putting in every number from
   `data/` (tokens `{{key}}`, `{{f:key}}`, `{{s:key}}`, `{{pct:a:b}}`, `{{fpct:key}}`, `{{r0:key}}` to
   `{{r2:key}}`, `{{a:key}}` from `audit_numbers.csv`, `{{vg:k1+k2}}` the held-back verdicts of the
   claims named), and `data/number_sources.csv`. It stops if a claim id it prints, whose held-back
   verdict is not "holds", has no `vg` token in its paragraph. It stops on a missing or empty key and prints the
   count of numerals left outside tokens (section numbers, standards' names, system names, claim ids
   and the like), for reading over.
