# Plan: csplib_028 BIBD

Encoding: Bool incidence matrix X[i][j] (i < v objects, j < b blocks); auxiliary P[i][i'][j] <-> X[i][j] & X[i'][j] for each pair of rows.

- "a v by b binary matrix" -> X[i][j] Bool, output matrix [v][b] of Bools.
- "exactly r ones per row" -> per row i: sum_j X[i][j] == r.
- "k ones per column" -> per column j: sum_i X[i][j] == k.
- "a scalar product of lambda between any pair of distinct rows" -> per pair i<i': sum_j P[i][i'][j] == lambda, P <-> X[i][j] & X[i'][j].
- Objective: none (satisfaction).
