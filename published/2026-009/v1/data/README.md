The data behind every figure, published under CC BY 4.0. Each file is plain CSV.

| File | What it holds | Written by |
|---|---|---|
| `study_outcomes.csv` | The study's runs at the controller's default checks and with the checks widened, by law and settings: completed, and stopped by which check (Section 3.1) | `study_results.py` |
| `study_scores.csv` | Each law at its defaults, by class of system and stage: medians over structures of the control-gauge, held-out-gauge, level, worst over-test, stress error (with quartiles) and stress bias lines, with and without the flagged structures (Section 3.2, Figure 1) | `study_results.py` |
| `study_change_linear_to_stage2.csv` | The change in the control-gauge, held-out-gauge and stress lines from the linear structure to stage 2, same law, structure and system: median, quartiles, structures up and down; all structures, without the flagged ones, without those whose member changes little in service, and without both (Section 3.4) | `study_results.py` |
| `study_change_by_rig.csv` | The same change in the stress error on each system alone | `study_results.py` |
| `study_scores_by_rig.csv` | Each law at its defaults on each system alone, linear structure (Section 3.1, 3.2) | `study_results.py` |
| `study_change_tuned.csv` | Tuned setting against defaults, same case (Section 3.3) | `study_results.py` |
| `study_change_measured_again.csv` | The frequency response measured again during the run against measured once and kept, same case | `study_results.py` |
| `study_single_effects.csv` | Softening joints only, hardening member only and both, against the linear structure, by system, size and law (Figure 2) | `study_results.py` |
| `study_member_state.csv` | The hardening member's change in service and as tested on each system, and the structures whose member changes little in service (Section 3.4) | `study_results.py` |

The `study_*` files are results of the study, from its 3,793 scorecards (scorer 0.2.1-draft), which
are published in the results record of the study and its audit, version 0.2 (DOI
10.5281/zenodo.24310746).

The `audit_*` CSV files are the same tables computed by the same script from the independent audit's
scorecards of the ten held-back structures (structure 24 left out; there are no runs with the
frequency response measured again, so `audit_change_measured_again.csv` is empty).
`audit_verdicts.json` and `audit_verdicts.md` are the audit's own verdict computation, copied
unchanged (the audit's record is in the same results record); the held-back numbers in Section 3 that compare two laws are
taken from them.

