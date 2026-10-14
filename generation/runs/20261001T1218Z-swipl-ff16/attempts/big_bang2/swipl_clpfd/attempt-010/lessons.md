# Lessons (swipl_clpfd), big_bang2: not solved in 10 attempts

All ten attempts ended in execution_timeout with no solution in 180 s.
Tried: reified pair comparisons (001); counts of faces per value with
variable products (002, 004); a table of all 12376 ways to spread six faces,
in scrambled (003) and fewest-distinct-values-first (005) order; counts with
`element/3` per face of the winner (007, 009, 010), with dice labelled in
different orders and values middle-out and `down`.
Diagnostics in attempts 006 and 008 (stderr) show: building the model takes 3 s;
with the table every labelling step costs about 12 ms (tuples_in over 12376
rows), and without it a single die0 candidate near the end of the first
enumeration is reached only after 115 s, then each (die0, die1, die2) prefix
costs seconds to refute. The search has no way to leave a prefix without
completions, which a solver with clause learning does.
