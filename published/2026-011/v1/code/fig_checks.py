"""What the controller's default checks did with each law at its defaults: of the runs started with
the checks at their defaults, the share that ran to the end and the share a check stopped. Structures
0 to 4 (the structures run with the checks at their defaults first), all five systems, linear and
level-dependent structures together. From
../data/study_outcomes.csv (written by law_results.py).

Copyright 2026 Kevin Cross and Norman Hunter. MIT license.
"""
from style import BLUE, LAWS, MUTED, NEW, ORANGE, one, plt, rows, save

t = rows('study_outcomes.csv')
fig, ax = plt.subplots(figsize=(7.2, 3.6))
for i, law in enumerate(LAWS):
    r = one(t, law=law, settings='default')
    if r is None:
        continue
    n = int(r['runs_checks_default'])
    done = 100.0 * int(r['completed']) / n
    new = law in NEW
    ax.barh(i, done, color=ORANGE if new else BLUE, hatch='///' if new else None, edgecolor='white', linewidth=0.5,
            label=None)
    ax.barh(i, 100.0 - done, left=done, color='#dfe5ec', hatch='xx', edgecolor='white', linewidth=0.5)
    ax.text(101, i, f"{int(r['completed'])} of {n}", va='center', fontsize=7.5, color=MUTED)
ax.set_yticks(range(len(LAWS)))
ax.set_yticklabels(LAWS, fontsize=8)
ax.invert_yaxis()
ax.set_xlim(0, 118)
ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xlabel('Runs that finished with the checks at their defaults, percent\n(cross-hatched grey: stopped by a check)')
ax.grid(axis='y', visible=False)
fig.tight_layout()
save(fig, 'fig_checks.png')
