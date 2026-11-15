#!/usr/bin/env python3
"""Deposits a version of an article on Zenodo, in the journal's community.

    scripts/zenodo.py reserve articles/2026-001   before the build: starts a draft deposit and
                                                  prints the two DOIs to put in the front matter
    scripts/zenodo.py upload  articles/2026-001   after the build: puts the frozen outputs of the
                                                  version in the draft, with the article's facts
    scripts/zenodo.py show    articles/2026-001   what Zenodo holds for the draft
    scripts/zenodo.py publish articles/2026-001   publishes the deposit and adds it to the journal's
                                                  community. It cannot be undone: a published
                                                  record is never deleted

The token is read from the environment variable ZENODO_TOKEN, or from the file named in
ZENODO_TOKEN_FILE (default ~/.config/hertzforge/zenodo_token). It needs the scopes
deposit:write and deposit:actions. It is never printed.

`reserve` handles a first version. A later version of an article that is already on Zenodo
starts from the record of the version before it (Zenodo's "New version"), which this script
does when the front matter's `doi_latest` is already set.

Only the Python standard library and PyYAML (already in the build environment) are used.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
API = os.environ.get('ZENODO_API', 'https://zenodo.org/api')
PREFIX = '10.5281/zenodo.'


def token() -> str:
    value = os.environ.get('ZENODO_TOKEN', '').strip()
    if not value:
        path = pathlib.Path(os.environ.get('ZENODO_TOKEN_FILE', '~/.config/hertzforge/zenodo_token')).expanduser()
        if not path.is_file():
            sys.exit(f'zenodo: no token. Put one in {path} (scopes deposit:write and deposit:actions), or set ZENODO_TOKEN.')
        value = path.read_text(encoding='utf-8').strip()
    if not value:
        sys.exit('zenodo: the token is empty.')
    return value


def call(method: str, url: str, body: object = None, raw: bytes | None = None, kind: str = 'application/json',
         fatal: bool = True) -> dict:
    if not url.startswith('http'):
        url = API + url
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header('Authorization', f'Bearer {token()}')
    if data is not None:
        request.add_header('Content-Type', kind)
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            text = response.read().decode('utf-8')
    except urllib.error.HTTPError as error:
        detail = error.read().decode('utf-8', 'replace')[:1500]
        if not fatal:
            return {'_error': f'{error.code}: {detail[:200]}'}
        sys.exit(f'zenodo: {method} {url} answered {error.code}.\n{detail}')
    return json.loads(text) if text.strip() else {}


def front_matter(article: pathlib.Path) -> dict:
    text = (article / 'article.md').read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        sys.exit(f'zenodo: {article}/article.md has no front matter.')
    return yaml.safe_load(text[4:text.index('\n---\n', 4)])


def journal() -> dict:
    return yaml.safe_load((ROOT / 'journal.yml').read_text(encoding='utf-8'))


def family_first(name: str) -> str:
    given, _, family = name.strip().rpartition(' ')
    return f'{family}, {given}' if given else family


def deposit_id(front: dict) -> str:
    doi = str(front.get('doi') or '')
    if not doi.startswith(PREFIX):
        sys.exit('zenodo: the front matter has no Zenodo DOI for this version. Run `reserve` first and put the DOIs in.')
    return doi[len(PREFIX):]


def metadata(front: dict) -> dict:
    facts = journal()
    article_id, number = str(front['id']), int(front['version'])
    date = str(front['date'])
    volume = int(date[:4]) - int(facts['first_volume_year']) + 1
    address = f'{facts["site"]}{facts["path"]}/{article_id}/'
    abstract = ' '.join(str(front['abstract']).split())
    description = (
        f'<p>{abstract}</p>'
        f'<p>{facts["title"]} {volume}, {article_id}, version {number}. The version of record is the article page at '
        f'<a href="{address}v{number}/">{address}v{number}/</a>. This deposit holds that page, the article in one '
        'file (it opens without a network connection), the PDF print copy, and the bundle of the data behind every '
        'figure and the code that draws it. The article is reviewed in public after publication; its reviews, its '
        f'review status and any later version are at <a href="{address}">{address}</a>.</p>'
    )
    creators = []
    for author in front['authors']:
        creator = {'name': family_first(author['name'])}
        orcid = str(author.get('orcid') or '').rsplit('/', 1)[-1]
        if orcid:
            creator['orcid'] = orcid
        creators.append(creator)
    return {
        'upload_type': 'publication',
        'publication_type': 'article',
        'title': str(front['title']),
        'creators': creators,
        'description': description,
        'publication_date': date,
        'access_right': 'open',
        'license': 'cc-by-4.0',
        'language': 'eng',
        'version': str(number),
        'journal_title': facts['title'],
        'journal_volume': str(volume),
        'journal_pages': article_id,
        'communities': [{'identifier': facts['zenodo_community']}],
        'related_identifiers': [
            {'identifier': f'{address}v{number}/', 'relation': 'isIdenticalTo', 'resource_type': 'publication-article', 'scheme': 'url'},
        ],
        'notes': 'Text, figures and data are under CC BY 4.0. Code in the bundle is under the MIT license.',
    }


def cmd_reserve(article: pathlib.Path) -> None:
    front = front_matter(article)
    if front.get('doi'):
        sys.exit(f'zenodo: this version already has a DOI in its front matter ({front["doi"]}).')
    latest = str(front.get('doi_latest') or '')
    if latest:
        # A later version: start it from the newest published version, which the article's
        # record names.
        record = json.loads((ROOT / 'published' / str(front['id']) / 'record.json').read_text(encoding='utf-8'))
        previous = str(record['versions'][-1]['doi'])[len(PREFIX):]
        started = call('POST', f'/deposit/depositions/{previous}/actions/newversion')
        newest = started.get('links', {}).get('latest_draft')
        draft = call('GET', newest) if newest else started
        if str(draft['id']) == previous:
            sys.exit('zenodo: Zenodo did not start a new version. Nothing else was done; look at the record on Zenodo.')
        if f'{PREFIX}{draft["conceptrecid"]}' != latest:
            sys.exit(f'zenodo: the new draft belongs to {PREFIX}{draft["conceptrecid"]}, not {latest}. Look at it on Zenodo.')
    else:
        draft = call('POST', '/deposit/depositions', {})
    reserved = draft['metadata']['prereserve_doi']['doi']
    held = call('POST', f'/records/{draft["id"]}/draft/pids/doi').get('pids', {}).get('doi', {}).get('identifier')
    if held and held != reserved:
        sys.exit(f'zenodo: the draft reserved {held}, not {reserved}. Nothing else was done; look at the draft on Zenodo.')
    print(f'Draft deposit {draft["id"]} started. It is not published, and can still be deleted.')
    print(f'  doi: "{reserved}"')
    print(f'  doi_latest: "{PREFIX}{draft["conceptrecid"]}"')
    print(f'  on Zenodo: {draft["links"].get("html", "")}')


def cmd_upload(article: pathlib.Path) -> None:
    front = front_matter(article)
    article_id, number = str(front['id']), int(front['version'])
    folder = ROOT / 'published' / article_id / f'v{number}'
    stem = f'{article_id}-v{number}'
    outputs = [('index.html', f'{stem}-page.html'), (f'{stem}.html', f'{stem}.html'), (f'{stem}.pdf', f'{stem}.pdf'),
               (f'{stem}-bundle.zip', f'{stem}-bundle.zip')]
    missing = [name for name, _ in outputs if not (folder / name).is_file()]
    if missing:
        sys.exit(f'zenodo: {folder} is missing {", ".join(missing)}. Build and freeze the version first.')
    number_on_zenodo = deposit_id(front)
    draft = call('GET', f'/deposit/depositions/{number_on_zenodo}')
    if draft.get('submitted'):
        sys.exit('zenodo: this deposit is already published. Nothing was changed.')
    expected = f'{PREFIX}{draft["conceptrecid"]}'
    if str(front.get('doi_latest')) != expected:
        sys.exit(f'zenodo: doi_latest in the front matter is {front.get("doi_latest")}, and the deposit says {expected}.')
    held = {entry['filename']: entry for entry in draft.get('files', [])}
    for name in held:
        if name not in {as_name for _, as_name in outputs}:
            call('DELETE', f'/deposit/depositions/{number_on_zenodo}/files/{held[name]["id"]}')
            print(f'  removed  {name}')
    for name, as_name in outputs:
        data = (folder / name).read_bytes()
        call('PUT', f'{draft["links"]["bucket"]}/{urllib.parse.quote(as_name)}', raw=data, kind='application/octet-stream')
        print(f'  uploaded {as_name} ({len(data):,} bytes)')
    call('PUT', f'/deposit/depositions/{number_on_zenodo}', {'metadata': metadata(front)})
    print('  facts set: title, authors, abstract, date, license, journal, community')
    print(f'Look at the draft before publishing it: {draft["links"].get("html", "")}')


def cmd_show(article: pathlib.Path) -> None:
    draft = call('GET', f'/deposit/depositions/{deposit_id(front_matter(article))}')
    meta = draft.get('metadata', {})
    print(f'deposit {draft["id"]}: {"published" if draft.get("submitted") else "draft, not published"}')
    print(f'  title: {meta.get("title", "")}')
    print(f'  authors: {"; ".join(c.get("name", "") + (" (" + c["orcid"] + ")" if c.get("orcid") else "") for c in meta.get("creators", []))}')
    print(f'  date: {meta.get("publication_date", "")}   license: {meta.get("license", "")}   version: {meta.get("version", "")}')
    print(f'  journal: {meta.get("journal_title", "")} {meta.get("journal_volume", "")}, {meta.get("journal_pages", "")}')
    print(f'  doi: {meta.get("prereserve_doi", {}).get("doi", "")}   all versions: {PREFIX}{draft.get("conceptrecid", "")}')
    for entry in draft.get('files', []):
        print(f'  file: {entry["filename"]} ({entry["filesize"]:,} bytes)')
    print(f'  on Zenodo: {draft.get("links", {}).get("html", "")}')


def cmd_publish(article: pathlib.Path) -> None:
    number_on_zenodo = deposit_id(front_matter(article))
    draft = call('GET', f'/deposit/depositions/{number_on_zenodo}')
    if draft.get('submitted'):
        sys.exit('zenodo: this deposit is already published.')
    if len(draft.get('files', [])) < 4:
        sys.exit('zenodo: the draft does not hold the four outputs. Run `upload` first.')
    done = call('POST', f'/deposit/depositions/{number_on_zenodo}/actions/publish')
    print(f'Published: https://doi.org/{done.get("doi", "")}')
    print(f'  all versions: https://doi.org/{done.get("conceptdoi", "")}')
    print(f'  record: {done.get("links", {}).get("record_html", done.get("links", {}).get("html", ""))}')
    # The deposit named the journal's community, and Zenodo takes the record of an owner or
    # curator of the community in when it is published. Say whether it is there.
    community = journal()['zenodo_community']
    held = call('GET', f'/records/{number_on_zenodo}/communities', fatal=False)
    slugs = [hit.get('slug', '') for hit in held.get('hits', {}).get('hits', [])]
    if community in slugs:
        print(f'  community: {community}')
    else:
        print(f'  community: not in "{community}" yet. On the record\'s Zenodo page: Communities, Submit to community.')


def main() -> None:
    parser = argparse.ArgumentParser(description='Deposit a version of an article on Zenodo.')
    parser.add_argument('action', choices=['reserve', 'upload', 'show', 'publish'])
    parser.add_argument('article', help='the article folder, for example articles/2026-001')
    arguments = parser.parse_args()
    article = pathlib.Path(arguments.article).resolve()
    if not (article / 'article.md').is_file():
        sys.exit(f'zenodo: {article} has no article.md.')
    {'reserve': cmd_reserve, 'upload': cmd_upload, 'show': cmd_show, 'publish': cmd_publish}[arguments.action](article)


if __name__ == '__main__':
    main()
