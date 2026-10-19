# lessons: csplib_002_template_design, huub_rust

Result: attempts 002 and 003 accepted on the 2-template example (optimum 418) and
timed out on json:2 (3 templates, optimum 408, "the optimum was not proven" at 180 s).
json:2 is skipped, so instances_checked / instances_available = 1/2 < 0.8: not retained.

Tried, all unproven on json:2 within 180 s (checked with evaluation.check, not attempts):
- product as `m.mul(p, l).define()` with a bound on the result (attempt 001 style): timeout.
- product written per copy count k with `implied_by(b)` links, one-hot over the layout value
  (attempt 002/003): timeout. Using `reified_by` here is wrong: it is an equivalence, and
  the model became infeasible during lowering.
- added the implied per-template constraint sum_j copies_tj <= n_slots * sheets_t: no change.
- creating the layout variables before the sheet variables: no change.

Reasoning: total demand is 3665 and each sheet holds 9 copies, so the optimum of 408 leaves
7 unused slots out of 3672. The difficulty is finding an exact packing, not proving the bound.
Restarts are off in the runner, so a wrong early choice is not undone.

Not tried: a table over the feasible layout rows per template, or a different search shape.
