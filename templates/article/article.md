---
# Filled in by the editors at publication.
id: ""                 # <year>-<nnn>, for example 2026-001. The editors assign it when the article is published
version: 1             # the version this source is. The build makes exactly this one
date: ""               # YYYY-MM-DD, the day this version is published
doi: ""                # this version's DOI, reserved before the build
doi_latest: ""         # the DOI that always resolves to the latest version, reserved before the build
note: First published. # what changed in this version: a line, or paragraphs (write `note: |` and indent them)

# Filled in by the authors.
title: ""
type: Research Article # Research Article | Method Note | Negative Result | Proposed Standard | Practice Note | System Description | Survey | Perspective
evidence: simulator    # simulator | bench | hardware; a Perspective or a Survey says what it rests on instead, for example: published sources
evidence_note: ""      # one sentence: what the results come from, and on what. It shows beside the evidence level
authors:               # in order; the author who led the work is first
  - name: ""
    orcid: ""          # https://orcid.org/0000-0000-0000-0000
    roles: []          # CRediT roles, needed when there is more than one author: Conceptualization,
                       # Methodology, Software, Validation, Formal analysis, Investigation, Resources,
                       # Data curation, "Writing: original draft", "Writing: review and editing",
                       # Visualization, Supervision, Project administration, Funding acquisition
implemented_in: ""     # the Hertzforge release or commit that implements this work, if any
                       # (or two lines: `label:` what it is, `url:` its address)
benchmarks: ""         # the Open Benchmark Set version, problems and seeds, if used
# contents: true       # a contents list. Left out, an article with five or more sections gets one
# number_sections: true  # have the build number the sections. Leave out if the headings carry their own numbers
abstract: >
  One paragraph: what was done, what was found, and how far the evidence goes.
---

## Introduction

What the problem is, why it matters on a real test, and what is already known. Cite a source
from `references.bib` by its key, like this: [@key]. Or leave `references.bib` out and write the
reference list by hand under References.

These section names suit a research article. Any type may use its own: only the closing sections
(How This Was Made, Acknowledgments, References) are fixed, and they come last, in that order.

## Method

Enough that a reader could do it again. An equation, with a name to refer to it by:

$$
m \ddot{x} + c \dot{x} + k x = f(t)
$$ {#eq-motion}

and a reference to it: @eq-motion.

## Results

Every figure is drawn by a file in `code/` from a file in `data/`. Write each one as the line
below, on one line: the caption, the figure's name, a name to refer to it by, alternative text
that says what the figure shows to a reader who cannot see it, and the data file behind it. Tell
its series apart by line style or marker as well as color. Refer to it as @fig-name.

    ![Caption.](figures/name.png){#fig-name fig-alt="What the figure shows." data="data/file.csv"}

A figure named `name` is interactive when `code/name.py` defines `figure()` and the article
holds no picture of it: the build then draws it, both interactive and as a static picture. A
picture you supply as `figures/name.png` (a photograph, a drawing, a plot made elsewhere) is
shown as it is. `code/README.md` says how.

A table, with a name to refer to it by (@tbl-name). A wide table scrolls inside its own frame on
a narrow screen:

| Quantity | Value |
|----------|------:|
|          |       |

: Caption. {#tbl-name}

## Limits

What this does not show, where it failed, and what would change the conclusion.

## How This Was Made

The tools used, AI tools included, and what each was used for. The authors are responsible for
every word, number and line of code.

## Acknowledgments

Whoever an idea came from, inside or outside the author list, and anyone who helped.

## References
