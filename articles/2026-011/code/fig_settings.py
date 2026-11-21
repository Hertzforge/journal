"""The three laws of this article at their other settings, on the 6 x 12 and 6 x 6 systems, linear
structures: the error at the held-out gauges and the level, for each law as built (its defaults), as
tuned, and in the other forms that were run (the published form of the two independent drive laws,
the open form of the nearly independent law, the independent law with the target weighting). Median
over structures 0 to 9, with a line from the first to the third quartile. From
../data/study_settings_scores.csv (written by law_results.py).

Copyright 2026 Kevin Cross and Norman Hunter. MIT license.
"""
from style import BLUE, GREEN, NEW, ORANGE, PURPLE, TEXT, YELLOW, one, plt, rows, save

SETTINGS = [('published', 'Published form', YELLOW, '...'), ('default', 'As built (defaults)', ORANGE, '///'),
            ('tuned', 'Tuned', GREEN, 'xxx'), ('open', 'Open form', BLUE, '\\\\\\'), ('weighted', 'Target weighting on', PURPLE, '+++')]
SYSTEMS = (('more_controls', '6 x 12 system'), ('equal', '6 x 6 system'))
t = rows('study_settings_scores.csv')
fig, axes = plt.subplots(2, 2, figsize=(10, 6.2), sharex=True, sharey='row')
for row, (key, label) in zip(axes, (('held_out', 'Error at the held-out gauges, dB\n(lower is better)'),
                                    ('level', 'Level error, dB\n(zero is on level)'))):
    for ax, (grp, title) in zip(row, SYSTEMS):
        ticks, names, seen = [], [], set()
        x = 0.0
        for law in NEW:
            start = x
            for a, name, c, h in SETTINGS:
                r = one(t, systems=grp, structure_kind='none', law=law, settings=a)
                if r is None:
                    continue
                ax.bar(x, float(r[key + '_db']), width=0.8, color=c, hatch=h, edgecolor='white', linewidth=0.5,
                       label=name if a not in seen else None)
                ax.plot([x, x], [float(r[key + '_q1']), float(r[key + '_q3'])], color=TEXT, lw=1.1)
                seen.add(a)
                x += 1
            if x > start:
                ticks.append((start + x - 1) / 2); names.append(law)
                x += 0.8
        ax.set_xticks(ticks)
        ax.set_xticklabels(names, fontsize=8)
        ax.grid(axis='x', visible=False)
        if key == 'held_out':
            ax.set_title(title, fontsize=9)
        else:
            ax.axhline(0, color=TEXT, lw=0.8)
    row[0].set_ylabel(label)
fig.tight_layout()
handles, labels = axes[0][0].get_legend_handles_labels()
for ax in (axes[0][1],):
    for h, l in zip(*ax.get_legend_handles_labels()):
        if l not in labels:
            handles.append(h); labels.append(l)
fig.legend(handles, labels, fontsize=8, ncol=len(labels), loc='lower center', bbox_to_anchor=(0.5, 1.0))
save(fig, 'fig_settings.png')
