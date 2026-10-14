# Lessons (z3_python)

Measured on this run's evaluator records (execution timeout 180 s):

- Bit-vector models with `z3.BV2Int(...)` outputs and objectives are accepted by the runner
  (`read` evaluates the expression to an integer; `optimum` gets an `IntNumRef`). They solved
  instances the integer encoding of the same constraints timed out on:
  - equal_sized_groups: Int encodings attempt-001/002/003/004 skipped json:2 and json:3
    (execution_timeout); BV attempt-005 checked all 5 instances (json:3 in 74 s).
  - cmo_2012: Int attempt-001 skipped 4 of 5 instances; BV attempt-002 skipped 1 of 5.
  - broken_weights: Int attempt-001 skipped json:3 (m=80); BV attempt-002 checked all 5 (json:3 in 179 s).
  Width must leave room for every intermediate value (products in twice the width, or ZeroExt).
- Replacing `z3.Distinct` over integer sums with "every value occurs exactly once" `PbEq` over
  Boolean match literals: de_bruijn_sequence attempt-001 timed out on 3 of 5 instances, attempt-002
  passed all 5 in under 2 s each.
- Boolean literals + `PbLe`/`PbEq` instead of integer equalities and `Sum(If(...))`:
  progressive party attempt-001 timed out on json:8 (181 s), attempt-002 solved all 9 in <= 5 s.
  coin3_application: adding the implied bound `used <= amount // value` cut the example from 146 s to 18 s.
- Counting `|x_a - x_b|` as the number of separating gaps (`Or`-prefix Booleans over a permutation
  matrix) instead of `Abs`: cabling example 15.7 s -> 1.2 s, json:3 146 s -> 9 s.
- Not a gain: car_sequencing attempt-003 (purely Boolean, outputs as an `If` chain, plus prefix bounds)
  checked 3 of 22 instances against 13 of 22 for attempt-002 (integer `sequence` variables linked to
  Boolean type literals, `PbLe` windows, suffix bounds) and 10 of 22 for attempt-001.
