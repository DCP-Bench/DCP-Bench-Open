# Lesson: tie a wide total by a pruned running sum, and pay on grouped thresholds

All three attempts declare `max_revenue`, an int whose domain spans thousands of values.

- attempt-001: total tied by an adder-encoded PB equality over its binary digits,
  objective as one soft clause per unit sold (weight = unit revenue). json:2 took 58 s,
  json:3 timed out.
- attempt-002: same tie, objective on the digits of the total (binary search). Worse:
  json:2 and json:3 both timed out.
- attempt-003: total tied by a running sum over the packages (one literal per partial
  sum, pruned to the window [greedy feasible revenue, sum of caps]), which unit
  propagation evaluates; objective as soft clauses on the total's order thresholds with
  weights in about sqrt(N) groups (weight 1 + (upper - v) // (isqrt(N) + 1)). All five
  instances accepted, slowest 5.0 s.

General point for the skill: when an output total has a wide domain, a running sum
pruned to a valid window often stays small (here at most 160k clauses) and propagates
fully, unlike an adder; and grouped-weight thresholds on the total keep RC2's core
count near sqrt(N).
