Each cell is water, submarine, or one part of a ship (left, right, top, bottom, middle); the grid is 0..MIDDLE with the generic ship marker excluded -> rel(g != _SHIP) plus a padded border fixed to water.
The occupied squares in each row and column are given -> count(row, WATER, IRT_EQ, cols - rowsum) and the same per column.
A ship square has no other ship square touching it, not even diagonally -> rel((g == WATER) || (all four diagonal neighbours == WATER)).
A submarine is a single square with water on all four sides -> rel((g == CIRCLE) >> all orthogonal neighbours WATER).
A left end has water to its left, above and below, and a ship part to its right -> rel((g == LEFT) >> ...).
A right end, a top end and a bottom end follow the same pattern -> rel((g == RIGHT/TOP/BOTTOM) >> ...).
A middle square is part of a horizontal or a vertical ship -> rel((g == MIDDLE) >> (horizontal || vertical)).
The fleet: each ship of length L has an exact pattern (end, L-2 middles, other end) in a row or column; the number of such windows equals the count in fleet_counts -> expr(window) summed by linear(..., IRT_EQ, count); length 1 -> count(CIRCLE, IRT_EQ, count).
Every ship of length 2 or more starts with one LEFT or TOP square, so the number of those equals the sum of the fleet counts for length >= 2 -> linear over Booleans, which rules out ships longer than the fleet allows.
Hints fix given squares -> rel(g == code).
Branching: all interior squares, INT_VAR_SIZE_MIN and INT_VAL_MIN (water first).
Objective: none (satisfaction).
