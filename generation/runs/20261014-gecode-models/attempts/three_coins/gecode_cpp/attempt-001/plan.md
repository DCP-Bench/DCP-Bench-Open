Three coins lie on a table in the order tails, heads, tails. -> steps[0][c] == init[c] (row 0 is the instance's starting state, True = tails) : rel(*this, s[0][c] == init[c])
In precisely three moves -> num_moves from the instance; steps has num_moves+1 rows of 3 coins.
Each move consists of choosing one coin and flipping it over -> per move t and coin c, d[t][c] = s[t][c] xor s[t+1][c] : rel(*this, a, BOT_XOR, b, d); exactly one coin flips per move : linear(*this, d, IRT_EQ, 1)
make them face either all heads or all tails -> final row all equal : rel(*this, s[last][c] == s[last][0]) for each c
Branching -> branch(*this, s, BOOL_VAR_NONE(), BOOL_VAL_MIN()) over all step variables (row 0 is fixed already).
Objective -> none (satisfaction).
