# three_sum

attempt-001 failed with `execution_error`: Pumpkin panicked with "attempt to
divide by zero" in `pumpkin-core/src/math/num_ext.rs`. The instance's `nums`
contains a `0`, so `weighted` produced a term scaled by zero.

The cause is general, not specific to this problem. `AffineView::scaled`
multiplies the existing scale without rechecking it, so it happily builds a
zero-scaled view that `AffineView::new`'s own `assert_ne!(scale, 0)` would have
rejected; the division by that scale then happens inside a propagator. Pumpkin's
own `boolean_less_than_or_equals` and `boolean_equals` scale each literal by its
weight, so they hit the same path.

Fixed in the integration rather than in this model, because instance data
containing a zero weight is ordinary: `weighted` now drops zero-coefficient
terms, `bool_le`/`bool_sum_eq` drop zero-weighted pairs, `c(0, ..)` fails with a
message instead of building a broken term, and a term list emptied by that
filtering still posts a valid constraint over a variable fixed at zero. Guarded
by a `zero_coefficients` check in `solvers/pumpkin_rust/readiness_test.py`.

attempt-002 carries the same model bytes, re-evaluated against the rebuilt image
and its fresh readiness record. The repair was to the integration, so the model
had nothing to change.
