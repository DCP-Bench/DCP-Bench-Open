# Lessons from attempts 001-006 (catfood2 = example, catfood3 = json:2)

- 001 (adder demand PBs, objective on production digits): example 14.7 s, json:2 timeout.
- 002 (BDD demand PBs): example 9.6 s, json:2 timeout.
- 003 (+ order-encoded total with grouped-weight thresholds, upper bound from a
  one-template plan): example 3.7 s; json:2 found its optimum (408, equal to the
  sum(demand)/n_slots bound) but the second enumerated solution timed out.
- 004 (+ digit pairs as exact ANDs): json:2 timeout with no solution.
- 005 (unary shares and quadratic unary merges instead of digits): example 34.7 s,
  json:2 timeout.
- 006 (004 + implied per-variation upper bound: copies of v <= n_slots * total -
  other demands): both accepted, json:2 in 23 s.

The implied upper bound mattered most: with the optimum at the slot bound the
coverage slack is 7 copies in total, and stating it lets propagation see that.
