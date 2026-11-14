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

1. Assign the identifier, `<year>-<nnn>`, and move the source to `articles/<id>/`.
2. Build version 1 and freeze it under `published/<id>/v1/`.
3. Deposit the version on Zenodo as a journal article, in the journal's community, with the
   authors' ORCID iDs and the license. Put the DOIs on the page.
4. Open the article's review thread and set the status to Review open.
5. Invite reviewers: at least one from outside the author list, aiming for two.

## After a Review

Link the review from the article. When an invited review is posted and the authors have answered
or revised, set the status to Reviewed. Export the thread to `reviews/<id>/` and include it in
the next deposit.
