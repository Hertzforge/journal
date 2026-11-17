# Data

Every file here is written by a script in `../code/` (`code/refresh.sh` runs them all from the Hertzforge Open Benchmark Set,
MIMO Random suite, version 0.2, DOI 10.5281/zenodo.24310742, and its results record, DOI 10.5281/zenodo.24310746),
except one:

- `member_design.json`: the hardening member's design for the four stage 2 problems of structure 0
  (`frame-12x6-realistic_s00`, `frame-12x6-strong_s00`, `frame-6x6-realistic_s00`, `frame-6x6-strong_s00`): the
  strips, the mass, the tuned frequency, the stiffness terms, where the member sits on the structure, and the
  frequencies of its own lowest modes. It was copied once, unchanged, from the set's generator's record of each
  structure (the generator export named in each entry), because the released problems carry the member's effect but
  not its design. `stage2_known.py` (the member table, `stage2_member.csv`) and `article_geometry.py` (the article figure) read it.
