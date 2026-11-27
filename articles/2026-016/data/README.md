The data behind every figure and number, published under CC BY 4.0. Each file is plain CSV. No law
is named: a level claim carries its claim identifier, and the default and repeat sets number the laws.

| File | What it holds | Written by |
|---|---|---|
| `numbers.csv` | Every number the article's text states: a key, the value, the text as printed, and the file and field it comes from. `code/check_numbers.py` checks the article against it | `suite_results.py` |
| `problems.csv` | One row a problem, study (380) and held back (230): system, kind, structure number, modes, how full level was set, full level in g, the Random problem's median change, the ideal drive's peak before the gain, the declared deviation, the quasi-steady state at full level and 6 dB over, the generation's play, the highest reachable frequency, the stepped and dwell schedules, how far the dwell mode moves, and the limit test's gap and bite (Sections 2 and 5; Figure 3) | `suite_results.py` |
| `example_reference.csv` | Problem `frame-12x6-realistic`, structure 0: the reference over the specification on the 2,553-point grid (lowest, median and highest control) and the largest ideal drive in engine volts (Figure 2) | `suite_results.py` |
| `schedules.csv` | The tone's frequency against time at full level for each test of the same problem (Figure 2) | `suite_results.py` |
| `agreement.csv` | The comparison of the two versions: pairs, outcome agrees, outcome and every reading agree, by comparison and test (Section 4.3; Figure 4) | `suite_results.py`, from the comparison's pair files |
| `pooled.csv` | Readings pooled over the laws, by version, system (and all systems), kind and test: runs, laws, the share completed and held, the IEC share's median and quartiles, the median completion and worst over-test, the share scored (Section 7; Figure 5) | `suite_results.py` |
| `effects.csv` | Every effect claim: identifier, version, system, kind and the kind it is set against, test, reading, side, the study's median and quartiles, units, laws, and the units on each side (Section 7.1) | `suite_results.py`, from the claims file |
| `levels.csv` | Every level claim: identifier, version, system, kind, test, line, side, the median excursion and its quartiles, structures, unscored runs, and the median IEC share and completion beside it (Section 7.2; Figure 6) | `suite_results.py`, from the claims file |
| `defaults.csv` | Each run at the engine's default protections beside the same case in the runs of record: outcome, IEC share and completion (Section 7.4; Figure 7) | `suite_results.py` |
| `repeats.csv` | Each repeat beside its run of record: outcome and IEC share (Section 7.4; Figure 7) | `suite_results.py` |
| `fig_article_parts.csv`, `fig_article_rig.csv` | Copied unchanged from 2026-013, which copied them from 2026-008, for Figure 1 | 2026-008 |

Written after the audit, by `audit_fill.py`: `audit_numbers.csv` (key, value and the text as printed
of every `[AUDIT: ...]` slot in `code/article_src.md`; `code/check_numbers.py` reads it with
`numbers.csv`) and `audit_verdicts.csv` (the audit's verdict on every claim: identifier, kind,
verdict, the held-back median and its count, the study's median and quartiles; Section 6.4 and
Figure 8). The claims' text is left out, since it names the laws; it is in the claims file under each
identifier.

The run files they are computed from are in the results record of the study and its audit
(DOI 10.5281/zenodo.24594793); the problems are the MIMO Sine suite, draft 0.1
(DOI 10.5281/zenodo.24594791).
