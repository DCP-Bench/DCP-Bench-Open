The grid is n x m; cells outside it are dead.
  -> BoolVarArray cell(n*m), cell[r*m+c] = 1 if alive
Every cell of the grid is a 0/1 variable; the output grid is one BoolVarArgs per row.
  -> output("grid", rows) with std::vector<BoolVarArgs>
A live cell has at least 2 live neighbours.
  -> linear over (neighbours, x) with coefficients (1,...,1,-2) >= 0 [sum_nb >= 2x] (no map row fits: reified count with a constant bound; linear is the bounds encoding)
A live cell has at most 3 live neighbours.
  -> linear over (neighbours, x) with coefficients (1,...,1,5) <= 8 [sum_nb <= 3 when x = 1] (same reason)
A dead cell in the grid must not have exactly 3 live neighbours (it would come alive).
  -> linear(nb, IRT_EQ, 3, Reify(x, RM_PMI)) : (sum_nb == 3) implies x = 1
A dead cell just outside the grid must not have exactly 3 live neighbours.
  -> linear(nb, IRT_NQ, 3) over its in-grid neighbours (the outside cell is 0)
Maximise the number of live cells.
  -> live = expr(sum(cell)); maximize(live)
Branching: branch on the cells, most-conflicting first (AFC), value 1 first (denser patterns first); restarts for the proof.
  -> branch(*this, cell, BOOL_VAR_AFC_MAX(0.99), BOOL_VAL_MAX()); restarts(100)
