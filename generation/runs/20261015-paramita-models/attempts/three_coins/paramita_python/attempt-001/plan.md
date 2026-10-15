# Plan: three_coins

- "Three coins lie on a table in the order tails, heads, tails" (init, 1 = tails) -> steps[0][i] fixed to init[i] (constants via unit clauses)
- "In precisely three moves" (num_moves) -> 4 states steps[0..3] of 3 Bools each (True = tails); states are indexed 0..num_moves
- "Each move consists of choosing one coin and flipping it over" -> per move k, a Bool m[k][i] (choose coin i); exactly one chosen: `sum(m[k]) == 1`; steps[k+1][i] == steps[k][i] XOR m[k][i], written as `Iff(steps[k+1][i], ~steps[k][i])` if m[k][i], else `Iff(steps[k+1][i], steps[k][i])`
- "make them face either all heads or all tails" -> last state: `Iff(steps[N][0], steps[N][1])` and `Iff(steps[N][1], steps[N][2])`
- steps output -> nested list of 4 rows of 3 Bools
- objective -> none (satisfaction)
