Problem: trace an N-Puzzle from puzzle_start to puzzle_end in exactly N_STEPS states; each step slides one tile into the blank; the state changes at every step.
Grid: side = size of puzzle_start (from the instance, 2x2, 3x3 or 4x4); tiles 0..side*side-1, tile 0 is the blank.
"each state is a permutation of the tiles" -> channel(*this, tiles_t, where_t, IPL_DOM) with distinct(*this, tiles_t, IPL_DOM) (tile on cell c <-> cell of tile v)
"puzzle_start is the first state" -> rel(*this, tile[0][c] == start[c])
"puzzle_end is the last state" -> rel(*this, tile[T-1][c] == end[c])
"each step moves the blank to a neighbouring cell (a slide)" -> extensional(*this, [blank_t, blank_{t+1}], adjacent-pairs TupleSet)
"the blank's neighbour tile slides in: the tile now on the new blank cell was on the old blank cell's neighbour" -> element(tile[t+1], blank_t, z) and element(tile[t], blank_{t+1}, z) (the tile that moves goes from the new blank cell into the old one)
"every other cell keeps its tile" -> per cell c: keep = (blank_t != c && blank_{t+1} != c); rel(tile[t+1][c] == tile[t][c], imp(keep)) (half-reified)
"state must change at each step (no freezing)" -> implied by the slide: the blank always moves to a different cell, so the state changes; no extra constraint.
"implied bound: one slide changes the sum of tile-to-target Manhattan distances by exactly 1, and the sum is 0 at the end" -> per cell c, element(dist_c, tile[t][c], d_c) with dist_c[v] = Manhattan distance of tile v from c to its end cell (dist_c[0] = 0); linear(sum d_c <= N_STEPS-1-t) (derived; prunes the search, not a part of the description)
Branching: blank positions in time order (INT_VAR_NONE, INT_VAL_MIN), so the blank path is decided and the tiles follow by propagation; then all tile and where variables as fallback.
Objective: none (satisfaction).
Output: steps[t][r][c] = tile on row r, column c of state t, as a three-level IntVarArgs output.
