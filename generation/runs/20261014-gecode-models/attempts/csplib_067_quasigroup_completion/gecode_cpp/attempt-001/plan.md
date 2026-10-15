quasigroup of order m is an m x m table in which each element 1..m occurs exactly once in every row and every column -> IntVarArray of N*N cells in 1..N, Matrix view m(col,row)
each element from 1 to m occurs exactly once in every row -> distinct(*this, row_r, IPL_DOM) for each row
each element from 1 to m occurs exactly once in every column -> distinct(*this, col_c, IPL_DOM) for each column
complete a partially filled quasigroup, the given cells keep their value (0 marks empty) -> rel(*this, cell == start[r][c]) for each non-zero entry of the instance start
print the completed quasigroup (puzzle) -> output("puzzle", matrix) one list per row
branching -> branch over all cells with INT_VAR_SIZE_MIN, INT_VAL_MIN (decision variables are all cells)
objective -> none (satisfaction)
