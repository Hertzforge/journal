"""A line-by-line port of the correction algorithm in Appendix A of D. O. Smallwood, "Multiple Shaker
Random Vibration Control: An Update", Proc. IEST 1999 (SAND98-2044C), MATLAB function
correction(Y, C, Z, e, tol, rankH), read from the scanned report pages 9 and 10 (Appendix A). Also the
factorization with zeros as the paper's body states it (Equation 8 and the sentence after it).

Indices are 0-based here; every MATLAB index i becomes i - 1, and every place the listing uses an
index as a number (the factor j or k in the alternate correction) uses the 1-based value.

Faithful by default. Optional switches (each one replaces ONE feature by the Hertzforge build's
version, for the one-at-a-time test) are off unless named; see README.md.

Copyright 2026 Kevin Cross. MIT license.
"""
import numpy as np


def factor_with_zeros(G):
    """Cholesky with zeros (Smallwood 1999, Eq. 8 and text): if a zero or negative diagonal element
    is found during the factorization, the entire row and column of the factor is set to zero."""
    n = G.shape[0]
    R = np.zeros((n, n), complex)
    for j in range(n):
        d = G[j, j].real - np.sum(np.abs(R[j, :j]) ** 2)
        if d <= 0:
            R[j, :] = 0
            R[:, j] = 0
            continue
        R[j, j] = np.sqrt(d)
        for k in range(j + 1, n):
            R[k, j] = (G[k, j] - np.sum(R[k, :j] * np.conj(R[j, :j]))) / R[j, j]
    return R


def correction(Y, C, Z, e, tol=1e-4, rankH=None, col1='printed', switch=()):
    """[Znew, D, Dp] = correction(Y, C, Z, e, tol, rankH).

    col1: the first-column line of the alternate correction.
      'printed'  Dp(k,1) = Z(k,1)*E(1,1)/(2*k*Y(1,1))   (as printed; also what Eq. 13 says
                 literally, with the row index and the column gauge's error)
      'columns'  Dp(k,1) = Z(k,1)*E(k,k)/(2*1*Y(k,k))   (the columns 2:N line with j = 1: the row
                 gauge's error and the column index; the reading if the first line is a slip)
    switch: features replaced by the build's, for the one-at-a-time test:
      'step'    alternate step Z(k,j)*E(k,k)/(2*Y(k,k)) in every column (no index factor)
      'zero'    the alternate form also on a zero term, and no reset of a zero term to minZ
      'divisor' divide by Z(j,j) itself (never below minZ) instead of max(Z(1,1), Z(j,j))
      'limit'   diagonal limit +3.5/-6 dB of its own term, scaling the column's first-form terms
      'order'   the alternate form swapped in inside the recursion (later columns use it)
    """
    r = Y.shape[0]
    if rankH is None:
        rankH = r
    scale = abs(Y.flat[np.argmax(np.abs(Y))])          # scale = abs(max(max(Y)))
    minZ = tol * scale
    if rankH > r:
        raise ValueError('rankH > size of Y')
    E = Y - C                                            # the error spectrum
    N = min(rankH, r)
    D = np.zeros((r, r), complex)
    Dp = D.copy()
    Z = Z.copy()
    if N < r:
        Z[N:, :] = 0
        Z[:, N:] = 0

    def div_of(j):
        if 'divisor' in switch:
            return max(Z[j, j].real, minZ)
        return max(abs(Z[0, 0]), Z[j, j].real)        # max(Z(1,1),Z(j,j)) (MATLAB max on |.|)

    def alt(k, j):
        """Dp(k,j); k, j 0-based."""
        if abs(E[k, k]) < .5 * Y[k, k].real:
            if 'step' in switch:
                return Z[k, j] * E[k, k] / (2 * Y[k, k])
            if j == 0 and col1 == 'printed':
                return Z[k, 0] * E[0, 0] / (2 * (k + 1) * Y[0, 0])
            return Z[k, j] * E[k, k] / (2 * (j + 1) * Y[k, k])
        return np.sign(E[k, k].real) * .5 * Z[k, j]

    def swap_inside(k, j):
        if 'order' in switch and (Z[k, j] != 0 or 'zero' in switch) and E[k, k].real < 0 \
                and abs(Z[k, j] + e * D[k, j]) > abs(Z[k, j]):
            D[k, j] = Dp[k, j]

    # first column of D
    D[0, 0] = (E[0, 0] / (2 * (Z[0, 0] if 'divisor' not in switch else max(Z[0, 0].real, minZ)))).real
    if N > 1:
        for k in range(1, N):
            D[k, 0] = (E[k, 0] - D[0, 0] * Z[k, 0]) / (Z[0, 0] if 'divisor' not in switch else max(Z[0, 0].real, minZ))
            Dp[k, 0] = alt(k, 0)
            swap_inside(k, 0)
        # columns 2:N
        for j in range(1, N):
            D[j, j] = E[j, j]
            for i in range(j):
                D[j, j] = D[j, j] - (np.conj(D[j, i]) * Z[j, i] + np.conj(Z[j, i]) * D[j, i])
            # I don't want to blow up if Z(j,j) gets small
            D[j, j] = (D[j, j] / (2 * div_of(j))).real
            if abs(D[j, j]) > 1e6:
                print('warning: D(j,j) too large')
            if j < N - 1:
                for k in range(j + 1, N):
                    D[k, j] = E[k, j] - D[j, j] * Z[k, j]
                    for i in range(j):
                        D[k, j] = D[k, j] - (np.conj(D[j, i]) * Z[k, i] + np.conj(Z[j, i]) * D[k, i])
                    D[k, j] = D[k, j] / div_of(j)
                    Dp[k, j] = alt(k, j)
                    swap_inside(k, j)
    # make sure diagonal corrections are small
    if 'limit' in switch:
        up, dn = 10 ** (3.5 / 20), 10 ** (-6 / 20)
        for j in range(N):
            st, lo, hi = e * D[j, j].real, Z[j, j].real * (dn - 1), Z[j, j].real * (up - 1)
            if st > hi or st < lo:
                D[j:, j] *= (hi if st > hi else lo) / st
    else:
        for i in range(N):
            test = max(abs(Z[i, i]), abs(Z[0, 0]))
            if abs(D[i, i]) > .5 * test:
                D[i, i] = D[i, i] * .5 * test / abs(D[i, i])
    # correct the Z matrix
    Znew = Z + e * D
    # I don't want to get stuck at zero
    if N > 1:
        for i in range(1, N):
            if Znew[i, i].real <= 0:
                Znew[i, i] = minZ
    if Znew[0, 0].real < 0:
        raise ValueError('Z(1,1)<0')
    # Check to see if alternate form should be used
    for i in range(N):
        for k in range(i + 1, N):
            if 'order' not in switch:
                nonzero = (Z[k, i] != 0) or ('zero' in switch)
                if nonzero and E[k, k].real < 0 and abs(Znew[k, i]) > abs(Z[k, i]):
                    Znew[k, i] = Z[k, i] + e * Dp[k, i]
            if Znew[k, i] == 0 and 'zero' not in switch:
                Znew[k, i] = minZ
    # If Znew is reduced to zero I want entire column to be zero
    for k in range(1, N):
        if Znew[k, k].real < minZ:
            for j in range(k + 1, N):
                if abs(Znew[j, k]) > 0:  # cannot be 0 in the faithful port (reset above)
                    Znew[j, k] = Znew[j, k] * .01 * minZ / abs(Znew[j, k])
    return Znew, D, Dp
