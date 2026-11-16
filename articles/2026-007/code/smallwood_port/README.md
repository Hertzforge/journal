# Smallwood 1999 Appendix A, Ported

A line-by-line port of the correction in Appendix A of D. O. Smallwood, "Multiple Shaker Random
Vibration Control: An Update" (SAND98-2044C, OSTI 3874), written for this article's second independent
check and published with it under the MIT license. Read from the scanned report: pages 9 and 10 for the
listing, page 6 for Equations 11 to 13, and page 4 for the factorization with zeros (Equation 8 and the
sentence after it). The OCR text of the listing is garbled and was not relied on.

## Files

- `smallwood_port.py`: `correction(Y, C, Z, e, tol, rankH)` ported line by line, same order, tests and
  constants (`tol = 1e-4`, `minZ = tol * abs(max(max(Y)))`, the 0.5 tests, the 1e6 warning, the 0.01
  collapse factor), and `factor_with_zeros` as the body states it (a zero or negative pivot sets the
  entire row and column of the factor to zero). Indices are 0-based; where the listing uses an index as a
  number (`2*j*Y(k,k)`, `2*k*Y(1,1)`) the 1-based value is used. `rankH` defaults to `min(size(Y))`, as in
  the listing; the Figure 3 case is full rank, so the rank rule does nothing there.
- `run_fig3_case.py`: the Figure 3 case as the article defines it (`make_data.structure('loop_true')` and
  `'loop_estimate'`, every mode 3 percent high, exact measurement, 30 loops, drive $A Z Z^H A^H$ with $A$
  the pseudo-inverse truncated at 1e-3, $Z_0 = R$), the independent target and a target with cross terms
  (coherence 0.64, phase 30 degrees). It runs the build's loop (an
  independent port of `factor.rs` `FactorLoop::iterate` at 646c4ca4, own coordinates) beside the port.
  Usage: `python run_fig3_case.py > ../../data/smallwood_port_output.txt` (it imports only
  `make_data.structure` from the folder above).
- `../../data/smallwood_port_output.txt`: the output (about 8 s on one core).

## Ambiguities and How They Were Read

1. **Column 1 of the alternate correction.** The listing prints
   `Dp(k,1) = Z(k,1)*E(1,1)/(2*k*Y(1,1))` (row index $k$, the first gauge's error and target), while
   columns 2 to N use `Dp(k,j) = Z(k,j)*E(k,k)/(2*j*Y(k,k))` (column index, the row gauge's error and
   target). Equation 13 in the text, $\Delta^{alt}_{jk} = Z_{jk}(\Phi^{RR}_{kk} - \Phi^{rr}_{kk})/(2j\Phi^{RR}_{kk})$
   with $j$ the row and $k$ the column (as in Equation 12), agrees literally with the column-1 line, not
   with columns 2 to N. Both are run: `col1='printed'` (default) and `col1='columns'` (the column-1 line
   read as the columns 2:N line with $j = 1$). The guidelines in the text ("the affected power spectra")
   point to the row gauge's error, which favours `'columns'` as the intent; the listing is what was
   printed.
2. **`max` of complex numbers.** MATLAB's `max` of complex values compares magnitudes; the diagonal of
   $Z$ is real, so `max(Z(1,1),Z(j,j))` is read as the larger magnitude.
3. **`E(k,k)<0` on a complex matrix.** MATLAB compares real parts; the diagonal of $E$ is real here.
4. **The column collapse** divides by `abs(Znew(j,k))`; in the faithful port a cross term cannot be exactly
   zero at that point (the reset just above sets it to `minZ`), so the guard added for the switched runs
   never acts in the faithful one.
5. **Convergence factor.** The article's case uses $e = 0.5$. The paper's own example uses $e = 1$. Both
   are run, and $e = 0.25$ as a smaller value.
6. **Not ported**, because the article's case does not use them: the update of $H$ and $G$ during the test
   (Figure 2 of the paper), time-domain randomization, and the drive-side details of the paper's loop.

## One at a Time

`correction(..., switch=(...))` replaces one feature by the build's: `'step'` (second-form step
$E_{kk}/(2G_{ref,kk})$ in every column), `'zero'` (second form on a zero term and no reset of a zero term),
`'divisor'` (divide by $Z_{jj}$, never below `minZ`), `'limit'` (+3.5 / -6 dB of the term's own value,
scaling the column's first-form terms), `'order'` (the second form swapped in inside the recursion).
These are approximations of the build's rules inside Smallwood's skeleton, for attribution only.

## Results (independent target unless stated; gauge 2; loop 30)

| Loop | 85 to 96 Hz RMS | 91.0 Hz | 91.5 Hz | 150 to 172 Hz RMS | Note |
|:---|:---|:---|:---|:---|:---|
| Build (`factor.rs`) | 2.37 | +4.87 | +5.05 | 1.12 | |
| Port, as printed, e = 0.5 | 1.54 | +0.40 | +5.04 | 0.74 | 161 Hz swings -5.7 to +2.5 dB over loops 3 to 30 |
| Port, column 1 read as columns 2:N, e = 0.5 | 2.05 | +4.86 | +5.04 | 0.89 | 91 Hz falls to +0.95 at loop 3, climbs back |
| Port, as printed, e = 1 | 2.84 | +4.87 | +5.05 | 2.01 | 120 lines over 0.5 dB |
| Port, as printed, e = 0.25 | 2.26 | +4.80 | +4.99 | 0.67 | |
| Cross-term target: build | 2.37 | +4.87 | +5.05 | 0.40 | |
| Cross-term target: port, e = 0.5 | 2.25 | +4.87 | +5.05 | 0.21 | 90.5 to 93 Hz identical to the build |
| Cross-term target: port, e = 1 | 3.20 | +4.87 | +5.05 | 1.46 | diverges near 413 Hz (+133 dB, drive power 8.6e12) |

One at a time, from the port as printed at e = 0.5, independent target: 91 Hz goes back to the build's
+4.87 dB with any one of `'zero'` (+4.87; 85-96 Hz RMS 2.37, the build's), `'step'` (+4.86), `'order'`
(+4.87) or `'limit'` (+4.77); `'divisor'` alone leaves it at +0.40. The line at 91.5 Hz is held under
every variant in the table (and 92.0 Hz at +4.61 dB in each run whose 89 to 94 Hz lines are printed).
The 103 "D(j,j) too large" warnings in the output all come from the diverging cross-term run at e = 1.
