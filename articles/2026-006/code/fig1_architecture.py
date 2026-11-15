"""Figure 1: the three programs, the protocol between them, and the drive path.

Draws from the layout of the Hertzforge repository at commit b587d5a1; reads no data file.
Writes ../figures/fig1_architecture.png. Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
from matplotlib.patches import FancyBboxPatch

from diagram import BLUE, GRAY, GREEN, ORANGE, PURPLE, arrow, box, canvas, save

fig, ax = canvas(9.0, 7.6, 100, 100)

# The shell.
box(ax, 18, 82, 64, 15, 'The shell (TypeScript, Svelte 5)',
    ['Every pixel and no numerics: workspaces, the command palette, the plotting kit.',
     'Draws what a service sends and how the service says to draw it.',
     'Runs in its own desktop window, or in a browser on the same computer.'],
    edge=PURPLE)

# The protocol band.
ax.text(48.5, 76.3, 'protocol sds/1 over WebSocket, on the same computer:\nJSON text frames, binary '
        'array frames, exact version match', fontsize=7.4, ha='center', va='center', color=GRAY,
        style='italic', linespacing=1.5)
arrow(ax, 20, 81.5, 20, 70.5, color=GRAY, both=True)
arrow(ax, 77, 81.5, 77, 70.5, color=GRAY, both=True)

# The analysis service.
box(ax, 2, 44, 42, 26, 'Analysis service (Python)',
    ['The analysis core carried over from',
     'Visual Dynamics.',
     'Spectra, modal fitting, finite elements,',
     'specifications, reports, scripting API.',
     'Converts a finished run into a project.',
     'No route to a drive.'],
    edge=GREEN)

# The drive path outline.
ax.add_patch(FancyBboxPatch((50, 3), 47.5, 68.5, boxstyle='round,pad=0.6,rounding_size=1.5',
                            facecolor='#fff6ef', edgecolor=ORANGE, lw=1.8, ls=(0, (6, 3)),
                            zorder=0))
ax.text(96.5, 5.0, 'drive path', fontsize=8.5, color=ORANGE, ha='right', va='bottom',
        fontweight='bold')

# The control service.
box(ax, 53, 44, 42, 26, 'Control service (Rust)',
    ['Test modules: Random, MIMO Random, Sine,',
     'Mixed Mode, Shock, SRS, MIMO Shock, TWR,',
     'Explorer, Recorder.',
     'Every protection: ceilings, aborts, stops.',
     'Law host: control laws as sandboxed files.',
     'Run writer, off the loop thread.'],
    edge=BLUE)

# The hardware abstraction.
box(ax, 53, 27, 42, 13, 'Hardware abstraction',
    ['What a backend can do, and what it has proven:',
     'who closes the loop, clock domain, abort bound.'],
    edge=BLUE)
arrow(ax, 74, 44, 74, 40.4, color=BLUE)

# Backends.
box(ax, 53, 8, 19.5, 15, 'Simulator',
    ['Simulated structures.', 'Every run marked SIM.'], edge=BLUE, title_size=9)
box(ax, 75.5, 8, 19.5, 15, 'NI-DAQmx',
    ['NI CompactDAQ', 'chassis and modules.'], edge=BLUE, title_size=9)
arrow(ax, 63, 27, 63, 23.4, color=BLUE)
arrow(ax, 85, 27, 85, 23.4, color=BLUE)

# The run folder and its conversion.
box(ax, 2, 8, 42, 26, 'Run folder, then a .hforge project',
    ['Written while the run goes: manifest, channel',
     'table, setup, the law, the log, the streams.',
     'Labeled SIM or HARDWARE, never guessed.',
     'Converted by the analysis service into a',
     '.hforge project: an HDF5 file with a',
     'documented layout.'],
    edge=GRAY)
arrow(ax, 52.6, 47, 44.8, 22, color=GRAY, label='writes', label_xy=(46.6, 36))
arrow(ax, 23, 34.4, 23, 43.6, color=GREEN, label='reads', label_xy=(23, 39))

save(fig, 'fig1_architecture.png')
