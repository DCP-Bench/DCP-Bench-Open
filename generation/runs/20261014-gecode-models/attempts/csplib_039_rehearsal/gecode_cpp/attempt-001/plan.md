# Plan: csplib_039_rehearsal (attempt-001)

Model: pieces are played one after another, so the slots form a timeline. A player waits from the start of the first piece they play to the end of the last one, minus the time they spend playing. Summed over players, the play time is a constant, so minimising waiting time means minimising the sum over players of (last end - first start).

- one slot per position, each slot holds one piece, all different -> channel(*this, order, pos) and distinct on order (permutation, IPL_DOM)
- slot start times are the running sum of the durations in order -> S[0] = 0, S[k+1] = S[k] + dur[order[k]] via element(IntArgs(dur), order[k])
- piece start = start of its slot -> element(*this, S, pos[p], st[p])
- piece end = start + duration -> linear with expr
- a player is present from the first start of a piece they play to the last end -> min(*this, starts of its pieces, first_j), max(*this, ends of its pieces, last_j)
- total waiting = sum over players (last_j - first_j) - sum over pieces dur * players_in_piece -> rel on IntVar obj, minimize(obj)
- branching: order with INT_VAR_NONE / INT_VAL_MIN (slots in order, the only decision); then st and S, which are fixed by propagation
- symmetry: none in the description
- no decomposition needed: element/channel/min/max are the rows that fit
