# Plan: flip_rows_cols (attempt-002)

Attempt-001 was accepted on 4 of 5 instances, but the 27x9 example hit execution_timeout (optimum not proven). Repair: symmetry breaking.

- Flipping every row and every column together leaves every cell sign and every sum unchanged -> fix row 0 as not flipped (R_0 = 0). No optimum is lost, since the complement of any solution is also a solution with the same objective.
- Everything else as attempt-001: X_ij <-> (R_i + C_j == 1), row and column sums >= 0, minimise the signed total.
