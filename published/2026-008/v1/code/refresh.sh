#!/bin/sh
# Refresh every number and figure of the benchmark article from the released problems, in one command.
#
#   sh code/refresh.sh SET_FOLDER RESULTS_FOLDER JOURNAL_FOLDER
#
# SET_FOLDER is the Open Benchmark Set, MIMO Random suite, version 0.2, unpacked (DOI 10.5281/zenodo.24310742:
# problems/); RESULTS_FOLDER is the results of the study and its audit, version 0.2, unpacked (DOI
# 10.5281/zenodo.24310746: cards/main, cards/audit, cards/audit2); JOURNAL_FOLDER is a copy of the journal repository, for the tube sections of article 2026-001 (read only). Reads seed 0 of the Frames
# problems (stage 1: frame-12x6, frame-6x6; stage 2: the realistic and strong variants of both) and the study's
# scorecards in RESULTS_FOLDER/cards/. The member's design is read from data/member_design.json. Writes data/ and figures/
# beside this folder. The reference runs go to a temporary folder that is deleted at the end. Needs the Python named
# in PY (default python3) with NumPy, matplotlib and build123d; nothing is installed.
set -e
[ $# -eq 3 ] || { echo "usage: sh code/refresh.sh SET_FOLDER RESULTS_FOLDER JOURNAL_FOLDER"; exit 2; }
REL=$(cd "$1" && pwd)
RES=$(cd "$2" && pwd)
JOURNAL=$(cd "$3" && pwd)
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
PY="${PY:-python3}"
P="$REL/problems"
RUNS=$(mktemp -d)
trap 'rm -rf "$RUNS"' EXIT
nice -n 10 $PY example_run.py "$P/frame-12x6_s00" "$P/frame-6x6_s00" --runs "$RUNS"
nice -n 10 $PY stage2_known.py "$P/frame-12x6-realistic_s00" "$P/frame-12x6-strong_s00" "$P/frame-6x6-realistic_s00" "$P/frame-6x6-strong_s00"
nice -n 10 $PY article_geometry.py "$P/frame-12x6-realistic_s00" "$JOURNAL/articles/2026-001/data/model_elements.csv"
nice -n 10 $PY set_summary.py "$P"
# The closed-loop example of Section 7.4: one scorecard of the study's main batch, copied into data/.
CARDS="$RES/cards/main"
nice -n 10 $PY closed_loop_run.py "$CARDS/s0_6x12_strong_pinv_closed_default_line_hold_divopen.json"
# Section 8, what softening and hardening each do: the single-effect runs of the same study, pooled over its laws,
# with the audit's two batches (ten held-back structures) beside them.
AUD="$RES/cards/audit $RES/cards/audit2"
nice -n 10 $PY effects.py "$CARDS" $AUD
nice -n 10 $PY default_checks.py "$CARDS" $AUD
nice -n 10 $PY fill_article.py "$P/frame-12x6-realistic_s00"
for f in fig_article fig_member fig_level_rule fig_stage1_band_errors fig_stage1_element_stress fig_closed_loop fig_effects; do
  nice -n 10 $PY $f.py
done
echo "refreshed: article.md (from article_template.md), data/ and figures/. Every number the text quotes is in data/article_numbers.csv."
