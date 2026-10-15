# Plan: flow_free_game (attempt-001)

- Connect matching colours with pipe -> per colour c and cell p: Bool L[c][p][d] = cell p has colour c at pipe distance d from the first endpoint of c. Exactly one (c, d) per cell -> sum(L) == 1 (one-hot colour and level).
- Print the board as colours 1..5 -> B[i][j] = sum_c c * col[c][p], where col[c][p] = OR_d L[c][p][d].
- Pair all colours -> the given endpoint cells are fixed colours (col unit true); the first endpoint A_c has level 0 only, no other cell has level 0.
- Pipes do not break (no crossing, no overlap) -> one colour per cell (exactly one), so a 4-neighbour pipe cell has at most two same-colour neighbours.
- Each pipe is a single path from A_c to B_c -> endpoints have exactly one same-colour neighbour (If(col, sum == 1)); every other cell of that colour has exactly two (If(col, sum == 2)).
- A pipe is connected to its first endpoint and has no separate loop -> L[c][p][d] implies a neighbour q with L[c][q][d-1] (levels strictly decrease, so no cycle).
- Cover the entire board -> every cell has exactly one colour (same as the one-hot constraint).
