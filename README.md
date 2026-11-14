# Hertzforge Journal

Research on vibration and shock testing, multi-input multi-output control and structural dynamics
analysis, published as interactive articles with their data and code.

Articles go live when they are ready and are reviewed in public afterward, by signed reviews
posted beside each article. Authors keep their copyright and their credit. Every article is free
to read, reuse and cite. There are no fees to publish or to read.

**Editors:** Kevin Cross and Brandon Zwink.

This repository is the journal's record: the source of every article, every published version
frozen as it was built, the reviews, and the policies. The journal is read at
hertzforge.com/journal.

## What Is Where

| Path | What it holds |
|---|---|
| `articles/<id>/` | An article's source: `article.md`, `references.bib`, `data/` (the data behind every figure), `code/` (the code that draws them) and, where an article supplies pictures, `figures/` |
| `published/<id>/v<n>/` | Version n as it was built: the page, the one-file copy, the PDF and the bundle. Never rebuilt, never edited |
| `published/<id>/record.json` | What changes after a version is frozen: which versions exist, the review status, the reviews |
| `reviews/<id>/` | The review record of each article, exported from its thread so it outlives the discussion, and `status.yml`, its review state |
| `people/` | One record per author and reviewer: name and ORCID iD |
| `policies/` | The policies, the guide for authors, the guide for reviewers and the editors' checklist |
| `templates/` | The article template and the review template |
| `journal.yml` | Facts every article repeats: the journal's title, its address, its ISSN once assigned. Also the list of article types: one line there adds a type |
| `scripts/publish` | The one command that builds and freezes a version (`scripts/journal.py` does the work) |
| `scripts/setup.sh` | Installs what the build needs, without administrator rights |
| `scripts/browser-check.py` | Opens a built version in a browser and checks what only a browser can show |
| `scripts/check-names.py` | The gate run before every push: names, licenses, and that no published version has changed |
| `scripts/sync-theme.py` | Refreshes `theme/` from a build of the website |
| `pipeline/` | What the build is made of: the page frame, its styles and script, the print layout, the figure runner, the figure colors, the pinned tools |
| `theme/` | A copy of the website's stylesheet, fonts, header and footer. Each version is frozen with the copy it was built with |
| `tests/` | The sample article, clearly marked as one, and its revision. Its builds are never committed and never published |

An article's identifier is `<year>-<nnn>`: the year it was first published and a running number,
for example `2026-001`. Titles are not in addresses, so a retitled article keeps its address.
Volume 1 is 2026.

## Publishing an Article

1. **Submit.** Copy `templates/article/` to `articles/<working-name>/`, write the article, add
   its data and code, and open a pull request. You do not need to use Hertzforge.
2. **The editors check** that it is in scope, complete, properly licensed and reproducible as
   submitted (`policies/EDITORS.md`). They do not judge whether it is right.
3. **It is published** as version 1 with the status Review open: it gets its identifier, each
   version is deposited on Zenodo with a DOI, and its review thread opens.
4. **Review happens in public.** Invited reviewers post signed reviews in the thread, using
   `templates/REVIEW.md`. The authors answer, revise as a new version, or both.

Changes to an article need its authors' approval. Nobody, the editors included, edits another
author's article beyond the publication checks.

## Building a Version

Every version of an article has four outputs, built once from one source and frozen:

1. **The article page,** in the site's style. This is the version of record.
2. **The article in one file,** for download: interactive, with the plotting library, the
   fonts and the figures written into it. It asks nothing of any server, so it opens offline and
   can be carried onto a closed network.
3. **A PDF print copy** from the same source, with a static picture of each figure. Its first
   page says it is the print copy and gives the address and DOI of the interactive version.
4. **A data and code bundle:** the data behind every figure and the code that draws it, with
   what is needed to run it again.

### Once on a Machine

```bash
scripts/setup.sh
```

It installs Quarto, at the version pinned in `pipeline/tools.json`, from its release tarball
(checked against the recorded checksum) into `~/dev/tools`, and a Python environment in `.venv`
from `requirements.lock`. No administrator rights are needed. The machine also needs a Chrome or
Chromium browser, which renders each figure's static picture and runs the browser checks.

### One Command

```bash
scripts/publish articles/2026-001
```

It reads `articles/2026-001/article.md`, draws every figure from `code/` and `data/`, builds
the four outputs for the version named in the article's front matter, checks them, and freezes
them in `published/2026-001/v<n>/` with a manifest of every file's hash. Then it rewrites the
article's record and the page at the article's own address, which forwards to the latest
version.

It refuses, and builds nothing, when:

- that version is already published. A published version never changes; set `version` to the
  next number and build again;
- an earlier version is missing, or is no longer what its manifest says;
- the article lacks a required part: its number, a title, authors, a type, an evidence level,
  an abstract, a date, a note of what changed, and the closing sections in order (How This Was
  Made, Acknowledgments, References);
- a co-authored article has an author without CRediT roles;
- an ORCID iD fails its check digit;
- a comment (`<!-- ... -->`) or a marked gap (TODO, PLACEHOLDER, "[... to be stated]") is still
  in the text;
- a figure has no alternative text, or one the build draws has no data file;
- a figure's series differ only by color, or a figure would fetch anything from another site;
- the version has no DOI. Reserve the DOIs first (below); `--no-doi` builds without them.

And it refuses to freeze what it built when the page's parts are missing or out of order, the
citation tags in the head are not the ones expected, the one-file copy would fetch anything, or
the PDF's first page does not say what it is.

### Looking at an Article Before It Is Published

```bash
scripts/publish path/to/the/article --preview
```

