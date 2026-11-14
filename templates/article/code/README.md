The code that draws each figure from the files in `../data` goes here. It is published under
the MIT license.

A figure named `name` is drawn by `name.py`, which defines one function, `figure()`, returning
a Plotly figure. It reads its data by a path from the article folder:

```python
import csv

import plotly.graph_objects as go


def figure() -> go.Figure:
    with open('data/file.csv', newline='') as file:
        rows = list(csv.DictReader(file))
    drawn = go.Figure()
    drawn.add_scatter(x=[float(r['x']) for r in rows], y=[float(r['a']) for r in rows],
                      name='First series', mode='lines', line={'color': '#2a78d6', 'dash': 'solid', 'width': 2})
    drawn.add_scatter(x=[float(r['x']) for r in rows], y=[float(r['b']) for r in rows],
                      name='Second series', mode='lines', line={'color': '#eb6834', 'dash': 'dash', 'width': 2})
    drawn.update_layout(xaxis={'title': {'text': 'Frequency (Hz)'}}, yaxis={'title': {'text': 'Response (g/N)'}})
    return drawn
```

What the build asks of a figure:

- Every series has a name, and series on the same axes differ by line style (`line.dash`) or
  marker (`marker.symbol`), never by color alone.
- Series colors come from `pipeline/palette.json`, in order. A page in dark reading shows each
  in its dark step.
- No map traces and no pictures loaded from another site: a page makes no outside requests.
- Labels use Unicode and `<sub>` or `<sup>`, not LaTeX between dollar signs.

The build draws the figure twice from this one function: interactive on the page, and as a
static picture for the PDF, for print and for readers with scripts off. NumPy is there for the
function to use. Other files here (a script that prepares the data, for example) travel in the
bundle as they are.

A figure is drawn this way when the article holds no picture of it. If the article supplies
`figures/name.png` itself (a photograph, a drawing, a plot made by other code), that picture is
shown as it is and nothing here is run for it; keep the code that made it here all the same. To
make such a plot interactive, give `name.py` a `figure()` function and remove the picture.
