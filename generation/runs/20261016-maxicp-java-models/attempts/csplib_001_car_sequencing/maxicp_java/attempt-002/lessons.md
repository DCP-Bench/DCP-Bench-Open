# csplib_001_car_sequencing, maxicp_java: lessons

Retry of a pair that failed by timeout. attempt-001 used one-hot `m.boolVarArray` per position, so the
registered Booleans were branched before the sequence. attempt-002 registers only the sequence
(`m.intVarArray`), links each position to its type and option flags with one `table` per position,
counts types with `sum(bools, demand)`, and adds the window upper bound plus a window lower bound
derived from the complement (`totalNeeds - (before + after) * at_most`).

Results:
- attempt-002 evaluation: example accepted (2 solutions); json:1 through json:21 `execution_timeout`
  at 180 s and skipped. Only 1 of 22 instances checked (about 5%), below the 80% needed to retain.
- Free checks on json:1 timed out with the same encoding before and after the lower bounds, so the
  lower bounds did not change the outcome.

Assessment: the DFS with no learning does not find two solutions within 180 s on the 200-car
instances (demand sums to about 200). This looks like a performance limit of plain DFS on this
instance family, not a wrong model. Not retained. Budget used: 1 of 5 new evaluated attempts.
