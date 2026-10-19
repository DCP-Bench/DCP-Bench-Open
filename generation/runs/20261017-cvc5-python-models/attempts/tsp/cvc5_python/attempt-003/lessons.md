# tsp / cvc5_python lessons

All three attempts were accepted at the top level, but only 1 of 5 instances was
checked: the 4 others hit execution_timeout (180 s). Retain needs 0.8, so none was kept.

- attempt-001: successor Ints, Distinct, position chain (Implies), cost Ints via Implies.
  Timeouts on the 12-city example and on the 20-city instances.
- attempt-002: Boolean edge variables with degree sums, MTZ-style positions, total as a
  bounded Sum of If. Same 1/5 result, same timeouts.
- attempt-003: attempt-002 plus data-derived lower bounds (sum of cheapest out-leg,
  sum of cheapest in-leg). Same 1/5 result.

Reading: the 12-city instance times out too, so the cost is the optimality proof
(tightening `total < best` until unsat), not the encoding size. The skill's known gap
applies: the runner rebuilds the Solver, so `QF_LIA` or `tlimit-per` set by the model
are ignored. Not tried: a different encoding of the distance sum (for example, Ints per
leg with a precomputed sorted table), or an encoding that gives cvc5 a smaller search space.
