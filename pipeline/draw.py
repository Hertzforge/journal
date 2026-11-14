"""Draws one figure of an article from its code and data.

    python draw.py ARTICLE_DIR NAME

Runs `ARTICLE_DIR/code/NAME.py`, which must define `figure()` returning a Plotly figure drawn
from files under `ARTICLE_DIR/data/`. Writes two files into `ARTICLE_DIR/figures/`:

    NAME.json   the figure, for the interactive page
    NAME.png    the same figure as a static image, for the PDF, for print and for readers with
                scripts off

The journal's build runs this for every figure, and a copy travels in every article's data and
code bundle, so a reader can regenerate each figure the same way.

A figure is refused when its series cannot be told apart without color, or when it would fetch
anything from outside the page.

Needs plotly and kaleido (and a Chrome for kaleido). MIT license.
"""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent

#: Trace types that fetch map tiles or outlines from another site when drawn.
FETCHING = frozenset({
    'scattergeo', 'choropleth', 'scattermapbox', 'choroplethmapbox', 'densitymapbox',
    'scattermap', 'choroplethmap', 'densitymap',
})

#: Trace types drawn as lines or markers, whose series must differ by more than color.
LINE_LIKE = frozenset({'scatter', 'scattergl', 'scatterpolar', 'scatterpolargl', 'scatter3d', 'scatterternary'})


def load(article: pathlib.Path, name: str):
    path = article / 'code' / f'{name}.py'
    if not path.is_file():
        raise SystemExit(f'draw: {path} does not exist')
    spec = importlib.util.spec_from_file_location(f'figure_{name}', path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(module)
    if not callable(getattr(module, 'figure', None)):
        raise SystemExit(f'draw: {path} must define figure(), returning a Plotly figure')
    return module.figure()


def style_of(trace: dict) -> tuple:
    """What tells a line or marker series apart besides its color."""
    mode = trace.get('mode') or 'lines'
    line = trace.get('line') or {}
    marker = trace.get('marker') or {}
    dash = line.get('dash', 'solid') if 'lines' in mode else None
    symbol = marker.get('symbol', 'circle') if 'markers' in mode else None
    return (dash, str(symbol))


def problems(spec: dict) -> list[str]:
    found = []
    traces = spec.get('data', [])
    for trace in traces:
        if trace.get('type', 'scatter') in FETCHING:
            found.append(f'a {trace.get("type")} trace fetches map data from another site; '
                         'an article page makes no outside requests')
    for image in (spec.get('layout', {}).get('images') or []):
        if str(image.get('source', '')).startswith(('http:', 'https:', '//')):
            found.append('a layout image is loaded from another site; put the file in the article')

    # Plotly typesets a label written between dollar signs with MathJax, which no page loads.
    def texts(value):
        if isinstance(value, dict):
            for inner in value.values():
                yield from texts(inner)
        elif isinstance(value, list):
            for inner in value[:50]:
                yield from texts(inner)
        elif isinstance(value, str):
            yield value

    layout_and_names = [spec.get('layout', {}), [{k: v for k, v in t.items() if k in ('name', 'text', 'hovertemplate')} for t in traces]]
    if any(len(text) > 2 and text.startswith('$') and text.endswith('$') for text in texts(layout_and_names)):
        found.append('a label is written as LaTeX between dollar signs, which needs MathJax; the page loads none. '
                     'Write it with Unicode letters and <sub> or <sup>')

    # Series drawn on the same axes must differ by line style or marker, not by color alone.
    groups: dict[tuple, list[dict]] = {}
    for trace in traces:
        if trace.get('type', 'scatter') in LINE_LIKE and trace.get('visible', True) is not False:
            axes = (trace.get('xaxis', 'x'), trace.get('yaxis', 'y'), trace.get('subplot'), trace.get('scene'))
            groups.setdefault(axes, []).append(trace)
    for group in groups.values():
        seen: dict[tuple, str] = {}
        for number, trace in enumerate(group, 1):
            style = style_of(trace)
            label = str(trace.get('name') or f'series {number}')
            if style in seen:
                found.append(f'"{label}" and "{seen[style]}" differ only by color; give one a '
                             'different line style (line.dash) or marker (marker.symbol)')
            else:
                seen[style] = label
        if len(group) > 1 and any(not trace.get('name') for trace in group):
            found.append('a series has no name; every series needs one for the legend')
    return found


def static_figure(figure, palette: dict):
    """The figure as it prints: a white ground, dark text, quiet grid lines."""
    import plotly.graph_objects as go

    look = palette['static']
    printed = go.Figure(figure)
    printed.update_layout(
        paper_bgcolor=look['surface'], plot_bgcolor=look['surface'],
        font={'color': look['text'], 'family': look['font'], 'size': 14},
        legend={'bgcolor': 'rgba(0,0,0,0)'},
    )
    axis = {'gridcolor': look['grid'], 'linecolor': look['axis'], 'zerolinecolor': look['axis'],
            'tickcolor': look['axis'], 'showline': True}
    printed.update_xaxes(**axis)
    printed.update_yaxes(**axis)
    return printed, look


def render(figure, width: int, height: int, scale: int) -> bytes:
    """The figure as a PNG, rendered by the Chrome on this machine from local files only: the
    plotly.js that the plotly package carries, and no MathJax. (Left to its defaults the renderer
    fetches MathJax from another site for every picture, which a closed network cannot do.)"""
    import time

    import kaleido
    import plotly

    script = pathlib.Path(plotly.__file__).parent / 'package_data' / 'plotly.min.js'
    options = {'format': 'png', 'width': width, 'height': height, 'scale': scale}
    last: Exception | None = None
    for attempt in range(3):  # a browser that is slow to start is given two more tries
        try:
            return kaleido.calc_fig_sync(figure, opts=options, kopts={'plotlyjs': script, 'mathjax': False})
        except Exception as problem:  # noqa: BLE001 - whatever the browser raised, try again
            last = problem
            time.sleep(1 + attempt)
    raise SystemExit(f'draw: the static picture could not be rendered: {last}')


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    article = pathlib.Path(argv[0]).resolve()
    name = argv[1]
    os.chdir(article)  # figure code reads data/... relative to the article

    import plotly.graph_objects as go

    figure = load(article, name)
    if not isinstance(figure, go.Figure):
        raise SystemExit(f'draw: figure() in code/{name}.py must return a plotly.graph_objects.Figure')

    spec = json.loads(figure.to_json())
    found = problems(spec)
    if found:
        for line in found:
            print(f'draw: {name}: {line}')
        return 1

    palette_file = next((p for p in (HERE / 'palette.json', article / 'palette.json') if p.is_file()), None)
    if palette_file is None:
        raise SystemExit('draw: palette.json is missing beside draw.py')
    palette = json.loads(palette_file.read_text(encoding='utf-8'))

    out = article / 'figures'
    out.mkdir(exist_ok=True)
    # Sorted keys and no spaces: the same figure always writes the same file.
    (out / f'{name}.json').write_text(json.dumps(spec, sort_keys=True, separators=(',', ':')) + '\n', encoding='utf-8')

    printed, look = static_figure(figure, palette)
    height = spec.get('layout', {}).get('height') or look['height']
    (out / f'{name}.png').write_bytes(render(printed, look['width'], height, look['scale']))
    print(f'draw: {name}: figures/{name}.json, figures/{name}.png')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
