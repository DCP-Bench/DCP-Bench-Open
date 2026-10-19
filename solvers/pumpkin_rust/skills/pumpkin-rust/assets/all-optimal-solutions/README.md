# Two cheapest tasks (all optimal solutions)

**Problem:** choose exactly two of five tasks with the smallest total cost; list every choice that reaches that cost.
**Shows:** Boolean literals with `boolean_equals`, `optimise` with `LinearSatUnsat`, posting the optimum, then enumeration over the literals with blocking clauses.
**Run:** `NO_CHECKERS=true cargo run --quiet`
**Expected:** `minimum cost: 3`
**Expected:** `optimal solutions: 2`
