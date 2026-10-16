# Plan: flip_rows_cols (attempt-001)

- Each row i may be flipped; each column j may be flipped -> Bool R_i (row flipped), C_j (column flipped). Sign output: row_signs[i] = 1 - 2*R_i.
- Cell (i,j) is negated when exactly one of its row and column is flipped -> Bool X_ij, with X_ij <-> (R_i + C_j == 1) (PB comparison in Iff).
- Signed cell value = a_ij * (1 - 2*X_ij), linear in X_ij.
- Each row sum is positive or zero -> sum_j a_ij*(1 - 2*X_ij) >= 0 (PB over X_ij).
- Each column sum is positive or zero -> sum_i a_ij*(1 - 2*X_ij) >= 0 (PB over X_ij).
- Objective: minimise the overall sum of the signed cells -> sum_ij a_ij*(1 - 2*X_ij) (linear PB objective, constant part kept).
