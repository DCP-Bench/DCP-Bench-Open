Futoshiki: a square n x n grid, place the digits 1..n so each row and each column holds every digit once.
Some cells are given digits -> rel(*this, cell[i] == v) for each non-zero entry of values.
Each row contains each of the digits 1 to n once -> distinct(*this, row_r, IPL_DOM)
Each column contains each of the digits 1 to n once -> distinct(*this, col_c, IPL_DOM)
Inequality between two neighbouring cells, the first is lower than the second -> rel(*this, a, IRT_LE, b), one per entry of lt (1-based cell indices)
Branching over all cells, first-fail on the variable, smallest value first -> branch(*this, cell, INT_VAR_SIZE_MIN(), INT_VAL_MIN())
Objective: none, satisfaction -> output grid as the n rows of cells
