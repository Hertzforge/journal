The code that draws each figure. It is published under the MIT license.

The three figures are block diagrams drawn from the layout of the Hertzforge repository at commit
`b587d5a1` and its documentation; they read no data file. Each script writes a static PNG to
`../figures`:

- `fig1_architecture.py`: Figure 1, the three programs, the protocol between them and the drive
  path.
- `fig2_one_loop.py`: Figure 2, one control loop: what the control law sees and what the core keeps.
- `fig3_bench.py`: Figure 3, the loopback bench the hardware evidence comes from.
- `diagram.py`: the drawing helpers the three share.

Run each from this folder: `python fig1_architecture.py`. Requirements: Python 3 with matplotlib
(tested with matplotlib 3.11.2).
