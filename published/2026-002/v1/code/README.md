The code that draws each figure from the files in ../data. It is published under the MIT license.

Every figure can be drawn again from this bundle alone. Each script reads only its own file in
`../data` and writes a static PNG to `../figures`:

- `fig1_measured_frequency_change.py`: Figure 1, measured change of a resonance frequency with level,
  one row per case, grouped by joint condition, marked by excitation and by whether the number is
  stated in the source's text or read off a figure's axis.
- `fig2_timeline.py`: Figure 2, the published work by the year it first appeared and by kind, marked
  by how much of each source was read.

The values in `../data` were taken by hand from the published sources named in each row; there is no
extraction script.

Requirements: Python 3 with matplotlib. Tested with matplotlib 3.11.2 (numpy 2.5.4 installed).

Draw the figures again:

    mkdir -p ../figures
    for f in fig*.py; do python "$f"; done
