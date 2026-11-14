"""Copies the look of hertzforge.com into theme/, from a built checkout of the website.

An article page is frozen with the stylesheet, fonts, header and footer it was built with, so a
later change to the site never re-renders an old version. theme/ is the copy every new build
starts from. Run this when the site's look changes and the journal should follow; versions
already published keep the look they were frozen with.

    python3 scripts/sync-theme.py                      # reads ~/dev/hertzforge-website
    python3 scripts/sync-theme.py /path/to/website

The website must have been built first (`npm run build` there): the stylesheet, the fonts, the
header and the footer are read from its dist/, exactly as the site serves them.
"""

from __future__ import annotations

import datetime
import json
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
THEME = ROOT / 'theme'
PAGE = 'journal/index.html'  # the page whose frame an article wears


def main(argv: list[str]) -> int:
    site = pathlib.Path(argv[0] if argv else pathlib.Path.home() / 'dev' / 'hertzforge-website').expanduser()
    dist = site / 'dist'
    page = dist / PAGE
    if not page.is_file():
        print(f'sync-theme: {page} is missing; build the website first (npm run build)')
        return 1
    html = page.read_text(encoding='utf-8')

    header = re.search(r'<header class="site-header".*?</header>', html, re.S)
    footer = re.search(r'<footer class="site-footer.*?</footer>', html, re.S)
    sheets = re.findall(r'<link rel="stylesheet" href="(/[^"]+)"', html)
    if not (header and footer and sheets):
        print('sync-theme: the header, the footer or the stylesheet was not found in the built page')
        return 1

    if THEME.exists():
        shutil.rmtree(THEME)
    (THEME / 'fonts').mkdir(parents=True)

    css = '\n'.join((dist / href.lstrip('/')).read_text(encoding='utf-8') for href in sheets)
    fonts: dict[str, str] = {}

    def font(match: re.Match[str]) -> str:
        source = match.group(1)
        name = pathlib.PurePosixPath(source).name
        plain = re.sub(r'\.[A-Za-z0-9_-]{6,}(\.woff2)$', r'\1', name)  # drop the build hash
        fonts[source] = plain
        return f'url(fonts/{plain})'

    css = re.sub(r'url\((/[^)]+?\.woff2)\)', font, css)
    left = re.findall(r'url\((?!fonts/|data:|#)[^)]*\)', css)
    if left:
        print(f'sync-theme: the stylesheet points at files this script does not copy: {left[:3]}')
        return 1
    for source, plain in fonts.items():
        shutil.copyfile(dist / source.lstrip('/'), THEME / 'fonts' / plain)

    # Each font family's license travels with the files.
    for package in sorted((site / 'node_modules' / '@fontsource-variable').glob('*')):
        license_file = package / 'LICENSE'
        if license_file.is_file() and any(plain.startswith(package.name) for plain in fonts.values()):
            shutil.copyfile(license_file, THEME / 'fonts' / f'LICENSE-{package.name}.txt')

    (THEME / 'site.css').write_text(css, encoding='utf-8')
    (THEME / 'header.html').write_text(header.group(0) + '\n', encoding='utf-8')
    (THEME / 'footer.html').write_text(footer.group(0) + '\n', encoding='utf-8')
    shutil.copyfile(dist / 'favicon.svg', THEME / 'favicon.svg')

    def git(*args: str) -> str:
        return subprocess.run(['git', '-C', str(site), *args], capture_output=True, text=True, check=False).stdout.strip()

    source = {
        'from': 'the website repository, built',
        'commit': git('rev-parse', 'HEAD'),
        'uncommitted_changes': bool(git('status', '--porcelain')),
        'page': PAGE,
        'taken': datetime.date.today().isoformat(),
        'fonts': sorted(fonts.values()),
    }
    (THEME / 'SOURCE.json').write_text(json.dumps(source, indent=2) + '\n', encoding='utf-8')
    (THEME / 'README.md').write_text(
        '# Theme\n\n'
        "A copy of hertzforge.com's stylesheet, fonts, header and footer, taken from a build of the\n"
        'website repository at the commit in `SOURCE.json`. Every article version is frozen with the\n'
        'copy it was built with. Do not edit these files; refresh them with\n'
        '`python3 scripts/sync-theme.py`.\n\n'
        'The stylesheet, header and footer are under the MIT license, as the website is. The fonts\n'
        'are under the SIL Open Font License 1.1; each family\'s license is in `fonts/`.\n',
        encoding='utf-8',
    )
    print(f'sync-theme: site.css ({len(css)} bytes), {len(fonts)} fonts, header, footer, from {source["commit"][:7]}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
