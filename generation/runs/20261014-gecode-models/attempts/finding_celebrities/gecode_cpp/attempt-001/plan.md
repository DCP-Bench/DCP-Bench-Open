Problem: a guest is a celebrity when everybody at the party knows them and they know only other celebrities; at least one celebrity is present; output the 0/1 celebrity flags in input order.
- a guest is a celebrity only if everybody at the party knows them (including themselves) -> rel(*this, celeb[c] == 0) for each c and each i with graph[i][c] = 0 (constant data, unit constraint)
- a celebrity knows only other celebrities: if c knows j then c celebrity implies j celebrity -> rel(*this, (celeb[c] == 1) >> (celeb[j] == 1)) for each pair with graph[c][j] = 1 (no global fits a per-pair implication; a decomposition is the only form)
- at least one celebrity is present -> linear(*this, celeb, IRT_GQ, 1)
- branching: all celebrity flags, BOOL_VAR_NONE, BOOL_VAL_MIN (propagation fixes most flags)
- objective: none (satisfaction); output celebrities
