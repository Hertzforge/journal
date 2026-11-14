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
| `articles/<id>/` | An article's source, with `data/` (the data behind every figure) and `code/` (the code that draws them) |
| `published/<id>/v<n>/` | Version n as it was built: the page, the single-file download, the PDF and the bundle. Never rebuilt, never edited |
| `reviews/<id>/` | The review record of each article, exported from its thread so it outlives the discussion |
| `people/` | One record per author and reviewer: name and ORCID iD |
| `policies/` | The policies, the guide for authors, the guide for reviewers and the editors' checklist |
| `templates/` | The article template and the review template |
| `scripts/check-names.py` | The gate run before every push |

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

## Licenses

| What | License | Copyright |
|---|---|---|
| Text, figures, data and reviews | Creative Commons Attribution 4.0 International, in `LICENSE` | The authors of each article and review |
| Code in an article's bundle, and this repository's own scripts | MIT, in `LICENSE-CODE` | The authors of that code |

The journal holds no copyright in any article. Hertzforge is the venue, never the author.

## Status

Not yet open. No article has been published, the build that turns an article's source into its
four outputs is not chosen (Quarto is the candidate and has not been tried), and the journal has
no ISSN yet.
