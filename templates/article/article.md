---
# Filled in by the editors at publication.
id: ""                 # <year>-<nnn>, for example 2026-001
version: 1
first_published: ""    # YYYY-MM-DD
date: ""               # the date of this version
doi: ""                # this version
doi_latest: ""         # always resolves to the latest version

# Filled in by the authors.
title: ""
type: Research Article # Research Article | Method Note | Negative Result | Proposed Standard | Practice Note | Survey | Perspective
evidence: simulator    # simulator | bench | hardware; a Perspective says what it rests on instead, for example: published sources
authors:               # in order; the author who led the work is first
  - name: ""
    orcid: ""          # https://orcid.org/0000-0000-0000-0000
    roles: []          # CRediT roles, for a co-authored article
implemented_in: ""     # the Hertzforge release or commit that implements this work, if any
benchmarks: ""         # the Open Benchmark Set version, problems and seeds, if used
abstract: >
  One paragraph: what was done, what was found, and how far the evidence goes.
---

**Evidence:** say in one sentence whether the results come from simulation, a bench or real test
hardware, and on what.

## Introduction

What the problem is, why it matters on a real test, and what is already known.

## Method

Enough that a reader could do it again.

## Results

Every figure is drawn by a file in `code/` from a file in `data/`. Give each figure alternative
text, and tell its series apart by line style or marker as well as color.

## Limits

What this does not show, where it failed, and what would change the conclusion.

## Contribution Statement

For a co-authored article: who did what, in the CRediT roles (Conceptualization, Methodology,
Software, Validation, Formal analysis, Investigation, Data curation, Writing: original draft,
Writing: review and editing, Visualization, Supervision).

## How This Was Made

The tools used, AI tools included, and what each was used for. The authors are responsible for
every word, number and line of code.

## Acknowledgments

Whoever an idea came from, inside or outside the author list, and anyone who helped.

## References

## Version History

- Version 1: first published.

---

Copyright the authors. Text, figures and data are under CC BY 4.0; code is under the MIT license.
Methods are published for research; anyone who applies one to a test is responsible for
protecting the equipment and the article under test.
