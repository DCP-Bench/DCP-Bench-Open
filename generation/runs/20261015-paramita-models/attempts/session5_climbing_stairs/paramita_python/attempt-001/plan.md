# Plan: session5_climbing_stairs

Requirements (description words) -> Paramita encoding

- "climb a stair of n steps" -> the moves add up to n: `sum(v * x[i][v]) == n` (PB over one-hot Bools)
- "you can take only m1 to m2 steps at a time" -> move i is one-hot over {0} + [m1..m2]: `sum(x[i].values()) == 1`
- "a list of n integers" -> one move per position i in 0..n-1 (each move is at least 1 step, so n slots suffice); output `steps[i] = sum(v * x[i][v])`
- "each integer is between m1 and m2, or 0 if no steps are taken at that move, i.e. after we reach the top" -> x[i][0] means "no step"; `If(x[i][0], x[i+1][0])` so zeros form a suffix

Objective: none (satisfaction).
