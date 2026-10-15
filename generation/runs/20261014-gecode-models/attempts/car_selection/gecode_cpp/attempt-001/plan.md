Problem: assign participants to cars, each participant at most one car, each car at most one participant, only to cars they are interested in; maximise the number of assignments.

each participant is assigned to at most one car -> linear(*this, row_i, IRT_LQ, 1) over the Booleans of row i
each car is assigned to at most one participant -> linear(*this, col_j, IRT_LQ, 1) over the Booleans of column j
a participant is assigned only to a car they are interested in (possible_assignments[i][j] = 0) -> rel(*this, a_ij, IRT_EQ, 0)
total number of assignments (objective) -> total = expr(*this, sum(all Booleans)), maximize(total)
branching: branch(*this, a, BOOL_VAR_NONE(), BOOL_VAL_MAX()) (no decomposition needed; linear sums are the map rows)
