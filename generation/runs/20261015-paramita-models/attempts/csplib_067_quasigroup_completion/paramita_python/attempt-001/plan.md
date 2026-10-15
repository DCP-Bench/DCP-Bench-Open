# Plan: csplib_067 quasigroup completion (order N Latin square with given cells)

- "each element from 1 to m occurs exactly once in every row" -> per row r and value v: sum over c of x[r][c][v] == 1 (one-hot per cell)
- "each element from 1 to m occurs exactly once in every column" -> per column c and value v: sum over r of x[r][c][v] == 1
- "each cell holds one value" -> per cell: sum over v of x[r][c][v] == 1 (one-hot encoding of the cell value)
- "partially filled, the given entries are kept" (0 = empty) -> for each non-zero start[r][c] = g: x[r][c][g-1] == 1
- "print the completed quasigroup (puzzle)" -> puzzle[r][c] = sum over v of (v+1) * x[r][c][v] (integer expression)
- Objective: satisfaction, none.
