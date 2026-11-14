#!/usr/bin/env python3
"""Opens a built version in a real browser and checks what only a browser can show.

    python scripts/browser-check.py tests/published/0000-000/v1
    python scripts/browser-check.py tests/published/0000-000/v1 --shots /some/folder

The one-file copy, opened from disk:
    - every network request it makes is listed; anything but the file itself is a failure
    - its figures are drawn by Plotly and answer a drag (zoom) and a pointer (hover)
    - the reading toggle repaints the figure in the other theme's colors
    - with scripts switched off, the text is all there and each figure shows its static picture

The article page, served the way the site serves it:
    - it asks only its own server for anything
    - it reads the article's record and builds the version selector from it
    - an older version says that a later one exists

Uses the Chrome on this machine, driven through the DevTools protocol by choreographer (which
kaleido already brings). Run inside the environment scripts/setup.sh makes.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import functools
import http.server
import json
import pathlib
import sys
import threading

import choreographer

RESULTS: list[tuple[bool, str]] = []


def check(what: str, ok: bool, detail: str = '') -> None:
    RESULTS.append((bool(ok), what))
    print(f'  {"ok  " if ok else "FAIL"}  {what}' + (f'  [{detail}]' if detail else ''))


async def evaluate(tab, expression: str):
    answer = await tab.send_command('Runtime.evaluate', {'expression': expression, 'awaitPromise': True, 'returnByValue': True})
    result = answer.get('result', {})
    if 'exceptionDetails' in result:
        raise RuntimeError(result['exceptionDetails'].get('exception', {}).get('description', 'script error'))
    return result.get('result', {}).get('value')


async def open_page(browser, url: str, *, width: int = 1280, height: int = 1400, dark: bool = False, scripts: bool = True):
    """A new tab on `url`, with every request it makes recorded from the first."""
    tab = await browser.create_tab('about:blank')
    requests: list[str] = []

    async def on_request(message) -> None:
        requests.append(message['params']['request']['url'])

    tab.subscribe('Network.requestWillBeSent', on_request)
    for domain in ('Network', 'Page', 'Runtime'):
        await tab.send_command(f'{domain}.enable')
    await tab.send_command('Network.setCacheDisabled', {'cacheDisabled': True})
    await tab.send_command('Emulation.setDeviceMetricsOverride',
                           {'width': width, 'height': height, 'deviceScaleFactor': 1, 'mobile': width < 600})
    await tab.send_command('Emulation.setEmulatedMedia',
                           {'features': [{'name': 'prefers-color-scheme', 'value': 'dark' if dark else 'light'}]})
    if not scripts:
        await tab.send_command('Emulation.setScriptExecutionDisabled', {'value': True})
    loaded = tab.subscribe_once('Page.loadEventFired')
    await tab.send_command('Page.navigate', {'url': url})
    await asyncio.wait_for(loaded, 60)
    await asyncio.sleep(1.5)  # figures draw, fonts settle, the record is read
    return tab, requests


async def screenshot(tab, path: pathlib.Path) -> None:
    size = await evaluate(tab, '({w: document.documentElement.clientWidth, h: document.documentElement.scrollHeight})')
    shot = await tab.send_command('Page.captureScreenshot', {
        'format': 'png', 'captureBeyondViewport': True,
        'clip': {'x': 0, 'y': 0, 'width': size['w'], 'height': min(size['h'], 12000), 'scale': 1},
    })
    path.write_bytes(base64.b64decode(shot['result']['data']))


FIGURE = "document.querySelector('.hf-figure .hf-plot')"


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:
        pass


async def check_interactive(tab, shots: pathlib.Path | None) -> None:
    """The first figure the build drew: Plotly drew it, and it answers a drag, a pointer and the reading toggle."""
    state = await evaluate(tab, f"""(() => {{
      const gd = {FIGURE};
      const holder = gd.closest('.hf-figure');
      return {{
        plotly: typeof Plotly === 'object' ? Plotly.version : null,
        drawn: gd.classList.contains('js-plotly-plot'),
        traces: gd.data ? gd.data.length : 0,
        written: JSON.parse(holder.querySelector('.hf-spec').textContent).data.length,
        stillHidden: getComputedStyle(holder.querySelector('.hf-static')).display === 'none',
      }};
    }})()""")
    check('Plotly is in the file and drew the figure', state['plotly'] and state['drawn'], f'plotly.js {state["plotly"]}')
    check('every series written into the page is drawn', state['traces'] == state['written'] > 0, f'{state["traces"]} series')
    check('the static picture gives way to the interactive figure', state['stillHidden'])

    # A drag across the plot zooms it.
    box = await evaluate(tab, f"""(() => {{
      const gd = {FIGURE};
      gd.scrollIntoView({{block: 'center', behavior: 'instant'}});
      const r = gd.querySelector('.nsewdrag').getBoundingClientRect();
      return {{x: r.left, y: r.top, w: r.width, h: r.height, range: gd._fullLayout.xaxis.range.slice()}};
    }})()""")
    y = box['y'] + box['h'] * 0.5
    x1, x2 = box['x'] + box['w'] * 0.30, box['x'] + box['w'] * 0.55
    await tab.send_command('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': x1, 'y': y})
    await tab.send_command('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': x1, 'y': y, 'button': 'left', 'buttons': 1, 'clickCount': 1})
    for step in range(1, 9):
        await tab.send_command('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': x1 + (x2 - x1) * step / 8, 'y': y, 'button': 'left', 'buttons': 1})
    await tab.send_command('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x2, 'y': y, 'button': 'left', 'buttons': 0, 'clickCount': 1})
    await asyncio.sleep(0.8)
    zoomed = await evaluate(tab, f'{FIGURE}._fullLayout.xaxis.range.slice()')
    before, after = box['range'][1] - box['range'][0], zoomed[1] - zoomed[0]
    check('a drag across the figure zooms it', 0 < after < before * 0.6,
          f'x axis {box["range"][0]:.0f} to {box["range"][1]:.0f} became {zoomed[0]:.0f} to {zoomed[1]:.0f}')

    # A pointer over the plot shows the values under it.
    await tab.send_command('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': box['x'] + box['w'] * 0.4, 'y': y})
    await tab.send_command('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': box['x'] + box['w'] * 0.42, 'y': y + 2})
    await asyncio.sleep(0.6)
    hover = await evaluate(tab, f"({FIGURE}.querySelector('.hoverlayer')?.textContent || '').trim()")
    check('a pointer over the figure shows the values under it', len(hover) > 10, hover[:70])
    if shots:
        await screenshot(tab, shots / 'single_zoomed_hover.png')

    # The reading toggle repaints the figure.
    colors = ("(() => { const gd = %s; const t = gd._fullData[0]; return {text: gd._fullLayout.font.color, "
              "line: (t.mode || '').includes('lines') ? t.line.color : t.marker.color}; })()" % FIGURE)
    light = await evaluate(tab, colors)
    await evaluate(tab, "document.querySelector('.theme-toggle').click()")
    await asyncio.sleep(0.8)
    dark = await evaluate(tab, colors)
    check('the reading toggle repaints the figure for dark reading', light['text'] != dark['text'] and light['line'] != dark['line'],
          f'text {light["text"]} to {dark["text"]}; first series {light["line"]} to {dark["line"]}')
    if shots:
        await screenshot(tab, shots / 'single_dark.png')


async def check_single(browser, single: pathlib.Path, shots: pathlib.Path | None) -> None:
    print(f'The one-file copy, opened from disk: {single.name}')
    url = single.resolve().as_uri()
    tab, requests = await open_page(browser, url)

    elsewhere = [r for r in requests if not r.startswith(('data:', 'blob:')) and r != url]
    check('it makes no network request (the file itself, and data written into it, are all it loads)',
          not elsewhere and url in requests,
          f'{len(requests)} requests: 1 file, {sum(r.startswith("data:") for r in requests)} data' if not elsewhere else '; '.join(elsewhere[:4]))

    drawn = await evaluate(tab, "document.querySelectorAll('.hf-figure .hf-plot').length")
    given = await evaluate(tab, "document.querySelectorAll('.hf-figure-given').length")
    if drawn:
        await check_interactive(tab, shots)
    else:
        check('it has no figure for the build to make interactive', True, f'{given} pictures supplied with the article')
    if given:
        pictures = await evaluate(tab, """[...document.querySelectorAll('.hf-figure-given .hf-static')].map((img) =>
          img.complete && img.naturalWidth > 0 && img.alt.length > 20 && img.src.startsWith('data:'))""")
        check('every picture supplied with the article is in the file, with alternative text', all(pictures), f'{len(pictures)} pictures')
    fonts = await evaluate(tab, "[...document.fonts].filter((f) => f.status === 'loaded').length")
    check("the site's fonts load from inside the file", fonts > 0, f'{fonts} faces')
    await tab.close()

    # With scripts off: the text, and each figure's picture.
    tab, requests = await open_page(browser, url, scripts=False)
    plain = await evaluate(tab, """(() => {
      const stills = [...document.querySelectorAll('.hf-figure .hf-static')];
      const plots = [...document.querySelectorAll('.hf-figure .hf-plot')];
      return {
        figures: stills.length,
        pictures: stills.every((img) => img.complete && img.naturalWidth > 0 && getComputedStyle(img).display !== 'none' && img.alt.length > 20),
        plotsShown: plots.some((plot) => getComputedStyle(plot).display !== 'none'),
        words: document.querySelector('.hf-prose').innerText.split(/\\s+/).length,
        sections: document.querySelectorAll('.hf-prose h2').length,
      };
    })()""")
    if plain['figures']:
        check('with scripts off, every figure shows its picture, with alternative text',
              plain['pictures'] and not plain['plotsShown'], f'{plain["figures"]} figures')
    check('with scripts off, the text reads in full', plain['words'] > 300 and plain['sections'] >= 8,
          f'{plain["words"]} words, {plain["sections"]} sections')
    elsewhere = [r for r in requests if not r.startswith(('data:', 'blob:')) and r != url]
    check('with scripts off, it still makes no network request', not elsewhere)
    if shots:
        await screenshot(tab, shots / 'single_scripts_off.png')
    await tab.close()


async def check_page(browser, version: pathlib.Path, shots: pathlib.Path | None) -> None:
    article = version.parent
    record = json.loads((article / 'record.json').read_text(encoding='utf-8'))
    here = int(version.name[1:])
    handler = functools.partial(Quiet, directory=str(article.parent))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_address[1]}'
    url = f'{origin}/{article.name}/{version.name}/'
    print(f'The article page, served as the site serves it: /{article.name}/{version.name}/')
    try:
        tab, requests = await open_page(browser, url, height=1800)
        elsewhere = [r for r in requests if not r.startswith((origin, 'data:', 'blob:'))]
        check('it asks only its own server for anything', not elsewhere, '; '.join(elsewhere[:4]) or f'{len(requests)} requests')
        check("it reads the article's record", f'{origin}/{article.name}/record.json' in requests)
        state = await evaluate(tab, """(() => {
          const select = document.getElementById('hf-version-select');
          const notice = document.querySelector('.hf-notlatest');
          return {
            options: select ? [...select.options].map((o) => o.textContent) : [],
            chosen: select ? select.value : null,
            notice: notice && !notice.hidden ? notice.innerText.replace(/\\s+/g, ' ') : '',
            status: document.querySelector('.hf-status-name').textContent,
            drawable: document.querySelectorAll('.hf-figure .hf-plot').length,
            drawn: document.querySelectorAll('.hf-figure .js-plotly-plot').length,
            doctype: document.compatMode,
          };
        })()""")
        check('the version selector lists every version in the record', len(state['options']) == len(record['versions']) and state['chosen'] == str(here),
              ' | '.join(state['options']))
        if here < record['latest']:
            check('an older version says a later one exists', f'version {record["latest"]}' in state['notice'], state['notice'][:90])
        else:
            check('the latest version carries no notice of a later one', state['notice'] == '')
        check('the banner shows the status in the record', state['status'] == record['status'], state['status'])
        if state['drawable']:
            check('every figure the build drew is interactive on the page', state['drawn'] == state['drawable'], f'{state["drawn"]} figures')
        layout = await evaluate(tab, """(() => {
          const nav = document.querySelector('.hf-contents');
          const prose = document.querySelector('.hf-prose').getBoundingClientRect();
          return {
            contents: nav ? nav.querySelectorAll('a').length : 0,
            beside: nav ? nav.getBoundingClientRect().left >= prose.right : false,
            open: nav ? nav.querySelector('details').open : false,
            wide: document.documentElement.scrollWidth > document.documentElement.clientWidth,
          };
        })()""")
        if layout['contents']:
            check('the contents list sits open beside the text on a wide screen', layout['beside'] and layout['open'],
                  f'{layout["contents"]} entries')
        check('the page does not scroll sideways on a wide screen', not layout['wide'])
        check('the page is laid out in standards mode', state['doctype'] == 'CSS1Compat')
        if shots:
            await screenshot(tab, shots / f'page_v{here}_light.png')
        await tab.close()
        tab, _ = await open_page(browser, url, width=390, height=900)
        phone = await evaluate(tab, """(() => {
          const frames = [...document.querySelectorAll('.table-wrap')];
          const nav = document.querySelector('.hf-contents details');
          return {
            wide: document.documentElement.scrollWidth > document.documentElement.clientWidth,
            tables: frames.length,
            scrolling: frames.filter((f) => f.scrollWidth > f.clientWidth + 1).length,
            escaped: frames.filter((f) => f.getBoundingClientRect().right > document.documentElement.clientWidth + 1).length,
            contentsClosed: nav ? !nav.open : null,
          };
        })()""")
        check('on a phone the page does not scroll sideways', not phone['wide'])
        if phone['tables']:
            check('on a phone every table stays inside its own frame, and a wide one scrolls there',
                  phone['escaped'] == 0, f'{phone["tables"]} tables, {phone["scrolling"]} scrolling in their frames')
        if phone['contentsClosed'] is not None:
            check('on a phone the contents list is closed above the text until it is asked for', phone['contentsClosed'])
        if shots:
            await screenshot(tab, shots / f'page_v{here}_phone.png')
        await tab.close()
        if shots:
            tab, _ = await open_page(browser, url, dark=True)
            await screenshot(tab, shots / f'page_v{here}_dark.png')
            await tab.close()
    finally:
        server.shutdown()


async def main(version: pathlib.Path, shots: pathlib.Path | None) -> int:
    stem = f'{version.parent.name}-{version.name}'
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    async with choreographer.Browser(headless=True) as browser:
        await check_single(browser, version / f'{stem}.html', shots)
        await check_page(browser, version, shots)
    failed = [what for ok, what in RESULTS if not ok]
    print(f'browser-check: {len(RESULTS) - len(failed)} of {len(RESULTS)} checks passed')
    return 1 if failed else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('version', help='a built version folder, such as tests/published/0000-000/v1')
    parser.add_argument('--shots', help='also save screenshots into this folder')
    arguments = parser.parse_args()
    sys.exit(asyncio.run(main(pathlib.Path(arguments.version).resolve(), pathlib.Path(arguments.shots) if arguments.shots else None)))
