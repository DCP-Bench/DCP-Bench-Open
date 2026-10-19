# coins_grid, eclipse_clp: lessons

- attempt-001 (plain 0/1 grid, row and column sums, cost z, default labeling): the optimum
  proof on the example (10x10, c=5) ran out of the 180 s budget. Rejected as `execution_timeout`.
- attempt-002 (adds per-row and per-column cost bounds, cost-sorted cell order with
  `indomain_max`): still timed out on the example. Its first evaluation attempt was disturbed by
  a container left running on the host and was not counted; the model was not evaluated.
- Ad hoc timing (not an attempt): the same model with the cells in row-major order and
  `search(..., input_order, indomain_max, ...)` proves the example optimum (200) in about 1 s.
  With `indomain_min` the same order did not finish in 170 s. Row-major order is what made the
  difference: each finished row fixes its cost and tightens the bound on the rest.
- attempt-003 (row-major order, `indomain_max`, row and column cost bounds): accepted, 4 of 5
  instances checked. The 12x12 instance (json:4) reached `execution_timeout` during search, so it
  is recorded as a performance limit (ratio 0.8).
