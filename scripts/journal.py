#!/usr/bin/env python3
"""The journal's build: turns one article's source into the four outputs of one version, and
freezes them.

    scripts/publish ARTICLE_DIR              build the version the article's front matter names
    scripts/publish ARTICLE_DIR --rebuild    the same, replacing a test build (never a real one)
    python scripts/journal.py record ID      rewrite an article's record after its review status changes
    python scripts/journal.py verify         check every frozen version against its manifest
    python scripts/journal.py selftest       build the sample twice and prove the freeze rule

What a build writes, into published/<id>/v<n>/:

    index.html              the article page, in the site's style: the version of record
    <id>-v<n>.html          the same article as one file that opens offline, figures interactive
    <id>-v<n>.pdf           the static print copy, from the same source
    <id>-v<n>-bundle.zip    the data behind every figure and the code that draws it
    <id>-v<n>.bib, .ris     the citation, for reference managers
    assets/, figures/, data/, code/   what the page itself loads and links
    version.json            what this version is and what it was built with
    MANIFEST.sha256         the hash of every file above

The freeze rule: a version folder is written once. A later build never rewrites it, whatever has
changed in the site's style, the build or a library; a change to an article is a new version in a
new folder. `verify` proves it at any time.

The conversion is Quarto's (Markdown, cross-references, citations, MathML, embedding, Typst).
Everything the journal's own rules decide (the parts of the page and their order, the citation
tags, the freeze) is done here. Run inside the environment scripts/setup.sh makes.
"""

from __future__ import annotations

import argparse
import base64
import datetime
import html
import html.parser
import json
import math
import mimetypes
import os
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile

import yaml

from freeze import sha256, tree, verify_version, version_folders, write_manifest

ROOT = pathlib.Path(__file__).resolve().parent.parent
PIPELINE = ROOT / 'pipeline'
THEME = ROOT / 'theme'
REAL_PUBLISHED = ROOT / 'published'
REAL_REVIEWS = ROOT / 'reviews'
WORK = ROOT / '_build' / 'work'
SAMPLE = ROOT / 'tests' / 'articles' / '0000-000'
SAMPLE_REVISION = ROOT / 'tests' / 'revision' / '0000-000'
TEST_PUBLISHED = ROOT / 'tests' / 'published'
TEST_REVIEWS = ROOT / 'tests' / 'reviews'

BODY_MARK = '<!--hf:body-->'
SOURCE = 'article.qmd'

TYPES = ('Research Article', 'Method Note', 'Negative Result', 'Proposed Standard', 'Practice Note', 'Survey', 'Perspective')
EVIDENCE = {'simulator': 'Simulator', 'bench': 'Bench', 'hardware': 'Hardware'}
CREDIT_ROLES = (
    'Conceptualization', 'Methodology', 'Software', 'Validation', 'Formal analysis', 'Investigation',
    'Resources', 'Data curation', 'Writing: original draft', 'Writing: review and editing',
    'Visualization', 'Supervision', 'Project administration', 'Funding acquisition',
)
#: The sections every article ends with, in this order. The contribution statement of a
#: co-authored article is written by the build, from each author's roles, ahead of them.
CLOSING = ('How This Was Made', 'Acknowledgments', 'References')
STATUS = {
    'Review open': ('review-open', 'Published; reviews and comments are welcome.'),
    'Reviewed': ('reviewed', 'Reviewed in public; the authors have answered or revised. Review stays open.'),
    'Retracted': ('retracted', 'This article has been retracted. It is kept here, with the reason.'),
}
USE = ('Methods are published for research. Anyone who applies one to a test is responsible for '
       'protecting the equipment and the article under test.')

esc = html.escape


class Refused(Exception):
    """A rule of the journal says no. The message is for the person at the keyboard."""


# ---------------------------------------------------------------- small helpers


def iso(value: object, what: str) -> str:
    if isinstance(value, datetime.datetime):
        value = value.date()
    if isinstance(value, datetime.date):
        return value.isoformat()
    try:
        return datetime.date.fromisoformat(str(value)).isoformat()
    except ValueError:
        raise Refused(f'{what} must be a date written YYYY-MM-DD, not {value!r}') from None


