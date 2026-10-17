# csplib_002_template_design, cvc5_python: lessons

Result: not retained. Accepted on the example (optimum 418) but the 3-template instance
(json:2, optimum 408) times out at 180 s in every formulation tried. instances_checked /
instances_available = 1 / 2 = 0.5, below the 0.8 threshold.

Evaluated attempts (through `manage evaluate`):
- attempt-003: linear case split `Implies(layout == k, printed == k * production)`,
  implied bounds (`sum printed <= n_slots * production`, `n_slots * sum production >= sum demand`).
  Example accepted in about 25 s; json:2 timeout.
- attempt-004: `printed` as a single `Sum` of `If(layout == k, k * production, 0)`.
  Example also timed out (181 s), so the `If` form is much slower than implications.
- attempt-005: layout chosen by Boolean one-hot selectors with pairwise at-most-one, and
  implications on the selectors. Example accepted in about 50 s; json:2 timeout.

Free checks (evaluation.check, not counted): attempt-001 (plain implications) and attempt-002
(same plus a sheet cap of max demand) both timed out on json:2.

Where the time goes: the first two instances are the same up to the name field; the
instances that differ in size have three templates. Proving the optimum (unsat at
`sum production < best`) over three interchangeable templates is the hard step. The
description does not ask for symmetry breaking between templates, so none was added.

Not tried: a different objective-proving scheme (not available through the runner), or
a smaller encoding of the layout as a table of patterns.
