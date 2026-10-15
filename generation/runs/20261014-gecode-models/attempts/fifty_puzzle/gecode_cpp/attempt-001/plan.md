Knock over dummies so that the numbers on the knocked-over dummies sum to exactly the target -> linear(*this, IntArgs(values), dummies, IRT_EQ, target_sum, IPL_DOM) [sum of values[i] * dummies[i] = target]
Each dummy is either knocked over (1) or not (0) -> BoolVarArray dummies(*this, n, 0, 1) [one Boolean per dummy, 1 = knocked over]
Output the dummies knocked over as a list of booleans -> output("dummies", dummies)
Branching: decide each dummy in order, try not knocked over first -> branch(*this, dummies, BOOL_VAR_NONE(), BOOL_VAL_MIN())
Objective: none (satisfaction)
