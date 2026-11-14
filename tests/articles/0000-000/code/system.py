"""Draws figures/system.png: a drawing of a two-mass chain, of the kind this sample invents.

This picture is supplied with the article as it is; the journal's build does not draw it. It is
here to test a figure that is a picture only. To draw it again:

    python code/system.py           (run from the article folder)

Needs plotly and kaleido (and a Chrome for kaleido). MIT license.
"""

import pathlib

import kaleido
import plotly
import plotly.graph_objects as go

INK = '#10161d'
BLUE = '#2a78d6'


def spring(x0: float, x1: float, y: float, turns: int = 6, height: float = 0.16) -> tuple[list, list]:
    """A zigzag from x0 to x1."""
    lead = (x1 - x0) * 0.15
    xs, ys = [x0, x0 + lead], [y, y]
    step = (x1 - x0 - 2 * lead) / (2 * turns)
    for i in range(2 * turns):
        xs.append(x0 + lead + (i + 0.5) * step)
        ys.append(y + (height if i % 2 == 0 else -height))
    return xs + [x1 - lead, x1], ys + [y, y]


def drawing() -> go.Figure:
    drawn = go.Figure()
    for x0, x1 in ((0.0, 1.6), (2.8, 4.4)):
        xs, ys = spring(x0, x1, 0.0)
        drawn.add_scatter(x=xs, y=ys, mode='lines', line={'color': INK, 'width': 2}, hoverinfo='skip')
    drawn.add_shape(type='line', x0=0, x1=0, y0=-0.9, y1=0.9, line={'color': INK, 'width': 4})
    for x0, label in ((1.6, 'm<sub>1</sub>'), (4.4, 'm<sub>2</sub>')):
        drawn.add_shape(type='rect', x0=x0, x1=x0 + 1.2, y0=-0.6, y1=0.6, line={'color': BLUE, 'width': 2},
                        fillcolor='rgba(42,120,214,0.10)')
        drawn.add_annotation(x=x0 + 0.6, y=0, text=label, showarrow=False, font={'size': 22, 'color': INK})
    for x, label in ((0.8, 'k<sub>1</sub>, c<sub>1</sub>'), (3.6, 'k<sub>2</sub>, c<sub>2</sub>')):
        drawn.add_annotation(x=x, y=0.48, text=label, showarrow=False, font={'size': 17, 'color': INK})
    # The force acts along the chain, on the first mass.
    drawn.add_annotation(x=2.8, y=0.95, ax=1.6, ay=0.95, xref='x', yref='y', axref='x', ayref='y', text='',
                         showarrow=True, arrowhead=2, arrowsize=1.4, arrowwidth=2.4, arrowcolor='#eb6834')
    drawn.add_annotation(x=2.2, y=1.3, text='f(t)', showarrow=False, font={'size': 18, 'color': INK})
    drawn.update_layout(
        width=800, height=330, showlegend=False, paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
        margin={'l': 20, 'r': 20, 't': 10, 'b': 10}, font={'family': 'Arial, Helvetica, sans-serif'},
        xaxis={'visible': False, 'range': [-0.4, 6.0]}, yaxis={'visible': False, 'range': [-1.3, 1.9], 'scaleanchor': 'x'},
    )
    return drawn


if __name__ == '__main__':
    script = pathlib.Path(plotly.__file__).parent / 'package_data' / 'plotly.min.js'
    picture = kaleido.calc_fig_sync(drawing(), opts={'format': 'png', 'width': 800, 'height': 330, 'scale': 2},
                                    kopts={'plotlyjs': script, 'mathjax': False})
    pathlib.Path('figures').mkdir(exist_ok=True)
    pathlib.Path('figures/system.png').write_bytes(picture)
    print('wrote figures/system.png')
