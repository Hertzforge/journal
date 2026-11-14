// The print copy's layout.
//
// The PDF is the static print copy of an article whose version of record is an interactive page.
// Its first page says so and gives that page's address; every later page repeats the address in
// its footer, so a printed sheet that gets separated still says where it came from.
//
// Only the fonts built into Typst are used, so the same source prints the same on any machine.

#let hf-ink = rgb("#10161d")
#let hf-muted = rgb("#566372")
#let hf-rule = rgb("#c9d3df")
#let hf-blue = rgb("#0b62c4")

#let article(
  running: "",
  address: "",
  title: "",
  authors: (),
  date: none,
  doc,
) = {
  set document(title: title, author: authors, date: date)
  set page(
    paper: "us-letter",
    margin: (x: 1in, top: 1.1in, bottom: 1.05in),
    header: context {
      if counter(page).get().first() > 1 {
        set text(size: 8.5pt, fill: hf-muted)
        grid(columns: (1fr, auto), running, [Print copy])
        v(-5pt)
        line(length: 100%, stroke: 0.5pt + hf-rule)
      }
    },
    footer: context {
      set text(size: 8.5pt, fill: hf-muted)
      grid(
        columns: (1fr, auto),
        [Interactive version: #link(address)],
        counter(page).display("1 / 1", both: true),
      )
    },
  )
  set text(font: "Libertinus Serif", size: 10.5pt, lang: "en", fill: hf-ink)
  show math.equation: set text(font: "New Computer Modern Math")
  show raw: set text(font: "DejaVu Sans Mono", size: 0.85em)
  set par(justify: true, leading: 0.62em)
  show heading: it => {
    set text(fill: hf-ink)
    set par(justify: false)
    block(above: 1.5em, below: 0.75em, it)
  }
  show link: set text(fill: hf-blue)
  show figure.caption: set text(size: 9.5pt)
  set figure(gap: 0.9em)
  doc
}

#set table(
  inset: 6pt,
  stroke: none,
)

// The first page: what this copy is, where the article lives, and who wrote it.
#let hf-cover(
  journal: "",
  sample: false,
  title: "",
  kind: "",
  authors: (),
  editors-note: none,
  evidence-label: "Evidence",
  evidence: "",
  evidence-note: "",
  version-line: "",
  note: "",
  address: "",
  doi: none,
  doi-latest: none,
  issn: none,
  citation: "",
) = {
  set par(justify: false)
  text(size: 9pt, fill: hf-muted, tracking: 1.4pt, upper(journal))
  v(-6pt)
  line(length: 100%, stroke: 1.2pt + hf-blue)
  v(2pt)
  if sample {
    block(width: 100%, inset: 9pt, fill: rgb("#fff3d6"), stroke: 0.8pt + rgb("#b37a00"), radius: 3pt)[
      *Sample. Not a publication.* This document exists to test the journal's build. Its authors,
      data and results are invented.
    ]
  }
  block(width: 100%, inset: 11pt, stroke: 0.9pt + hf-ink, radius: 3pt)[
    *Print copy.* This is the static print copy of an interactive article. The version of record,
    with its interactive figures and the data and code behind them, is at \
    #link(address) \
    #if doi != none [DOI of this version: #link("https://doi.org/" + doi)[#doi]]
  ]
  v(12pt)
  text(size: 9.5pt, fill: hf-muted, tracking: 0.6pt, upper(kind))
  v(-2pt)
  par(leading: 0.5em, text(size: 21pt, weight: "bold", title))
  v(4pt)
  for author in authors {
    block(above: 0.55em, below: 0em)[
      #text(size: 11.5pt, weight: "semibold", author.name)
      #if author.orcid != none [
        #h(6pt) #text(size: 8.5pt, fill: hf-muted)[ORCID #link("https://orcid.org/" + author.orcid)[#author.orcid]]
      ]
    ]
  }
  if editors-note != none {
    v(4pt)
    text(size: 9.5pt, fill: hf-muted, editors-note)
  }
  v(12pt)
  grid(
    columns: (auto, 1fr),
    column-gutter: 12pt,
    row-gutter: 7pt,
    text(fill: hf-muted, evidence-label), [*#evidence.* #evidence-note],
    text(fill: hf-muted)[Version], [#version-line #if note != "" [ \ Change note: #note]],
    ..if doi-latest != none {
      (text(fill: hf-muted)[Latest version], link("https://doi.org/" + doi-latest)[#doi-latest])
    } else { () },
    ..if issn != none { (text(fill: hf-muted)[ISSN], issn) } else { () },
    text(fill: hf-muted)[Cite as], citation,
  )
  v(8pt)
  line(length: 100%, stroke: 0.5pt + hf-rule)
}

// The last lines: where it is implemented, where its reviews are, and its license.
#let hf-back(
  implemented: none,
  implemented-url: none,
  reviews: "",
  license: "",
  use: "",
) = {
  set par(justify: false)
  v(1em)
  line(length: 100%, stroke: 0.5pt + hf-rule)
  set text(size: 9.5pt)
  if implemented != none [
    *Implemented in.* #if implemented-url != none { link(implemented-url, implemented) } else { implemented }
    #parbreak()
  ]
  [*Reviews.* #reviews]
  parbreak()
  license
  parbreak()
  text(fill: hf-muted, use)
}
