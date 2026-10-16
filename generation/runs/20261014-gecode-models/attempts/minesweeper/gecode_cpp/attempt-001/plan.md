Attempt 001 plan. Board: game_data[r][c] = X for an unopened cell, otherwise a clue.
Opened cell is not a mine (it was revealed) -> mine[r][c] == 0 -> rel(*this, mine[k], IRT_EQ, 0)
Clue: the number of mines among the 8 neighbours of an opened cell equals its clue -> linear(*this, neighbours, IRT_EQ, clue)
Unopened cells are free Booleans; no other constraint from the description -> none.
Branching: all mine Booleans in row-major order, BOOL_VAR_NONE, BOOL_VAL_MIN (satisfaction, no objective).
Output: mines as one list per row (std::vector<BoolVarArgs>).
