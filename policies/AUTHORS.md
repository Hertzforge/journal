# Guide for Authors

Anyone may submit, on any topic in the journal's scope. You do not need to use Hertzforge.

## Scope

Vibration and shock testing, multi-input multi-output control, and structural dynamics analysis:
methods, results, practice and the prior work behind them.

## Article Types

| Type | What it is |
|---|---|
| Research Article | A new method, law, analysis or result, with its evidence. |
| Method Note | A short, self-contained method or technique. |
| Negative Result | Something tried that did not work, and why. Kept as part of the record. |
| Proposed Standard | A proposed practice, metric or acceptance standard, versioned and open to comment. It cites the published standards as references and says where and why it departs. |
| Practice Note | How to do something well on a real test. |
| System Description | How a test system, or part of one, is built and why: its software, hardware, firmware or the interfaces between them, the design choices and what was rejected, and the evidence that it works as described. |
| Survey | A map of prior work on a topic. It says what it rests on (for example: published sources) where other articles state an evidence level. |
| Perspective | An argued position on practice or on the field. It cites the evidence it rests on, and says what it rests on where other articles state an evidence level. |

## What Every Article Needs

- A title, and the authors with their ORCID iDs.
- The article type, and the evidence level: simulation, a bench, or real test hardware. An
  article that argues a position or maps published work says what it rests on instead (for
  example: published sources).
- An abstract, and the article.
- A contribution statement, if it is co-authored, in the CRediT roles.
- A statement of how it was made: the tools used, AI tools included, and what for.
- Acknowledgments that name the sources of ideas, and references.
- The data behind every figure and the code that draws it.
- Figures that read without color alone: series are told apart by line style or marker as well,
  and every image has alternative text.

## How to Submit

Copy `templates/article/` to `articles/<working-name>/`, write the article in `article.md`
(Markdown, with its facts in the block at the top), put the data behind each figure in `data/`
and the code that draws it in `code/`, and open a pull request. The template shows how a figure,
an equation, a table and a citation are written, and `templates/article/code/README.md` says
what the build asks of a figure. The template's section names suit a research article; use your
own where they fit better. To see your article as it will be published, run
`scripts/publish articles/<working-name> --preview`.

## What the Editors Check Before Publishing

That the article is in scope and complete, that its figures regenerate from its data and code,
that it is licensed as the policies require, and that it claims no affiliation. Then it is
published, and review opens.

## After Publication

Answer reviews in the article's thread. Revise as a new version when you choose to; every
version stays available and citable.

## Reporting on the Benchmark Set

If your article develops a control law for multi-shaker testing, we recommend reporting it on
the Open Benchmark Set and naming the version, the problems and the seeds. It is a
recommendation, not a requirement.

## What You Keep

Your copyright and your credit. Your article is under CC BY 4.0 and its code under the MIT
license. Nobody edits it without your approval.
