"""Figure 1: the invented response and two noisy estimates of it, from data/response.csv.

The journal's build calls figure(). To look at the figure on its own:

    python code/response.py         (run from the article folder)

MIT license.
"""

import csv

import plotly.graph_objects as go

# Column, legend name, color, line style. The colors are the journal's series colors, in order;
# the line styles are what tells the series apart without color.
SERIES = [
    ('reference', 'Reference', '#2a78d6', 'solid'),
    ('estimate_8_averages', 'Estimate, 8 averages', '#eb6834', 'dot'),
    ('estimate_64_averages', 'Estimate, 64 averages', '#1baf7a', 'dash'),
]


def figure() -> go.Figure:
    with open('data/response.csv', newline='') as file:
        rows = list(csv.DictReader(file))
    frequency = [float(row['frequency_hz']) for row in rows]

    drawn = go.Figure()
    for column, name, color, dash in SERIES:
        drawn.add_scatter(
            x=frequency,
            y=[float(row[column]) for row in rows],
            name=name,
            mode='lines',
            line={'color': color, 'dash': dash, 'width': 2},
            hovertemplate='%{y:.3g} (m/s²)/N',
        )
    drawn.update_layout(
        xaxis={'title': {'text': 'Frequency (Hz)'}, 'hoverformat': '.0f', 'ticksuffix': ''},
        yaxis={'title': {'text': 'Accelerance magnitude ((m/s²)/N)'}, 'type': 'log', 'dtick': 1},
        hovermode='x unified',
        legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'x': 0},
        margin={'l': 76, 'r': 20, 't': 44, 'b': 60},
        height=460,
    )
    return drawn


if __name__ == '__main__':
    figure().show()
