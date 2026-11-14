# The Editors' Checklist

What an editor checks before an article is published, and what happens when it is. The editors
do not judge whether an article is right. Review does that, in public.

## Before Publishing

- [ ] **In scope:** vibration and shock testing, multi-input multi-output control, or structural
      dynamics analysis.
- [ ] **Complete:** title; authors with ORCID iDs; type; evidence level at the top; abstract;
      body; contribution statement if co-authored; how it was made; acknowledgments naming the
      sources of ideas; references; license line.
- [ ] **Reproducible as submitted:** every figure regenerates from the article's own `data/` and
      `code/`.
- [ ] **Licensed as the policies require:** nothing in the article or its bundle that cannot be
      published under CC BY 4.0 (text, figures, data) and MIT (code). No code from sources under
      GPL, AGPL or SSPL in the bundle.
- [ ] **No affiliation claimed.** Authors by name and ORCID iD. Published prior work and its
      institutions may be cited and credited by name.
- [ ] **No claim that Hertzforge supports hardware** beyond what it supports.
- [ ] **Figures read without color alone,** and every image has alternative text.
- [ ] **The gate passes** (`scripts/check-names.py`).

## Who Handles It

When one editor is an author, the other handles the article. When both are, reviewers come from
outside the author list and the article says its authors are the journal's editors.

## At Publication

1. Assign the identifier, `<year>-<nnn>`, and move the source to `articles/<id>/`. A preview
   (`scripts/publish <folder> --preview`) lists everything still owed at any time before this.
2. Reserve the DOIs on Zenodo, in the journal's community (`hertzforge-journal`), before
   building: start the deposit as a journal article and take the DOI it reserves for this
   version and the one that always gives the latest version. Put both in the article's front
   matter, with the date. They are printed on the page and in the PDF, and a frozen version
   cannot be given them afterward.
3. Build version 1 and freeze it under `published/<id>/v1/`: `scripts/publish articles/<id>`.
   The build checks the article against this list where it can, and refuses to freeze a version
   that fails. Look at the page, the one-file copy and the PDF.
4. Upload the four outputs to the reserved deposit, with the authors' ORCID iDs and the license,
   and publish it.
5. Open the article's review thread, put its address in `reviews/<id>/status.yml` with the
   status Review open, and run `python scripts/journal.py record <id>`.
6. Invite reviewers: at least one from outside the author list, aiming for two.

The steps, with the commands, are in the repository's `README.md` under Publishing an Article.

## After a Review

List the review in `reviews/<id>/status.yml` and run `python scripts/journal.py record <id>`:
every version's page then links it, without any published version changing. When an invited
review is posted and the authors have answered or revised, set the status there to Reviewed.
Export the thread to `reviews/<id>/` and include it in the next deposit.
