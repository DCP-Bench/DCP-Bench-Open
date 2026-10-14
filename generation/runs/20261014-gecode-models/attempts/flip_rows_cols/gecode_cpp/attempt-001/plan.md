Plan: flip the signs of entire rows and columns so that every row and column sums to a non-negative number, and minimise the total sum of the resulting array.

- Decision: x[i] = 1 if row i is flipped; y[j] = 1 if column j is flipped. -> BoolVarArray x(27), y(9); branch on both.
- Symmetry: flipping all rows and all columns together leaves every entry unchanged -> rel(*this, x[0] == 0) (row 0 not flipped). Symmetry breaking, see reference comment.
- Output row_signs[i] = 1 - 2 x[i] in {-1, 1} -> IntVarArray rs(27, -1, 1), rel(rs[i] == 1 - 2*x[i]).
- Output col_signs[j] = 1 - 2 y[j] in {-1, 1} -> IntVarArray cs(9, -1, 1), rel(cs[j] == 1 - 2*y[j]).
- Entry sign flipped cell p[i][j] = x[i] xor y[j] -> rel(x[i], BOT_XOR, y[j], p[i][j]) (BoolVar per cell).
- Each row sum non-negative: sum_j a_ij (1 - 2 p_ij) >= 0 -> linear(2*a_ij over p_ij, IRT_LQ, sum_j a_ij).
- Each column sum non-negative: sum_i a_ij (1 - 2 p_ij) >= 0 -> linear(2*a_ij over p_ij column, IRT_LQ, sum_i a_ij).
- Objective total = sum of all entries after flipping = sum_ij a_ij (1 - 2 p_ij) -> IntVar total = expr(sum(IntArgs(-2a), p) + sum a).
- Branching: y (column flips) first, then x (BOOL_VAR_NONE, BOOL_VAL_MIN); p and row signs follow by propagation. Minimise total.
