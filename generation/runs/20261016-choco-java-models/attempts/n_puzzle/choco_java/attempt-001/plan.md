Problem: n_puzzle. Trace a sliding-tile puzzle from the start state to the end state in exactly N_STEPS states; each step slides one tile into the blank, so the state changes at every step.

- grid g x g, tiles 1..g*g-1 and the blank 0; the state at each step is a permutation of the cells -> m.inverseChanneling(P[s], G[s]) (P[s][v] = cell of value v, G[s][c] = value at cell c)
- start state and end state as given -> G[0] and G[N_STEPS-1] fixed with eq().post()
- each step moves the blank to a neighbouring cell (no freezing, the state changes) -> m.table over (blank cell at s, blank cell at s+1) with allowed pairs = adjacent cells
- the tile that is moved (the one on the target cell) goes to the old blank cell, all other tiles stay -> for each tile: m.ifThenElse(P[s][t] = P[s+1][0], P[s+1][t] = P[s][0], P[s+1][t] = P[s][t])
- objective: none, satisfaction; output the states as steps -> out.put("steps", G) with G[s][r][c]
