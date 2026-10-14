A boy wants to give an apple to a girl; he passes num_gates gates, each guard takes half of his apples plus one, the boy gives an integer number of apples, after giving the apple to the girl he has no apples left.
apples[i] = apples before gate i (i = 0..num_gates-1); apples[num_gates] = apples after the last gate = 1 (the apple given to the girl) -> rel(*this, apples[n] == 1)
bribe i = apples[i]/2 + 1 is an integer -> 2*bribe[i] == apples[i] + 2 -> linear(*this, {2,-1}, {bribe[i], apples[i]}, IRT_EQ, 2)
after gate i he has apples[i] - bribe[i] -> apples[i+1] == apples[i] - bribe[i] -> linear(*this, {1,-1,1}, {apples[i+1], apples[i], bribe[i]}, IRT_EQ, 0)
apples are non-negative and bounded by 3*2^n - 2 (reverse recurrence from 1 apple; the start count is the maximum, so the bound is exact) -> IntVarArray domains
branching: apples in order with INT_VAR_SIZE_MIN and INT_VAL_MIN, then the bribes
objective: none (satisfaction); outputs: apples as IntVarArray of num_gates+1
