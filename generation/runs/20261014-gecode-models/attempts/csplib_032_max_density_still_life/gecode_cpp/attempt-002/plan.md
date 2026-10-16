The grid is n x m; cells outside it are dead.
  -> BoolVarArray cell(n*m), cell[r*m+c] = 1 if alive
Every cell of the grid is a 0/1 variable; the output grid is one BoolVarArgs per row.
  -> output("grid", rows) with std::vector<BoolVarArgs>
A live cell has at least 2 live neighbours.
  -> linear over (neighbours, x) with coefficients (1,...,1,-2) >= 0 (same as attempt 1)
A live cell has at most 3 live neighbours.
  -> linear over (neighbours, x) with coefficients (1,...,1,5) <= 8 (same as attempt 1)
A dead cell in the grid must not have exactly 3 live neighbours.
  -> linear(nb, IRT_EQ, 3, Reify(x, RM_PMI)) (same as attempt 1)
A dead cell just outside the grid must not have exactly 3 live neighbours.
  -> linear(nb, IRT_NQ, 3) over its in-grid neighbours (same as attempt 1)
Maximise the number of live cells.
  -> live = expr(sum(cell)); maximize(live)
Branching: cells in reading order (row by row), live value first. Changed from attempt 1 (AFC with restarts) because attempt 1 timed out on the 8x8 instance; the reading-order search sweeps the grid row by row, so the rows above are fixed before the constraints of the lower rows are tested.
  -> branch(*this, cell, BOOL_VAR_NONE(), BOOL_VAL_MAX())
