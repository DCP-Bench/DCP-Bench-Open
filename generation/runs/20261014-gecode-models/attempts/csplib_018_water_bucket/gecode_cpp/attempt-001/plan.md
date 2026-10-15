Problem: divide 8 pints into 4 and 4 with 8, 5, 3 pint buckets; minimise the number of pours.

Requirement: the buckets start at [8,0,0] (instance initial_state) -> sequence[0] is fixed to the initial state, rel(st == init) -> rel(*this, st[b], IRT_EQ, init[b])
Requirement: a pour moves water from bucket i to bucket j until i is empty or j is full, one transfer -> per step a pour code 3*i+j (i != j) and the next state; the legal pours of each state are tuples of a table -> extensional(*this, [s0,s1,s2,pour,t0,t1,t2], TupleSet) with one tuple per legal (state, pour), built from the capacities
Requirement: a pour that changes nothing is not a transfer -> tuples only for amount > 0
Requirement: the goal state is 4,4,0 (instance goal_state) and the sequence ends there -> tuple (goal, NONE, PAD,PAD,PAD) only; no real pour leaves the goal
Requirement: after the goal, the rest of the list is padding [-1,-1,-1] (instance PADDING_VALUE) -> tuples (PAD, NONE, PAD); a non-goal state cannot take NONE, so the goal must be reached
Requirement: the goal is reached within MAX_STEPS states -> last state in {goal, PAD} -> extensional on 3 vars with 2 tuples
Requirement: state domains -> st[k][b] in PAD..capacities[b]
Objective: minimise the number of transfers -> moves_k = (pour_k != NONE) as BoolVar, total = sum(moves), minimize(total)
Branching: pour choices in order (INT_VAR_NONE, INT_VAL_MIN), then the states (fixed by propagation, branched for safety)
