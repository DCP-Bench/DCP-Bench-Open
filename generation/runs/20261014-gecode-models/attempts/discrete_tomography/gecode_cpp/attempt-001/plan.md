matrix is a 0/1 grid of rows x cols cells -> IntVarArray x(rows*cols, 0, 1), row-major; output matrix as one list per row
each row's number of ones equals its row sum -> count(*this, row_i, 1, IRT_EQ, row_sums[i])
each column's number of ones equals its column sum -> count(*this, col_j, 1, IRT_EQ, col_sums[j])
branching -> branch on all cells with INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN(); restarts(100) for heavy tails
objective -> none (satisfaction)