def slug(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def orcid_id(value: object, who: str) -> str | None:
    """The sixteen characters of an ORCID iD, checked against its own check digit."""
    if not value:
        return None
    match = re.fullmatch(r'(?:https?://orcid\.org/)?(\d{4}-\d{4}-\d{4}-\d{3}[\dX])', str(value).strip())
    if not match:
        raise Refused(f"{who}'s ORCID iD is not of the form 0000-0000-0000-0000: {value!r}")
    digits = match.group(1).replace('-', '')
    total = 0
    for character in digits[:-1]:
        total = (total + int(character)) * 2
    check = (12 - total % 11) % 11
    if ('X' if check == 10 else str(check)) != digits[-1]:
        raise Refused(f"{who}'s ORCID iD {match.group(1)} fails its check digit; it has a typing error")
    return match.group(1)


def human_size(size: int) -> str:
    if size >= 1_000_000:
        return f'{size / 1_000_000:.1f} MB'
    return f'{max(1, round(size / 1000))} kB'


def run(command: list[str], cwd: pathlib.Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False)


# ---------------------------------------------------------------- tools


def tools_file() -> dict:
    return json.loads((PIPELINE / 'tools.json').read_text(encoding='utf-8'))


def find_quarto() -> pathlib.Path:
    """The pinned Quarto: $QUARTO, the copy scripts/setup.sh installs, or the one on the PATH."""
    wanted = tools_file()['quarto']['version']
    home = pathlib.Path(os.environ.get('HERTZFORGE_TOOLS', pathlib.Path.home() / 'dev' / 'tools'))
    candidates = [os.environ.get('QUARTO'), home / f'quarto-{wanted}' / 'bin' / 'quarto', shutil.which('quarto')]
    for candidate in candidates:
        if candidate and pathlib.Path(candidate).is_file():
            found = run([str(candidate), '--version'], ROOT).stdout.strip()
            if found == wanted:
                return pathlib.Path(candidate)
    raise Refused(f'Quarto {wanted} was not found. Run scripts/setup.sh, or set QUARTO to its path.')


def tool_versions(quarto: pathlib.Path) -> dict:
    from importlib import metadata

    import plotly

    script = (pathlib.Path(plotly.__file__).parent / 'package_data' / 'plotly.min.js').read_text(encoding='utf-8')[:400]
    theme = json.loads((THEME / 'SOURCE.json').read_text(encoding='utf-8'))
    commit = run(['git', 'rev-parse', 'HEAD'], ROOT).stdout.strip()
    dirty = bool(run(['git', 'status', '--porcelain', '--', 'pipeline', 'scripts', 'theme', 'journal.yml'], ROOT).stdout.strip())

    def first_line(*args: str) -> str:
        return (run([str(quarto), *args], ROOT).stdout.splitlines() or [''])[0].strip()

    return {
        'quarto': first_line('--version'),
        'pandoc': first_line('pandoc', '--version'),
        'typst': first_line('typst', '--version'),
        'python': sys.version.split()[0],
        'plotly': metadata.version('plotly'),
        'plotly.js': (re.search(r'plotly\.js v([\w.]+)', script) or [None, 'unknown'])[1],
        'kaleido': metadata.version('kaleido'),
        'theme': theme.get('commit', '')[:12],
        'build': commit[:12] + ('+changes' if dirty else ''),
    }


# ---------------------------------------------------------------- reading an article


def read_source(article: pathlib.Path) -> tuple[dict, str]:
    path = article / SOURCE
    if not path.is_file():
        raise Refused(f'{path} does not exist. An article is a folder holding {SOURCE}, data/ and code/.')
    match = re.match(r'---\n(.*?)\n---\n(.*)\Z', path.read_text(encoding='utf-8'), re.S)
    if not match:
        raise Refused(f'{path} must begin with its front matter between two lines of ---')
    front = yaml.safe_load(match.group(1)) or {}
    if not isinstance(front, dict):
        raise Refused(f'the front matter of {path} is not a set of named fields')
    return front, match.group(2)


def headings(body: str) -> list[tuple[int, str, int]]:
    """(level, title, line index) of every heading outside a code block."""
    found, fenced = [], False
    for index, line in enumerate(body.splitlines()):
        if line.lstrip().startswith(('```', '~~~')):
            fenced = not fenced
        match = None if fenced else re.match(r'(#{1,6})\s+(.+?)\s*(?:\{[^}]*\})?\s*$', line)
        if match:
            found.append((len(match.group(1)), match.group(2), index))
    return found


FIGURE = re.compile(r'!\[(?P<caption>[^\]]*)\]\(figures/(?P<name>[\w-]+)\.png\)(?:\{(?P<attrs>[^}]*)\})?')


def figures_in(body: str) -> list[dict]:
    found = []
    for match in FIGURE.finditer(body):
        attrs = match.group('attrs') or ''
        found.append({
            'name': match.group('name'),
            'caption': match.group('caption').strip(),
            'id': (re.search(r'#(fig-[\w-]+)', attrs) or [None, None])[1],
            'alt': (re.search(r'fig-alt="([^"]*)"', attrs) or [None, ''])[1].strip(),
            'data': (re.search(r'\bdata="([^"]*)"', attrs) or [None, ''])[1].strip(),
        })
    return found


def load_people() -> dict[str, dict]:
    people = {}
    for path in sorted((ROOT / 'people').glob('*.yml')):
        record = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
        if record.get('name'):
            people[record['name']] = record
    return people


def understand(article: pathlib.Path, journal: dict, real: bool, need_doi: bool) -> tuple[dict, str, list[str]]:
    """Reads and checks an article. Returns what the build needs, the body, and warnings.
    Everything wrong is reported at once."""
    front, body = read_source(article)
    wrong: list[str] = []
    warnings: list[str] = []

    article_id = str(front.get('id') or '')
    if not re.fullmatch(r'\d{4}-\d{3}', article_id):
        wrong.append(f'id must be <year>-<nnn>, for example 2026-001; it is {article_id!r}')
    elif article.name != article_id:
        wrong.append(f'the folder is named {article.name} but the article says its id is {article_id}')

    sample = bool(front.get('sample'))
    if real and sample:
        wrong.append('this is marked as a sample; a sample is never published. Build it under tests/')
    if not real and not sample:
        wrong.append('only a sample (sample: true) may be built outside articles/ and published/')

    title = str(front.get('title') or '').strip()
    if not title:
        wrong.append('title is empty')
    kind = front.get('type')
    if kind not in TYPES:
        wrong.append(f'type must be one of: {", ".join(TYPES)}')
    # A Perspective argues a position: it says what it rests on where others state an evidence level.
    evidence = ' '.join(str(front.get('evidence') or '').split())
    if kind == 'Perspective':
        if not evidence:
            wrong.append('evidence is empty: a Perspective says what it rests on, for example: published sources')
        evidence_label, evidence_shown = 'Rests on', evidence[:1].upper() + evidence[1:]
    else:
        if evidence not in EVIDENCE:
            wrong.append(f'evidence must be one of: {", ".join(EVIDENCE)}')
        evidence_label, evidence_shown = 'Evidence', EVIDENCE.get(evidence, '')
    evidence_note = ' '.join(str(front.get('evidence_note') or '').split())
    if not evidence_note:
        wrong.append('evidence_note is empty: say in one sentence what the results come from')
    abstract = str(front.get('abstract') or '').strip()
    if not abstract:
        wrong.append('abstract is empty')

    people = load_people()
    authors = []
    for number, entry in enumerate(front.get('authors') or [], 1):
        name = str((entry or {}).get('name') or '').strip()
        if not name:
            wrong.append(f'author {number} has no name')
            continue
        try:
            orcid = orcid_id(entry.get('orcid'), name)
        except Refused as problem:
            wrong.append(str(problem))
            orcid = None
        if not orcid:
            warnings.append(f'{name} has no ORCID iD')
        known = people.get(name)
        if known and orcid and known.get('orcid') and orcid_id(known['orcid'], name) != orcid:
            wrong.append(f"{name}'s ORCID iD differs from the one in people/")
        words = name.split()
        roles = list(entry.get('roles') or [])
        for role in roles:
            if role not in CREDIT_ROLES:
                wrong.append(f'{name}: {role!r} is not a CRediT role ({", ".join(CREDIT_ROLES)})')
        authors.append({
            'name': name,
            'family': str(entry.get('family') or words[-1]),
            'given': str(entry.get('given') or ' '.join(words[:-1])),
            'orcid': orcid,
            'roles': roles,
            'slug': slug(name),
        })
    if not authors:
        wrong.append('authors is empty')
    if len(authors) > 1:
        for author in authors:
            if not author['roles']:
                wrong.append(f'{author["name"]} has no roles; a co-authored article says who did what')

    versions = []
    for number, entry in enumerate(front.get('versions') or [], 1):
        entry = entry or {}
        if entry.get('version') != number:
            wrong.append(f'versions must run 1, 2, 3 in order; entry {number} says {entry.get("version")!r}')
        try:
            date = iso(entry.get('date'), f'the date of version {number}')
        except Refused as problem:
            wrong.append(str(problem))
            date = ''
        note = ' '.join(str(entry.get('note') or '').split())
        if not note:
            wrong.append(f'version {number} has no note saying what changed')
        doi = str(entry.get('doi') or '').strip()
        if doi and not re.fullmatch(r'10\.\d{4,9}/\S+', doi):
            wrong.append(f'the DOI of version {number} is not a DOI: {doi!r}')
        versions.append({'version': number, 'date': date, 'note': note, 'doi': doi})
    if not versions:
        wrong.append('versions is empty; the first entry is version 1')
    elif any(a['date'] > b['date'] for a, b in zip(versions, versions[1:]) if a['date'] and b['date']):
        wrong.append('the versions are not in date order')
    doi_latest = str(front.get('doi_latest') or '').strip()
    if doi_latest and not re.fullmatch(r'10\.\d{4,9}/\S+', doi_latest):
        wrong.append(f'doi_latest is not a DOI: {doi_latest!r}')
    if versions and need_doi and not (versions[-1]['doi'] and doi_latest):
        wrong.append('this version has no DOI, or the article has no doi_latest. Reserve both on Zenodo '
                     'first: a frozen version cannot be given a DOI afterward. (--no-doi builds without.)')

    implemented = front.get('implemented_in') or {}
    if isinstance(implemented, str):
        implemented = {'label': implemented}
    implemented = {'label': str(implemented.get('label') or '').strip(), 'url': str(implemented.get('url') or '').strip()}
    if implemented['url'] and not implemented['url'].startswith('https://'):
        wrong.append('implemented_in.url must be an https address')

    # The body: its closing sections, in order, and its figures.
    found = headings(body)
    if any(level == 1 for level, _, _ in found):
        wrong.append('the body has a level-one heading (#); the title is the only one, and sections start at ##')
    sections = [title_ for level, title_, _ in found if level == 2]
    if 'Contribution Statement' in sections:
        wrong.append('remove the Contribution Statement section: the build writes it from each author\'s roles')
    if 'Abstract' in sections:
        wrong.append('remove the Abstract section: the build places the abstract from the front matter')
    if tuple(sections[-len(CLOSING):]) != CLOSING:
        wrong.append(f'the article must end with these sections, in this order: {", ".join(CLOSING)}')

    figures = figures_in(body)
    if body.count('](figures/') != len(figures):
        wrong.append('a figure is not written as ![Caption.](figures/name.png){#fig-name fig-alt="..." data="data/file"}')
    seen = set()
    for figure in figures:
        where = f'figure {figure["name"]}'
        if figure['name'] in seen:
            wrong.append(f'{where} appears twice')
        seen.add(figure['name'])
        if not figure['id']:
            wrong.append(f'{where} has no id (#fig-...)')
        if not figure['caption']:
            wrong.append(f'{where} has no caption')
        if not figure['alt']:
            wrong.append(f'{where} has no alternative text (fig-alt="...")')
        if not (article / 'code' / f'{figure["name"]}.py').is_file():
            wrong.append(f'{where}: code/{figure["name"]}.py does not exist; every figure is drawn by a file in code/')
        if not figure['data']:
            wrong.append(f'{where} names no data file (data="data/...")')
        elif not figure['data'].startswith('data/') or not (article / figure['data']).is_file():
            wrong.append(f'{where}: {figure["data"]} is not a file under data/')

    if wrong:
        raise Refused(f'{article / SOURCE} cannot be built:\n' + '\n'.join(f'  - {line}' for line in wrong))

    number = versions[-1]['version']
    first_year = int(versions[0]['date'][:4])
    editors = {name for name, record in people.items() if record.get('role') == 'editor'}
    by_line = {author['name'] for author in authors}
    editors_note = None
    if editors and editors <= by_line:
        editors_note = ("The authors of this article are the journal's editors. Its reviewers are drawn from "
                        'outside the author list.')
    site = journal['site'].rstrip('/')
    base = f'{site}{journal["path"]}/{article_id}'
    ctx = {
        'id': article_id, 'n': number, 'sample': sample, 'title': title, 'kind': kind,
        'evidence': evidence_shown, 'evidence_label': evidence_label, 'evidence_key': evidence, 'evidence_note': evidence_note,
        'abstract': abstract, 'authors': authors, 'versions': versions,
        'date': versions[-1]['date'], 'first': versions[0]['date'], 'note': versions[-1]['note'],
        'doi': versions[-1]['doi'], 'doi_latest': doi_latest,
        'issn': str(journal.get('issn') or '').strip(), 'journal': journal['title'],
        'volume': first_year - int(journal['first_volume_year']) + 1, 'year': versions[-1]['date'][:4],
        'site': site, 'journal_address': f'{site}{journal["path"]}/',
        'article_address': f'{base}/', 'address': f'{base}/v{number}/',
        'stem': f'{article_id}-v{number}', 'implemented': implemented, 'editors_note': editors_note,
        'people_pages': bool(journal.get('people_pages')), 'figures': figures,
        'bibliography': 'references.bib' if (article / 'references.bib').is_file() else '',
        'benchmarks': str(front.get('benchmarks') or '').strip(),
    }
    ctx.update(citation(ctx))
    return ctx, body, warnings


# ---------------------------------------------------------------- the citation


def citation(ctx: dict) -> dict:
    """The formatted citation, and the same as BibTeX and RIS."""

    def short(author: dict) -> str:
        initials = ' '.join(
            '-'.join(part[0] + '.' for part in word.split('-') if part) for word in author['given'].split()
        )
        return f'{author["family"]}, {initials}'.rstrip(', ')

    names = [short(author) for author in ctx['authors']]
    if len(names) == 1:
        by = names[0]
    else:
        by = ', '.join(names[:-1]) + ', and ' + names[-1]
    link = f'https://doi.org/{ctx["doi"]}' if ctx['doi'] else ctx['address']
    head = f'{by} ({ctx["year"]}). {ctx["title"]}.'
    tail = f'{ctx["volume"]}, {ctx["id"]}, version {ctx["n"]}. {link}'

    def tex(text: str) -> str:
        return re.sub(r'([&%$#_{}])', r'\\\1', text)

    key = re.sub(r'[^a-z]', '', ctx['authors'][0]['family'].lower()) + ctx['year'] + 'hf' + ctx['id'].replace('-', '') + f'v{ctx["n"]}'
    fields = [
        ('author', ' and '.join(f'{tex(a["family"])}, {tex(a["given"])}'.rstrip(', ') for a in ctx['authors'])),
        ('title', '{' + tex(ctx['title']) + '}'),
        ('journal', tex(ctx['journal'])),
        ('year', ctx['year']),
        ('volume', str(ctx['volume'])),
        ('number', ctx['id']),
        ('note', f'Version {ctx["n"]}'),
        ('doi', ctx['doi']),
        ('issn', ctx['issn']),
        ('url', ctx['address']),
    ]
    bibtex = '@article{' + key + ',\n' + ',\n'.join(f'  {name} = {{{value}}}' for name, value in fields if value) + '\n}\n'

    ris_lines = [('TY', 'JOUR')]
    ris_lines += [('AU', f'{a["family"]}, {a["given"]}'.rstrip(', ')) for a in ctx['authors']]
    ris_lines += [
        ('TI', ctx['title']), ('JO', ctx['journal']), ('VL', str(ctx['volume'])), ('SP', ctx['id']),
        ('PY', ctx['year']), ('DA', ctx['date'].replace('-', '/')), ('ET', f'Version {ctx["n"]}'),
        ('DO', ctx['doi']), ('SN', ctx['issn']), ('UR', ctx['address']),
        ('AB', plain(ctx['abstract'])), ('ER', ''),
    ]
    ris = ''.join(f'{tag}  - {value}\r\n' for tag, value in ris_lines if value or tag == 'ER')
    return {'cite_head': head, 'cite_tail': tail, 'cite_link': link, 'bibtex': bibtex, 'ris': ris}


def plain(markdown: str) -> str:
    """Markdown read as one line of plain text, for a description or an abstract field."""
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', markdown)
    text = re.sub(r'[*_`$]', '', text)
    return ' '.join(text.split())


def highwire(ctx: dict) -> list[tuple[str, str]]:
    """The tags that index an article, as the indexer documents them: dates as YYYY/MM/DD, one
    author tag per author in order, the article number as its first page."""
    tags = [('citation_title', ctx['title'])]
    tags += [('citation_author', author['name']) for author in ctx['authors']]
    tags += [
        ('citation_publication_date', ctx['date'].replace('-', '/')),
        ('citation_journal_title', ctx['journal']),
    ]
    if ctx['issn']:
        tags.append(('citation_issn', ctx['issn']))
    tags += [('citation_volume', str(ctx['volume'])), ('citation_firstpage', ctx['id'])]
    if ctx['doi']:
        tags.append(('citation_doi', ctx['doi']))
    tags.append(('citation_pdf_url', f'{ctx["address"]}{ctx["stem"]}.pdf'))
    return tags


# ---------------------------------------------------------------- the page


MARKS = {
    'review-open': '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="2.5" fill="currentColor" stroke="none"/>',
    'reviewed': '<circle cx="12" cy="12" r="8.5"/><path d="M8 12.4l2.7 2.7L16 9.6"/>',
    'retracted': '<circle cx="12" cy="12" r="8.5"/><path d="M6 18L18 6"/>',
}


def trace() -> str:
    """The waveform the site runs under its page titles: here, one decaying burst."""
    points = []
    for step in range(0, 1201, 3):
        envelope = math.exp(-(((step - 260) / 150) ** 2)) + 0.35 * math.exp(-(((step - 760) / 110) ** 2))
        points.append(f'{step} {50 - 40 * envelope * math.sin(step / 7.2):.1f}')
    path = 'M' + 'L'.join(points)
    return ('<svg class="trace" viewBox="0 0 1200 100" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
            f'<path class="trace-glow" d="{path}"></path><path class="trace-line" d="{path}"></path></svg>')


def head_html(ctx: dict, variant: str) -> str:
    description = plain(ctx['abstract'])
    if len(description) > 300:
        description = description[:297].rsplit(' ', 1)[0] + '...'
    lines = [
        f'<title>{esc(ctx["title"])} | {esc(ctx["journal"])}</title>',
        f'<meta name="description" content="{esc(description)}">',
        f'<link rel="canonical" href="{esc(ctx["address"])}">',
    ]
    if ctx['sample']:
        lines.append('<meta name="robots" content="noindex, nofollow">')
    lines += [f'<meta name="{name}" content="{esc(value)}">' for name, value in highwire(ctx)]
    lines += [
        '<meta property="og:type" content="article">',
        f'<meta property="og:site_name" content="{esc(ctx["journal"])}">',
        f'<meta property="og:url" content="{esc(ctx["address"])}">',
        f'<meta property="og:title" content="{esc(ctx["title"])}">',
        f'<meta property="og:description" content="{esc(description)}">',
        '<meta name="color-scheme" content="light dark">',
        '<meta name="theme-color" content="#000000">',
    ]
    if variant == 'page':
        lines.append('<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">')
    lines += [
        '<link rel="stylesheet" href="assets/site.css">',
        '<link rel="stylesheet" href="assets/article.css">',
        # Before first paint: mark that scripts run, and apply the reader's saved choice of theme.
        "<script>(function(){var r=document.documentElement;r.classList.add('js');try{var s=localStorage.getItem('hf-theme');"
        "if(s==='light'||s==='dark')r.dataset.theme=s;}catch(e){}})();</script>",
    ]
    return '\n'.join(lines) + '\n'


def shell_html(ctx: dict, variant: str, status: dict, sizes: dict[str, int]) -> str:
    """Everything on the page around the article's own text, top to bottom, with BODY_MARK where
    the text goes. `variant` is "page" (the article page) or "single" (the one-file download)."""
    single = variant == 'single'
    header = (THEME / 'header.html').read_text(encoding='utf-8')
    footer = (THEME / 'footer.html').read_text(encoding='utf-8')
    if single:  # a file on someone's disk has no site around it
        header = re.sub(r'href="/(?!/)', f'href="{ctx["site"]}/', header)
        footer = re.sub(r'href="/(?!/)', f'href="{ctx["site"]}/', footer)
    stem, n = ctx['stem'], ctx['n']
    slug_, meaning = STATUS[status['status']]
    if status['status'] == 'Retracted' and status.get('retraction'):
        meaning = f'Retracted: {status["retraction"]}'

    out: list[str] = ['<a class="skip" href="#main">Skip to content</a>', header]
    out.append('<main id="main"' + ('' if single else ' data-pagefind-body') + '>')
    record = '' if single else ' data-record="../record.json"'
    out.append(f'<article class="hf-article" data-id="{ctx["id"]}" data-version="{n}"{record}>')

    # 1. Status banner.
    marks = ''.join(
        f'<svg data-for="{name}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{shape}</svg>' for name, shape in MARKS.items()
    )
    as_of = (f' <span class="hf-status-asof">As of {ctx["date"]}, when this version was published; the status now '
             f'is at <a href="{esc(ctx["article_address"])}">{esc(ctx["article_address"].split("//")[1])}</a>.</span>')
    out.append(
        f'<div class="hf-status dark" id="hf-status" data-status="{slug_}"><div class="wrap">'
        f'<span class="hf-status-mark" aria-hidden="true">{marks}</span>'
        f'<strong class="hf-status-name">{esc(status["status"])}</strong>'
        f'<span class="hf-status-text">{esc(meaning)}</span>{as_of}'
        '<a class="hf-status-link" href="#hf-reviews">Reviews</a></div></div>'
    )
    if ctx['sample']:
        out.append('<div class="hf-sample dark"><div class="wrap"><strong>Sample. Not a publication.</strong> '
                   "This page exists to test the journal's build. Its authors, data and results are invented.</div></div>")

    # 2. Title, type, authors.  3. Evidence level.
    authors = []
    for author in ctx['authors']:
        name = f'<span class="hf-author-name">{esc(author["name"])}</span>'
        if ctx['people_pages']:
            people = f'/people/{author["slug"]}/' if not single else f'{ctx["site"]}/people/{author["slug"]}/'
            name = f'<a class="hf-author-name" href="{people}">{esc(author["name"])}</a>'
        orcid = (f' <a class="hf-orcid" href="https://orcid.org/{author["orcid"]}" rel="noopener">ORCID {author["orcid"]}</a>'
                 if author['orcid'] else '')
        authors.append(f'<li>{name}{orcid}</li>')
    editors_note = f'<p class="hf-editors-note">{esc(ctx["editors_note"])}</p>' if ctx['editors_note'] else ''
    out.append(
        '<div class="page-head dark"><div class="wrap">'
        f'<p class="eyebrow">{esc(ctx["journal"])}</p>'
        f'<h1 class="steel">{esc(ctx["title"])}</h1>'
        f'<p class="hf-kind" id="hf-type"><span class="tag tag-strong">{esc(ctx["kind"])}</span></p>'
        f'<ul class="hf-authors" id="hf-authors">{"".join(authors)}</ul>{editors_note}'
        f'<p class="hf-evidence" id="hf-evidence"><span class="tag">{ctx["evidence_label"]}</span><strong>{esc(ctx["evidence"])}.</strong> '
        f'{esc(ctx["evidence_note"])}</p>'
        f'</div>{trace()}</div>'
    )
    out.append('<div class="page-body"><div class="wrap"><div class="prose hf-prose">')
    out.append('<section class="hf-meta" aria-label="About this version">')

    # 4. Version line: this version, its date, first publication, the selector, the change note.
    known = ' '.join(
        (f'<strong>{v["version"]} (this version)</strong>' if v['version'] == n else f'<a href="../v{v["version"]}/">{v["version"]}</a>')
        for v in ctx['versions']
    )
    history = ''.join(
        '<li>' + (f'<a href="../v{v["version"]}/">Version {v["version"]}</a>' if v['version'] != n and not single else f'Version {v["version"]}')
        + f', {v["date"]}. {esc(v["note"])}</li>' for v in ctx['versions']
    )
    if single:
        versions_line = (f'<p class="hf-versions">Every version, and any later than this one, is at '
                         f'<a href="{esc(ctx["article_address"])}">{esc(ctx["article_address"])}</a>.</p>')
        selector = ''
    else:
        versions_line = (f'<p class="hf-versions">Versions: {known}. Any later version is listed at '
                         f'<a href="../">the article\'s address</a>.</p>')
        selector = '<label class="hf-select-label" for="hf-version-select" id="hf-version-select-slot" hidden></label>'
    out.append(
        '<div class="hf-panel hf-version" id="hf-version"><h2 class="hf-label">Version</h2>'
        f'<p class="hf-version-line"><span><strong>Version {n}</strong>, published {ctx["date"]}. '
        f'First published {ctx["first"]}.</span>{selector}</p>'
        f'<p class="hf-note">Change note: {esc(ctx["note"])}</p>{versions_line}'
        '<div class="note hf-notlatest" hidden></div>'
        f'<details class="hf-history"><summary>Version history</summary><ol>{history}</ol></details></div>'
    )

    # 5. DOIs, then the citation box with BibTeX and RIS.
    def doi_row(label: str, doi: str, none: str) -> str:
        value = f'<a href="https://doi.org/{esc(doi)}" rel="noopener">{esc(doi)}</a>' if doi else none
        return f'<dt>{label}</dt><dd>{value}</dd>'

    ids = doi_row('DOI of this version', ctx['doi'], 'None assigned') + doi_row(
        'DOI that always gives the latest version', ctx['doi_latest'], 'None assigned')
    if ctx['issn']:
        ids += f'<dt>ISSN</dt><dd>{esc(ctx["issn"])}</dd>'
    out.append(f'<div class="hf-panel" id="hf-doi"><h2 class="hf-label">Identifiers</h2><dl class="hf-ids">{ids}</dl></div>')
    embed = ' data-hf-embed' if single else ''
    nowrap_id = f'<span class="hf-nowrap">{ctx["id"]}</span>'
    out.append(
        '<div class="hf-panel hf-cite" id="hf-cite"><h2 class="hf-label">Cite This Version</h2>'
        f'<p class="hf-citation">{esc(ctx["cite_head"])} <em>{esc(ctx["journal"])}</em> '
        f'{esc(ctx["cite_tail"].rsplit(" ", 1)[0]).replace(ctx["id"], nowrap_id)} '
        f'<a href="{esc(ctx["cite_link"])}" rel="noopener">{esc(ctx["cite_link"])}</a></p>'
        f'<p class="hf-cite-files"><a class="btn btn-ghost btn-sm" href="{stem}.bib" download="{stem}.bib"{embed}>BibTeX</a>'
        f'<a class="btn btn-ghost btn-sm" href="{stem}.ris" download="{stem}.ris"{embed}>RIS</a></p>'
        f'<details><summary>Show the BibTeX entry</summary><pre><code>{esc(ctx["bibtex"])}</code></pre></details></div>'
    )

    # 6. Downloads.
    if single:
        out.append(
            '<div class="hf-panel hf-downloads" id="hf-downloads"><h2 class="hf-label">This Copy</h2>'
            f'<p>This is the downloaded copy of version {n}: one file that opens without a network connection and '
            'asks nothing of any server. The article page, the PDF print copy and the data and code bundle are at '
            f'<a href="{esc(ctx["address"])}">{esc(ctx["address"])}</a>.</p></div>'
        )
    else:
        def item(file: str, label: str, about: str) -> str:
            return (f'<li><a href="{file}" download="{file}">{label}</a><span class="size">{human_size(sizes[file])}</span>'
                    f'<span class="d">{about}</span></li>')

        out.append(
            '<div class="hf-downloads" id="hf-downloads"><h2 class="hf-label">Downloads</h2><ul class="dl">'
            + item(f'{stem}.html', 'The Article in One File', 'Interactive, and opens without a network connection. It asks nothing of any server, so it can be carried onto a closed network.')
            + item(f'{stem}.pdf', 'PDF Print Copy', 'Static figures, from the same source as this page.')
            + item(f'{stem}-bundle.zip', 'Data and Code Bundle', 'The data behind every figure and the code that draws it, with what is needed to run it again.')
            + '</ul></div>'
        )
    out.append('</section>')

    # 7 to 9: the abstract, the body and its closing sections come from the article.
    out.append(BODY_MARK)

    # 10. Implemented in.
    if ctx['implemented']['label']:
        label = esc(ctx['implemented']['label'])
        if ctx['implemented']['url']:
            label = f'<a href="{esc(ctx["implemented"]["url"])}" rel="noopener">{label}</a>'
        out.append(f'<section class="hf-end" id="hf-implemented"><h2>Implemented In</h2><p>{label}</p></section>')

    # 11. Reviews: each invited review, and the thread.
    reviews = status.get('reviews') or []
    if reviews:
        rows = ''.join(
            '<li>' + (f'<a href="{esc(r["url"])}" rel="noopener">' if r.get('url') else '')
            + 'Review by ' + esc(r.get('reviewer') or 'a reviewer whose name is withheld at their request')
            + ('</a>' if r.get('url') else '')
            + (f', of version {r["version"]}' if r.get('version') else '') + (f', {r["date"]}' if r.get('date') else '') + '.</li>'
            for r in reviews
        )
        listed = f'<ul class="hf-reviews-list">{rows}</ul>'
    else:
        listed = '<p>No invited review had been posted when this version was published.</p>'
    thread = (f'<p><a href="{esc(status["thread"])}" rel="noopener">The review thread</a>: reviews, the authors\u2019 '
              'answers, and comments from anyone.</p>') if status.get('thread') else ''
    out.append(
        '<section class="hf-end" id="hf-reviews"><h2>Reviews</h2>'
        '<p>Review is public and signed, and stays open after publication.</p>'
        f'<div id="hf-reviews-static">{listed}{thread}<p>Reviews posted since are listed at '
        f'<a href="{esc(ctx["article_address"])}">{esc(ctx["article_address"])}</a>.</p></div>'
        '<div id="hf-reviews-live"></div></section>'
    )

    # 12. License line.
    holders = [a['name'] for a in ctx['authors']]
    by = holders[0] if len(holders) == 1 else ', '.join(holders[:-1]) + ' and ' + holders[-1]
    out.append(
        f'<p class="hf-license" id="hf-license">Copyright {ctx["first"][:4]} {esc(by)}. Text, figures and data '
        '<a href="https://creativecommons.org/licenses/by/4.0/" rel="license noopener">CC BY 4.0</a>; code '
        f'<a href="https://opensource.org/license/mit" rel="license noopener">MIT</a>.<br>{USE}</p>'
    )
    out.append('</div></div></div></article></main>')
    out.append(footer)
    if ctx['figures']:
        out.append('<script src="assets/plotly.min.js"></script>')
    out.append('<script src="assets/article.js"></script>')
    return '\n'.join(out) + '\n'


# ---------------------------------------------------------------- the print copy


def typ(text: object) -> str:
    """A Typst string: shown as written, whatever characters it holds."""
    return '"' + str(text).replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ') + '"'


def print_parts(ctx: dict) -> dict[str, str]:
    year, month, day = (int(part) for part in ctx['date'].split('-'))
    authors = ', '.join(typ(a['name']) for a in ctx['authors'])
    running = f'{ctx["journal"]} {ctx["volume"]}, {ctx["id"]}, version {ctx["n"]}'
    show = (
        '#show: doc => article(\n'
        f'  running: {typ(running)},\n'
        f'  address: {typ(ctx["address"])},\n'
        f'  title: {typ(ctx["title"])},\n'
        f'  authors: ({authors},),\n'
        f'  date: datetime(year: {year}, month: {month}, day: {day}),\n'
        '  doc,\n)\n'
    )

    def opt(value: str) -> str:
        return typ(value) if value else 'none'

    people = ', '.join(f'(name: {typ(a["name"])}, orcid: {opt(a["orcid"] or "")})' for a in ctx['authors'])
    version_line = f'Version {ctx["n"]}, published {ctx["date"]}. First published {ctx["first"]}.'
    cite = f'{ctx["cite_head"]} {ctx["journal"]} {ctx["cite_tail"]}'
    cover = (
        '#hf-cover(\n'
        f'  journal: {typ(ctx["journal"])},\n'
        f'  sample: {"true" if ctx["sample"] else "false"},\n'
        f'  title: {typ(ctx["title"])},\n'
        f'  kind: {typ(ctx["kind"])},\n'
        f'  authors: ({people},),\n'
        f'  editors-note: {opt(ctx["editors_note"] or "")},\n'
        f'  evidence-label: {typ(ctx["evidence_label"])},\n'
        f'  evidence: {typ(ctx["evidence"])},\n'
        f'  evidence-note: {typ(ctx["evidence_note"])},\n'
        f'  version-line: {typ(version_line)},\n'
        f'  note: {typ(ctx["note"])},\n'
        f'  address: {typ(ctx["address"])},\n'
        f'  doi: {opt(ctx["doi"])},\n'
        f'  doi-latest: {opt(ctx["doi_latest"])},\n'
        f'  issn: {opt(ctx["issn"])},\n'
        f'  citation: {typ(cite)},\n'
        ')\n'
    )
    holders = [a['name'] for a in ctx['authors']]
    by = holders[0] if len(holders) == 1 else ', '.join(holders[:-1]) + ' and ' + holders[-1]
    reviews = ('This article is reviewed in public. Its reviews, its review status and any later version are at '
               + ctx['article_address'])
    license_line = f'Copyright {ctx["first"][:4]} {by}. Text, figures and data CC BY 4.0; code MIT.'
    back = (
        '#hf-back(\n'
        f'  implemented: {opt(ctx["implemented"]["label"])},\n'
        f'  implemented-url: {opt(ctx["implemented"]["url"])},\n'
        f'  reviews: {typ(reviews)},\n'
        f'  license: {typ(license_line)},\n'
        f'  use: {typ(USE)},\n'
        ')\n'
    )
    return {'typst-show.typ': show, '_cover.typ': cover, '_back.typ': back}


# ---------------------------------------------------------------- the source Quarto reads


def quarto_source(ctx: dict, body: str) -> str:
    """The article as Quarto reads it: the abstract placed first, the contribution statement
    written from the authors' roles, and the closing sections given fixed anchors. The front
    matter the journal's own rules read is not passed on."""
    lines = body.strip('\n').splitlines()
    marks = {title: index for level, title, index in headings(body.strip('\n')) if level == 2 and title in CLOSING}
    anchors = {'How This Was Made': 'how-this-was-made', 'Acknowledgments': 'acknowledgments', 'References': 'references'}
    for title, index in marks.items():
        lines[index] = f'## {title} {{#{anchors[title]}}}'
    if ctx['bibliography'] and '{#refs}' not in body:
        lines.insert(marks['References'] + 1, '\n::: {#refs}\n:::')
    if len(ctx['authors']) > 1:
        statement = ['## Contribution Statement {#contribution-statement}', '']
        statement += [f'- **{a["name"]}:** {", ".join(a["roles"])}.' for a in ctx['authors']]
        lines[marks['How This Was Made']:marks['How This Was Made']] = [*statement, '']

    front = {'title': ctx['title'], 'lang': 'en', 'engine': 'markdown', 'link-citations': True, 'filters': ['figures.lua']}
    if ctx['bibliography']:
        front['bibliography'] = ctx['bibliography']
    return '\n'.join([
        '---', yaml.safe_dump(front, sort_keys=False, allow_unicode=True).strip(), '---', '',
        '::: {.hf-abstract}', '## Abstract {#abstract}', '', ctx['abstract'], ':::', '',
        '```{=typst}', '#pagebreak()', '```', '',
        *lines, '',
    ])


FORMATS = {
    'page': {'format': {'html': {
        'template': 'page-template.html', 'minimal': True, 'theme': 'none', 'html-math-method': 'mathml',
        'appendix-style': 'none', 'include-in-header': '_head-page.html',
        'include-before-body': '_front-page.html', 'include-after-body': '_back-page.html',
    }}},
    'single': {'format': {'html': {
        'template': 'page-template.html', 'minimal': True, 'theme': 'none', 'html-math-method': 'mathml',
        'appendix-style': 'none', 'embed-resources': True, 'include-in-header': '_head-single.html',
        'include-before-body': '_front-single.html', 'include-after-body': '_back-single.html',
    }}},
    'print': {'format': {'typst': {
        'template-partials': ['typst-template.typ', 'typst-show.typ'], 'citeproc': True, 'keep-typ': True,
        'include-before-body': '_cover.typ', 'include-after-body': '_back.typ',
    }}},
}


def render(quarto: pathlib.Path, work: pathlib.Path, variant: str, output: str) -> None:
    (work / f'_{variant}.yml').write_text(yaml.safe_dump(FORMATS[variant], sort_keys=False), encoding='utf-8')
    to = 'typst' if variant == 'print' else 'html'
    done = run([str(quarto), 'render', '_article.qmd', '--to', to, '--metadata-file', f'_{variant}.yml', '--output', output],
               work, dict(os.environ, HF_VARIANT=variant))
    if done.returncode != 0 or not (work / output).is_file():
        tail = '\n'.join((done.stdout + done.stderr).splitlines()[-25:])
        raise Refused(f'Quarto could not build {output}:\n{tail}')


def finish_html(path: pathlib.Path, work: pathlib.Path) -> None:
    """Quarto drops the doctype; without it a browser lays the page out in its old-pages mode.
    In the one-file copy, each small file a link offers is written into the link itself."""
    text = path.read_text(encoding='utf-8')
    if not text.lstrip().lower().startswith('<!doctype'):
        text = '<!doctype html>\n' + text

    def embed(match: re.Match[str]) -> str:
        file = work / match.group(1)
        kind = mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
        if file.suffix in ('.bib', '.ris', '.py', '.csv', '.txt', '.json'):
            kind = 'text/plain;charset=utf-8'
        data = base64.b64encode(file.read_bytes()).decode('ascii')
        return f'href="data:{kind};base64,{data}"'

    text = re.sub(r'href="([^"]+)"(?= download="[^"]*" data-hf-embed)', embed, text)
    text = text.replace(' data-hf-embed', '')
    path.write_text(text, encoding='utf-8')


# ---------------------------------------------------------------- the bundle


def bundle(ctx: dict, work: pathlib.Path, target: pathlib.Path, versions: dict) -> None:
    """The data behind every figure and the code that draws it, with what is needed to run it
    again. The same files always make the same zip."""
    top = f'{ctx["stem"]}-bundle'
    holders = [a['name'] for a in ctx['authors']]
    by = holders[0] if len(holders) == 1 else ', '.join(holders[:-1]) + ' and ' + holders[-1]
    mit = (ROOT / 'LICENSE-CODE').read_text(encoding='utf-8').split('\n\n', 2)[2]
    figure_lines = '\n'.join(f'    python draw.py . {figure["name"]}' for figure in ctx['figures']) or '    (this article has no figures)'
    readme = f"""# Data and Code: {ctx['title']}

{by}. {ctx['journal']} {ctx['volume']}, {ctx['id']}, version {ctx['n']} ({ctx['date']}).

The article: {ctx['address']}
{('DOI of this version: https://doi.org/' + ctx['doi']) if ctx['doi'] else ''}

`data/` holds the data behind every figure. `code/` holds the code that draws each one.
`draw.py` is the journal's figure runner, as it was when this version was built.

## Drawing the Figures Again

Needs Python 3.10 or later and a Chrome or Chromium browser (the static pictures are rendered
with it).

    pip install -r requirements.txt
{figure_lines}

Each command writes `figures/<name>.json` (the interactive figure) and `figures/<name>.png` (its
static picture).

## License

The data, and the figures drawn from it, are under Creative Commons Attribution 4.0
International (https://creativecommons.org/licenses/by/4.0/): reuse them, with credit to the
authors. The code is under the MIT license. Both are in `LICENSE.txt`.
"""
    license_text = (
        f'Copyright (c) {ctx["first"][:4]} {by}\n\n'
        'DATA AND FIGURES (the files in data/, and the figures drawn from them)\n\n'
        'Creative Commons Attribution 4.0 International (CC BY 4.0).\n'
        'https://creativecommons.org/licenses/by/4.0/legalcode\n\n'
        'CODE (the files in code/, and draw.py)\n\nMIT License\n\n' + mit
    )
    requirements = f'plotly=={versions["plotly"]}\nkaleido=={versions["kaleido"]}\n'
    members: list[tuple[str, bytes]] = [
        ('README.md', readme.encode()), ('LICENSE.txt', license_text.encode()),
        ('requirements.txt', requirements.encode()),
        ('draw.py', (PIPELINE / 'draw.py').read_bytes()), ('palette.json', (PIPELINE / 'palette.json').read_bytes()),
    ]
    for folder in ('data', 'code'):
        for path in sorted((work / folder).rglob('*')):
            if path.is_file():
                members.append((path.relative_to(work).as_posix(), path.read_bytes()))
    year, month, day = (int(part) for part in ctx['date'].split('-'))
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in members:
            info = zipfile.ZipInfo(f'{top}/{name}', date_time=(year, month, day, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)


# ---------------------------------------------------------------- the article's record


def read_status(reviews: pathlib.Path, article_id: str) -> dict:
    """An article's review state: reviews/<id>/status.yml, or Review open when there is none."""
    path = reviews / article_id / 'status.yml'
    status = {'status': 'Review open', 'thread': '', 'retraction': '', 'reviews': []}
    if path.is_file():
        status.update(yaml.safe_load(path.read_text(encoding='utf-8')) or {})
    if status['status'] not in STATUS:
        raise Refused(f'{path}: status must be one of: {", ".join(STATUS)}')
    for value in [status['thread'], *[review.get('url', '') for review in status['reviews'] or []]]:
        if value and not str(value).startswith('https://'):
            raise Refused(f'{path}: {value!r} must be an https address')
    status['reviews'] = [
        {**review, 'date': iso(review['date'], 'a review date') if review.get('date') else ''}
        for review in status['reviews'] or []
    ]
    return status


def write_record(published: pathlib.Path, reviews: pathlib.Path, article_id: str, journal: dict) -> dict:
    """What changes after a version is frozen lives beside the versions, not in them: which
    versions exist, the review status, the reviews. Pages read it; the site lists from it. Also
    writes the article's own address, which forwards to the latest version."""
    home = published / article_id
    frozen = [json.loads((folder / 'version.json').read_text(encoding='utf-8'))
              for folder in version_folders(published) if folder.parent == home]
    if not frozen:
        raise Refused(f'{home} holds no published version')
    latest = frozen[-1]
    status = read_status(reviews, article_id)
    record = {
        'id': article_id,
        'title': latest['title'],
        'type': latest['type'],
        'evidence': latest['evidence'],
        'authors': latest['authors'],
        'first_published': frozen[0]['date'],
        'latest': latest['version'],
        'versions': [{'version': v['version'], 'date': v['date'], 'note': v['note'], 'doi': v['doi']} for v in frozen],
        'doi_latest': latest['doi_latest'],
        'status': status['status'],
        'retraction': status['retraction'],
        'thread': status['thread'],
        'reviews': status['reviews'],
        'sample': latest['sample'],
    }
    (home / 'record.json').write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    address = f'{journal["site"].rstrip("/")}{journal["path"]}/{article_id}/v{latest["version"]}/'
    robots = '<meta name="robots" content="noindex, nofollow">\n' if latest['sample'] else ''
    (home / 'index.html').write_text(
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        f'<title>{esc(latest["title"])} | {esc(journal["title"])}</title>\n{robots}'
        f'<link rel="canonical" href="{esc(address)}">\n'
        f'<meta http-equiv="refresh" content="0; url=v{latest["version"]}/">\n</head>\n<body>\n'
        f'<p>The latest version of this article is <a href="v{latest["version"]}/">version {latest["version"]}</a>.</p>\n'
        '</body>\n</html>\n',
        encoding='utf-8',
    )
    return record


# ---------------------------------------------------------------- checks of what was built


class Requests(html.parser.HTMLParser):
    """Every address a page would fetch as it loads: scripts, stylesheets, images, frames, media,
    and anything a style block or attribute pulls in."""

    LOADS = {'script': 'src', 'img': 'src', 'iframe': 'src', 'source': 'src', 'video': 'src',
             'audio': 'src', 'embed': 'src', 'object': 'data', 'track': 'src', 'input': 'src'}
    LINKS = {'stylesheet', 'icon', 'preload', 'modulepreload', 'manifest', 'prefetch', 'preconnect', 'dns-prefetch'}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.found: list[str] = []
        self.in_style = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        fields = dict(attrs)
        address = fields.get(self.LOADS.get(tag, ''))
        if tag == 'link' and set((fields.get('rel') or '').lower().split()) & self.LINKS:
            address = fields.get('href')
        if address is not None:
            self.found.append(address)
        for name in ('srcset', 'poster', 'style'):
            if fields.get(name):
                self.css(fields[name]) if name == 'style' else self.found.append(fields[name])
        self.in_style = tag == 'style'

    def handle_endtag(self, tag: str) -> None:
        if tag == 'style':
            self.in_style = False

    def handle_data(self, data: str) -> None:
        if self.in_style:
            self.css(data)

    def css(self, text: str) -> None:
        self.found += [m.group(1).strip('\'" ') for m in re.finditer(r'url\(([^)]*)\)', text)]
        self.found += [m.group(1) for m in re.finditer(r'@import\s+["\']([^"\']+)', text)]


def outside_requests(page: pathlib.Path) -> list[str]:
    """The addresses a one-file page would fetch that are not written into the file itself."""
    reader = Requests()
    reader.feed(page.read_text(encoding='utf-8'))
    return sorted({address for address in reader.found if not address.startswith(('data:', '#'))})


def inspect(stage: pathlib.Path, ctx: dict) -> list[str]:
    """Checks a built version against the journal's rules before it is frozen."""
    wrong = []
    stem = ctx['stem']
    page = (stage / 'index.html').read_text(encoding='utf-8')
    head = page.split('</head>')[0]

    if not page.lower().startswith('<!doctype html>'):
        wrong.append('index.html does not begin with a doctype')
    tags = [(name, html.unescape(value)) for name, value in re.findall(r'<meta name="(citation_[a-z_]+)" content="([^"]*)">', head)]
    if tags != highwire(ctx):
        wrong.append(f'the citation tags in the head are not the ones expected: {tags}')
    if f'<link rel="canonical" href="{esc(ctx["address"])}">' not in head:
        wrong.append('the head has no canonical link to this version')

    # The parts of the page, top to bottom, as the journal lists them.
    order = ['id="hf-status"', '<h1', 'id="hf-type"', 'id="hf-authors"', 'id="hf-evidence"', 'id="hf-version"',
             'id="hf-version-select-slot"', 'id="hf-doi"', 'id="hf-cite"', f'href="{stem}.bib"', f'href="{stem}.ris"',
             'id="hf-downloads"', 'id="abstract"']
    if len(ctx['authors']) > 1:
        order.append('id="contribution-statement"')
    order += ['id="how-this-was-made"', 'id="acknowledgments"', 'id="references"']
    if ctx['implemented']['label']:
        order.append('id="hf-implemented"')
    order += ['id="hf-reviews"', 'id="hf-license"']
    at = -1
    for mark in order:
        found = page.find(mark, at + 1)
        if found < 0:
            wrong.append(f'the page is missing {mark}, or has it out of order')
            break
        at = found
    for figure in ctx['figures']:
        if f'src="figures/{figure["name"]}.png"' not in page or f'data-figure="{figure["name"]}"' not in page:
            wrong.append(f'figure {figure["name"]} is not on the page with both its picture and its interactive form')

    single = stage / f'{stem}.html'
    for address in outside_requests(single):
        wrong.append(f'the one-file copy would fetch {address[:90]}')
    if 'data-record="' in single.read_text(encoding='utf-8'):
        wrong.append('the one-file copy asks for the article record; it must ask for nothing')

    from pypdf import PdfReader

    reader = PdfReader(stage / f'{stem}.pdf')
    first = ' '.join(reader.pages[0].extract_text().split())
    if 'print copy' not in first.lower() or ctx['address'] not in first.replace(' ', ''):
        wrong.append('the first page of the PDF does not say it is the print copy and give the address')
    pictures = sum(len(page_.images) for page_ in reader.pages)
    if pictures < len(ctx['figures']):
        wrong.append(f'the PDF holds {pictures} pictures for {len(ctx["figures"])} figures')

    with zipfile.ZipFile(stage / f'{stem}-bundle.zip') as archive:
        names = archive.namelist()
    for figure in ctx['figures']:
        for needed in (f'code/{figure["name"]}.py', figure['data']):
            if f'{stem}-bundle/{needed}' not in names:
                wrong.append(f'the bundle is missing {needed}')
    return wrong


# ---------------------------------------------------------------- publish


def publish(article: pathlib.Path, published: pathlib.Path, reviews: pathlib.Path,
            rebuild: bool = False, need_doi: bool = True, quiet: bool = False) -> pathlib.Path:
    say = (lambda *_: None) if quiet else print
    article = article.resolve()
    published = published.resolve()
    real = published == REAL_PUBLISHED
    journal = yaml.safe_load((ROOT / 'journal.yml').read_text(encoding='utf-8'))
    ctx, body, warnings = understand(article, journal, real, need_doi and real)
    for line in warnings:
        say(f'note: {line}')
    home = published / ctx['id']
    target = home / f'v{ctx["n"]}'

    # The freeze rule, before anything is built.
    if target.exists():
        if rebuild and not real:
            shutil.rmtree(target)
        elif rebuild:
            raise Refused(f'{target} is a published version. A published version is never rebuilt.')
        else:
            raise Refused(
                f'{target.relative_to(ROOT) if target.is_relative_to(ROOT) else target} already exists. A published '
                'version never changes: a change to the article is a new version. Add the next entry under '
                '`versions` in the front matter, with its date and what changed, and build again.'
            )
    for earlier in range(1, ctx['n']):
        if not (home / f'v{earlier}' / 'version.json').is_file():
            raise Refused(f'version {ctx["n"]} cannot be built: version {earlier} was never published in {home}')
    broken = [line for folder in version_folders(published) if folder.parent == home for line in verify_version(folder)]
    if broken:
        raise Refused('an earlier version is not as it was frozen; nothing was built:\n' + '\n'.join(f'  - {b}' for b in broken))

    quarto = find_quarto()
    versions = tool_versions(quarto)
    status = read_status(reviews, ctx['id'])

    # A clean working copy of the article; the source folder is never written to.
    work = WORK / ctx['stem']
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    for folder in ('data', 'code'):
        if (article / folder).is_dir():
            shutil.copytree(article / folder, work / folder, ignore=shutil.ignore_patterns('__pycache__', '.DS_Store'))
        else:
            (work / folder).mkdir()
    if ctx['bibliography']:
        shutil.copyfile(article / ctx['bibliography'], work / ctx['bibliography'])

    say(f'{ctx["id"]} version {ctx["n"]}: {ctx["title"]}')
    for figure in ctx['figures']:
        done = run([sys.executable, str(PIPELINE / 'draw.py'), str(work), figure['name']], work)
        if done.returncode != 0:
            raise Refused(f'figure {figure["name"]} could not be drawn:\n{(done.stdout + done.stderr).strip()}')
        say(f'  figure   {figure["name"]}: figures/{figure["name"]}.json and .png, from {figure["data"]}')

    import plotly

    assets = work / 'assets'
    shutil.copytree(THEME / 'fonts', assets / 'fonts')
    shutil.copyfile(THEME / 'site.css', assets / 'site.css')
    shutil.copyfile(THEME / 'favicon.svg', assets / 'favicon.svg')
    shutil.copyfile(PIPELINE / 'article.css', assets / 'article.css')
    palette = json.loads((PIPELINE / 'palette.json').read_text(encoding='utf-8'))['series']
    script = (PIPELINE / 'article.js').read_text(encoding='utf-8')
    script = script.replace('/*PALETTE*/ { light: [], dark: [] }', json.dumps(palette))
    (assets / 'article.js').write_text(script, encoding='utf-8')
    if ctx['figures']:
        shutil.copyfile(pathlib.Path(plotly.__file__).parent / 'package_data' / 'plotly.min.js', assets / 'plotly.min.js')
    for name in ('page-template.html', 'figures.lua'):
        shutil.copyfile(PIPELINE / name, work / name)
    shutil.copyfile(PIPELINE / 'print' / 'typst-template.typ', work / 'typst-template.typ')
    for name, text in print_parts(ctx).items():
        (work / name).write_text(text, encoding='utf-8')
    (work / '_article.qmd').write_text(quarto_source(ctx, body), encoding='utf-8')
    stem = ctx['stem']
    (work / f'{stem}.bib').write_text(ctx['bibtex'], encoding='utf-8')
    (work / f'{stem}.ris').write_text(ctx['ris'], encoding='utf-8', newline='')

    def write_parts(variant: str, sizes: dict[str, int]) -> None:
        front, back = shell_html(ctx, variant, status, sizes).split(BODY_MARK)
        (work / f'_head-{variant}.html').write_text(head_html(ctx, variant), encoding='utf-8')
        (work / f'_front-{variant}.html').write_text(front, encoding='utf-8')
        (work / f'_back-{variant}.html').write_text(back, encoding='utf-8')

    # The bundle, the print copy and the one-file copy first, so the page can state their sizes.
    bundle(ctx, work, work / f'{stem}-bundle.zip', versions)
    say(f'  bundle   {stem}-bundle.zip')

    render(quarto, work, 'print', f'{stem}.pdf')
    # Compiled again without the machine's own fonts, so the same source prints the same anywhere.
    done = run([str(quarto), 'typst', 'compile', '_article.typ', f'{stem}.pdf', '--ignore-system-fonts'], work)
    if done.returncode != 0:
        raise Refused(f'Typst could not compile the print copy:\n{done.stderr.strip()[-2000:]}')
    say(f'  print    {stem}.pdf')

    write_parts('single', {})
    render(quarto, work, 'single', f'{stem}.html')
    finish_html(work / f'{stem}.html', work)
    say(f'  one file {stem}.html')

    sizes = {name: (work / name).stat().st_size for name in (f'{stem}.html', f'{stem}.pdf', f'{stem}-bundle.zip')}
    write_parts('page', sizes)
    render(quarto, work, 'page', 'index.html')
    finish_html(work / 'index.html', work)
    say('  page     index.html')

    # Stage the version, check it, and only then put it in place.
    stage = WORK / f'{stem}.staged'
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir()
    for name in ('index.html', f'{stem}.html', f'{stem}.pdf', f'{stem}-bundle.zip', f'{stem}.bib', f'{stem}.ris'):
        shutil.copyfile(work / name, stage / name)
    for folder in ('assets', 'figures', 'data', 'code'):
        if (work / folder).is_dir() and any((work / folder).iterdir()):
            shutil.copytree(work / folder, stage / folder)
    record = {
        'id': ctx['id'], 'version': ctx['n'], 'date': ctx['date'], 'first_published': ctx['first'], 'note': ctx['note'],
        'title': ctx['title'], 'type': ctx['kind'], 'evidence': ctx['evidence_key'],
        'authors': [{'name': a['name'], 'orcid': a['orcid'] or ''} for a in ctx['authors']],
        'doi': ctx['doi'], 'doi_latest': ctx['doi_latest'], 'issn': ctx['issn'], 'volume': ctx['volume'],
        'address': ctx['address'], 'sample': ctx['sample'],
        'outputs': {'page': 'index.html', 'single_file': f'{stem}.html', 'pdf': f'{stem}.pdf', 'bundle': f'{stem}-bundle.zip'},
        'built': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'built_with': versions,
    }
    (stage / 'version.json').write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    wrong = inspect(stage, ctx)
    if wrong:
        raise Refused(f'the build of {stem} failed its checks and was not published (it is in {stage}):\n'
                      + '\n'.join(f'  - {line}' for line in wrong))

    write_manifest(stage)
    home.mkdir(parents=True, exist_ok=True)
    stage.rename(target)
    write_record(published, reviews, ctx['id'], journal)
    shown = target.relative_to(ROOT) if target.is_relative_to(ROOT) else target
    say(f'frozen: {shown}/ ({len(tree(target))} files; '
        f'one file {human_size(sizes[f"{stem}.html"])}, PDF {human_size(sizes[f"{stem}.pdf"])}, bundle {human_size(sizes[f"{stem}-bundle.zip"])})')
    return target


# ---------------------------------------------------------------- commands


def cmd_publish(args: argparse.Namespace) -> int:
    article = pathlib.Path(args.article).resolve()
    root = article.parent.parent
    published = pathlib.Path(args.published).resolve() if args.published else root / 'published'
    reviews = pathlib.Path(args.reviews).resolve() if args.reviews else root / 'reviews'
    if article.parent.name != 'articles':
        raise Refused(f'{article} is not in an articles/ folder. Real articles live in articles/<id>/; the sample in tests/articles/.')
    target = publish(article, published, reviews, rebuild=args.rebuild, need_doi=not args.no_doi)
    if published == REAL_PUBLISHED:
        print('\nNext, by hand: deposit the four outputs on Zenodo under the reserved DOI, open the review thread,\n'
              'set reviews/<id>/status.yml, commit published/ and push. See README.md.')
    else:
        shown = target.relative_to(ROOT) if target.is_relative_to(ROOT) else target
        print(f'\nA test build. To check it in a browser:  .venv/bin/python scripts/browser-check.py {shown}')
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    journal = yaml.safe_load((ROOT / 'journal.yml').read_text(encoding='utf-8'))
    published = pathlib.Path(args.published).resolve() if args.published else REAL_PUBLISHED
    reviews = pathlib.Path(args.reviews).resolve() if args.reviews else REAL_REVIEWS
    record = write_record(published, reviews, args.id, journal)
    print(f'{args.id}: {record["status"]}, {len(record["versions"])} version(s), {len(record["reviews"])} review(s) recorded')
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    roots = [pathlib.Path(args.published).resolve()] if args.published else [REAL_PUBLISHED, TEST_PUBLISHED]
    folders = [folder for root in roots if root.is_dir() for folder in version_folders(root)]
    wrong = [line for folder in folders for line in verify_version(folder)]
    for line in wrong:
        print(line)
    print(f'verify: {len(folders)} frozen version(s), {len(wrong)} difference(s)')
    return 1 if wrong else 0


def cmd_selftest(args: argparse.Namespace) -> int:
    """Builds the sample as version 1, revises it, builds version 2, and proves that version 1
    did not change by a byte and cannot be built again."""
    stage = ROOT / '_build' / 'selftest' / 'articles' / '0000-000'
    if stage.parent.parent.exists():
        shutil.rmtree(stage.parent.parent)
    if TEST_PUBLISHED.exists():
        shutil.rmtree(TEST_PUBLISHED)
    shutil.copytree(SAMPLE, stage, ignore=shutil.ignore_patterns('__pycache__', '.DS_Store'))
    passed: list[str] = []

    def check(what: str, ok: bool, detail: str = '') -> None:
        passed.append(what) if ok else None
        print(f'  {"ok  " if ok else "FAIL"}  {what}' + (f': {detail}' if detail and not ok else ''))
        if not ok:
            raise Refused(f'selftest failed: {what}')

    print('1. Version 1 of the sample, from source')
    v1 = publish(stage, TEST_PUBLISHED, TEST_REVIEWS)
    before = tree(v1)
    manifest_before = (v1 / 'MANIFEST.sha256').read_bytes()
    check('the four outputs exist', all((v1 / name).is_file() for name in ('index.html', '0000-000-v1.html', '0000-000-v1.pdf', '0000-000-v1-bundle.zip')))

    print('2. Building version 1 again is refused')
    try:
        publish(stage, TEST_PUBLISHED, TEST_REVIEWS, quiet=True)
        check('a second build of version 1 is refused', False)
    except Refused as refusal:
        check('a second build of version 1 is refused', 'never changes' in str(refusal))
    check('version 1 is untouched by the refused build', tree(v1) == before)

    print('3. The article is revised (text, data and a figure change) and built as version 2')
    shutil.copytree(SAMPLE_REVISION, stage, dirs_exist_ok=True)
    v2 = publish(stage, TEST_PUBLISHED, TEST_REVIEWS)
    after = tree(v1)
    check('version 2 exists beside version 1', v2.name == 'v2' and v2.parent == v1.parent)
    check('every file of version 1 is byte for byte what it was', after == before,
          f'{sorted(set(before.items()) ^ set(after.items()))[:4]}')
    check("version 1's manifest is unchanged", (v1 / 'MANIFEST.sha256').read_bytes() == manifest_before)
    check('version 1 still matches its manifest', not verify_version(v1))
    check('version 2 matches its manifest', not verify_version(v2))
    check('the two versions differ where the article changed',
          sha256(v1 / 'figures' / 'response.png') != sha256(v2 / 'figures' / 'response.png')
          and sha256(v1 / 'data' / 'response.csv') != sha256(v2 / 'data' / 'response.csv'))
    record = json.loads((v1.parent / 'record.json').read_text(encoding='utf-8'))
    check('the record lists both versions and names version 2 the latest',
          record['latest'] == 2 and [v['version'] for v in record['versions']] == [1, 2])
    check("the article's own address forwards to version 2", 'url=v2/' in (v1.parent / 'index.html').read_text(encoding='utf-8'))

    print('4. A change to a frozen file is caught')
    victim = v1 / 'data' / 'response.csv'
    original = victim.read_bytes()
    victim.write_bytes(original + b'1,1\n')
    caught = verify_version(v1)
    victim.write_bytes(original)
    check('verify reports a changed file', any('changed since it was frozen' in line for line in caught))
    check('and passes again once it is restored', not verify_version(v1))

    print('5. The rules the build enforces')
    try:
        publish(stage, REAL_PUBLISHED, REAL_REVIEWS, quiet=True)
        check('a sample is refused in published/', False)
    except Refused as refusal:
        check('a sample is refused in published/', 'sample is never published' in str(refusal))
    check('no sample reached published/', not (REAL_PUBLISHED / '0000-000').exists())
    journal = yaml.safe_load((ROOT / 'journal.yml').read_text(encoding='utf-8'))
    ctx, _, _ = understand(stage, {**journal, 'issn': '0000-0000'}, real=False, need_doi=False)
    names = [name for name, _ in highwire(ctx)]
    check('with an ISSN set, the head carries every citation tag of the spec',
          names == ['citation_title', 'citation_author', 'citation_author', 'citation_publication_date',
                    'citation_journal_title', 'citation_issn', 'citation_volume', 'citation_firstpage',
                    'citation_doi', 'citation_pdf_url'])
    try:
        orcid_id('0000-0002-1825-0098', 'A test author')
        check('an ORCID iD with a typing error is refused', False)
    except Refused:
        check('an ORCID iD with a typing error is refused', True)

    print('6. The data and code bundle, on its own')
    unpacked = ROOT / '_build' / 'selftest' / 'bundle'
    with zipfile.ZipFile(v2 / '0000-000-v2-bundle.zip') as archive:
        archive.extractall(unpacked)
    alone = unpacked / '0000-000-v2-bundle'
    done = run([sys.executable, 'draw.py', '.', 'response'], alone)
    check('the bundle draws its figure again from nothing but its own files',
          done.returncode == 0 and (alone / 'figures' / 'response.png').is_file(), (done.stdout + done.stderr)[-300:])
    check('the figure it draws is the one in the published version',
          (alone / 'figures' / 'response.json').read_bytes() == (v2 / 'figures' / 'response.json').read_bytes())

    if not args.no_browser:
        print('7. Both versions, in a browser')
        for version in (v1, v2):
            done = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'browser-check.py'), str(version)], cwd=ROOT, check=False)
            check(f'the browser checks pass for {version.name}', done.returncode == 0)

    print(f'\nselftest: {len(passed)} checks passed. The sample is in tests/published/ (not committed, not on the site).')
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('publish', help='build and freeze one version of an article')
    build.add_argument('article', help='the article folder: articles/<id>, or tests/articles/0000-000 for the sample')
    build.add_argument('--rebuild', action='store_true', help='replace a test build; refused for a published version')
    build.add_argument('--no-doi', action='store_true', help='build a real article without its DOIs (it can never gain them)')
    build.add_argument('--published', help='where versions are frozen (default: published/ beside articles/)')
    build.add_argument('--reviews', help='where review status is read (default: reviews/ beside articles/)')
    build.set_defaults(run=cmd_publish)
    record = commands.add_parser('record', help="rewrite an article's record from its versions and review status")
    record.add_argument('id')
    record.add_argument('--published')
    record.add_argument('--reviews')
    record.set_defaults(run=cmd_record)
    verify = commands.add_parser('verify', help='check every frozen version against its manifest')
    verify.add_argument('--published')
    verify.set_defaults(run=cmd_verify)
    selftest = commands.add_parser('selftest', help='build the sample twice and prove the freeze rule')
    selftest.add_argument('--no-browser', action='store_true', help='skip the checks that need Chrome')
    selftest.set_defaults(run=cmd_selftest)
    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except Refused as refusal:
        print(f'\nrefused: {refusal}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
