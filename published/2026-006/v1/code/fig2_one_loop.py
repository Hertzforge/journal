"""Figure 2: one control loop, what the control law sees and what the core keeps.

Draws from docs/control-law-spec.md and docs/drive-path.md at commit b587d5a1; reads no data file.
Writes ../figures/fig2_one_loop.png. Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
from diagram import BLUE, GRAY, ORANGE, PURPLE, arrow, box, canvas, save

fig, ax = canvas(9.0, 6.4, 100, 100)

box(ax, 1, 58, 22, 38, 'Measure',
    ['Control and limit', 'accelerometers.', 'Spectra, FRF and', 'coherence estimated', 'by the core.'],
    edge=BLUE)

box(ax, 28, 58, 30, 38, 'Control law file',
    ['A WebAssembly component,', 'run in a sandbox:',
     'no files, no network,', 'a clock that does not move,', 'fixed random seeds,',
     'a memory cap and a time', 'budget per call.',
     'Returns a drive request.'],
    edge=PURPLE)

box(ax, 63, 58, 35, 38, 'Core checks the request',
    ['Right size, finite, a valid',
     'spectral matrix (small negative',
     'eigenvalues repaired, large ones',
     'refused). A failed call holds',
     'the previous drive; three in a',
     'row end the run with a',
     'controlled stop.'],
    edge=BLUE)

box(ax, 63, 6, 35, 44, 'Core protections, every law',
    ['Drive ceiling and drive abort.',
     'Cap on change per loop.',
     'Limit notching.',
     'Envelope alarm and abort.',
     'Divergence, kinematic and',
     'overload checks.',
     'May reduce a request,',
     'never make it more aggressive.'],
    edge=ORANGE, lw=1.8)

box(ax, 28, 6, 30, 44, 'Drive out',
    ['The core synthesizes the',
     'drive time history and',
     'plays it on the output',
     'channels.',
     'A raw-input watchdog on the',
     'loop thread trips the',
     'emergency stop, whatever',
     'the law did.'],
    edge=BLUE)

box(ax, 1, 6, 22, 44, 'Recorded',
    ['Which law ran: name,', 'version, SHA-256 of', 'the file, parameters.',
     'Where the module', 'records it, every', 'call\'s inputs and', 'outputs.',
     'By a writer thread,', 'off the loop thread.'],
    edge=GRAY)

arrow(ax, 23.6, 77, 27.4, 77, color=BLUE)
arrow(ax, 58.6, 77, 62.4, 77, color=PURPLE)
arrow(ax, 80.5, 57.4, 80.5, 50.6, color=BLUE)
arrow(ax, 62.4, 28, 58.6, 28, color=ORANGE)
arrow(ax, 27.4, 28, 23.6, 28, color=GRAY)
arrow(ax, 30, 50.6, 12, 57.4, color=BLUE, ls=(0, (3, 2)), label='next loop',
      label_xy=(18.5, 53.2))

save(fig, 'fig2_one_loop.png')
