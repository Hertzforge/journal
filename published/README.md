# Published Versions

`published/<id>/v<n>/` is version n of an article exactly as it was built: the page
(`index.html`), the one-file copy, the PDF, the data and code bundle, the citation files, what
the page loads, and `MANIFEST.sha256`, the hash of every file. A folder here is written once,
by `scripts/publish`, and is never rebuilt and never edited. A change to an article is a new
version in a new folder. `python scripts/journal.py verify` checks every version against its
manifest, and the gate refuses a push that changes one.

Beside the versions, `published/<id>/record.json` holds what changes after a version is frozen
(which versions exist, the review status, the reviews), and `published/<id>/index.html` forwards
the article's own address to its latest version. Both are rewritten by
`python scripts/journal.py record <id>`.

The website copies this folder into its `/journal/` section as it is.

| Article | Title | Authors | First published |
|---|---|---|---|
| `2026-001` | What Is a Good Multi-Shaker Test? A Proposed Practice for Judging MIMO Vibration and Shock Tests on Flexible Articles | Kevin Cross, Brandon Zwink | 2026-11-14 |
