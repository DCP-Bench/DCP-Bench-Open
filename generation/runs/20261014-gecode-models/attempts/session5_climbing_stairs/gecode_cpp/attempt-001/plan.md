# Plan: session5_climbing_stairs

Requirements in the description's words:
- climb a stair of n steps (instance field n) -> sum of steps over all moves equals n: linear(*this, steps, IRT_EQ, n) [linear sum over the output array]
- you can take only m1 to m2 steps at a time -> each steps[i] in {0} ∪ [m1..m2]: dom(*this, steps[i], IntSet(0, m1..m2), IPL_DEF) per entry (0 is the "no move" value)
- 0 if no steps are taken at that move, i.e. after we reach the top -> zeros only at the end: rel(*this, (steps[i] == 0) >> (steps[i+1] == 0)) for each i (implication chain, no zero before a nonzero move)
- output length: the output shape follows n (the example shows [20] for n=20; n=10 needs [10]), so the array has n slots; with m1 = 1 that is enough for n one-step moves, and trailing slots are 0 -> IntVarArray of length n
- branching: decision variables are the moves -> branch(*this, steps, INT_VAR_NONE(), INT_VAL_MAX()) (moves in order, largest first, zeros last)
- objective: none (satisfaction)
