"devise an order in which the pieces can be rehearsed" -> start[j] start time of piece j, pieces do not overlap (pairwise disjunction); pos[j] = number of pieces starting before j (sum of reified "<"), inverseChanneling(pos, order) gives rehearsal_order
"players can arrive immediately before the first piece in which they are involved and depart after the last" -> per player: first start = min of start[j] over pieces j he plays, last end = max of end[j] over those pieces
"minimize the total time that players are waiting to play" -> per player: waiting = (last end - first start) - total playing time of that player; objective minimize sum of waiting
Objective: minimize total waiting time over all players.