A preview builds the same four outputs into `_build/preview/` and freezes nothing. It works on
any folder, wherever it is and whatever it is called, at any stage: with no number, no date and
no DOIs yet. The page is marked as a preview. After building, it lists everything still owed
before the article can be published, with the line of `article.md` where that helps. The
article's folder is only read.

### Publishing, Step by Step

1. **Give the article its identifier** and move its source to `articles/<id>/`. Set `id`. The
   number is assigned here, by the editors, never taken from a working folder's name.
2. **Reserve the DOIs on Zenodo** before building. Start the deposit in the journal's community
   (`hertzforge-journal`) as a journal article; Zenodo reserves the DOI of this version and the
   DOI that always gives the latest version. Put them in the front matter (`doi`,
   `doi_latest`). They are printed on the page and in the PDF, and a frozen version cannot be
   given them afterward.
3. **Set the date** of the version, and its note.
4. **Build:** `scripts/publish articles/<id>`.
5. **Look at it:** `.venv/bin/python scripts/browser-check.py published/<id>/v<n>`, and open the
   page, the one-file copy and the PDF yourself.
6. **Commit** `articles/<id>/` and `published/<id>/` and push. The gate runs first.
7. **Deposit:** upload the four outputs from `published/<id>/v<n>/` to the reserved deposit and
   publish it.
8. **Open the review thread,** put its address in `reviews/<id>/status.yml`, and run
   `.venv/bin/python scripts/journal.py record <id>`.
9. **The website** takes the article in at its next build: it copies `published/` as it is, and
   lists the article on the journal's home page from its record.

### A New Version

Change the article in `articles/<id>/`, set `version` to the next number with its `date`, its
`doi` and a `note` of what changed (a line, or paragraphs), and run `scripts/publish
articles/<id>` again. It writes `published/<id>/v<n+1>/` and leaves every earlier version as it
was. The new version's history is the notes of the versions already frozen, followed by its
own. Each earlier version's page then says that a later one exists, because pages read the
article's record; no published file changes.

### After a Review

Reviews and the review status are not part of any version. List the review in
`reviews/<id>/status.yml`, set the status, and run
`.venv/bin/python scripts/journal.py record <id>`. Every version's page shows the new state.

### Checking That Nothing Has Changed

```bash
.venv/bin/python scripts/journal.py verify
```

It compares every published version with the manifest written when it was built. The gate runs
the same check before every push, and also refuses a push that changes or removes a file of a
version the remote already has.

### The Sample and the Self-Test

`tests/articles/0000-000/` is a sample article, marked as one on every page it produces. It
has numbered sections, a contents list, a wide table, a picture it supplies and a figure the
build draws. It exists to test the build and is never published: the build refuses it in `published/`, its
output goes to `tests/published/` (not committed), and the website leaves it out unless a test
build asks for it.

```bash
scripts/publish tests/articles/0000-000 --rebuild     # the sample's four outputs, from source
.venv/bin/python scripts/journal.py selftest          # the whole build, twice, and the freeze rule
```

The self-test builds the sample as version 1, lays its revision over it, builds version 2, and
checks that version 1 did not change by a byte and cannot be built again. It checks that an
article with gaps is refused for publication and built by a preview. Then it unpacks the bundle
on its own and redraws the figure from it, and runs the browser checks on both versions.

### What an Article May Hold

- **Sections of its own.** Only the closing sections are fixed: How This Was Made,
  Acknowledgments and References, last and in that order. An article may also write its own
  Contribution Statement (before them), Implemented In and Version History (after them); where
  it does not, the build writes the contribution statement from the authors' roles, and the
  version history from each version's note.
- **A contents list,** beside the text on a wide screen and folded above it on a narrow one. An
  article with five or more sections gets one; `contents:` in the front matter says otherwise.
- **Section numbers,** its own (written in the headings) or the build's (`number_sections: true`).
- **Tables of any width.** Each sits in its own frame, and a wide one scrolls inside it.
- **Two kinds of figure.** One the build draws from `code/<name>.py` is interactive on the page
  and in the one-file copy, with a static picture behind it. A picture the article supplies in
  `figures/` (a photograph, a drawing, a plot made elsewhere) is shown as it is. Both offer
  their data, their code and their picture.
- **Two ways to write a figure.** The journal's form is numbered and cross-referenced by the
  build. Plain Markdown, with the alternative text in the brackets and the caption in the next
  paragraph, is shown as the author wrote it.
- **References** from `references.bib`, cited by key, or a list written by hand.

### What the Build Is Made Of

Quarto converts the article (Markdown, cross-references, citations, equations as MathML, the
embedding of the one-file copy, and Typst for the PDF). Its own theme and scripts are switched
off; the page frame is the journal's. Figures are not drawn by cells in the document: each is
drawn by its file in `code/`, once, into an interactive figure and a static picture. The
journal's own rules (the parts of the page and their order, the citation tags, the freeze) are
in `scripts/journal.py`.

The tools are pinned in `pipeline/tools.json` and `requirements.lock`, with their licenses. No
part of the build, and nothing written into an article, is under GPL, AGPL or SSPL, with one
thing to know: Quarto carries Pandoc, which is under GPL and is run as a separate program.
Nothing of it is linked into the build or copied into an article.

When the website's look changes and the journal should follow, build the website and run
`python3 scripts/sync-theme.py`. Versions already published keep the look they were frozen with.

## Licenses

| What | License | Copyright |
|---|---|---|
| Text, figures, data and reviews | Creative Commons Attribution 4.0 International, in `LICENSE` | The authors of each article and review |
| Code in an article's bundle, and this repository's own scripts | MIT, in `LICENSE-CODE` | The authors of that code |

The journal holds no copyright in any article. Hertzforge is the venue, never the author.

## Status

Not yet open. No article has been published and the journal has no ISSN yet. The build is in
place and has been run end to end on the sample.
