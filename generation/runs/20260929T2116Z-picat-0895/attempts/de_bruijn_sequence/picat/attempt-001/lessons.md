# de_bruijn_sequence / picat, attempt 1

Rejected with `invalid_solution` on the first instance: every returned sequence
was all zeros or all ones, although the values of the strings are constrained
to be all different.

Cause: a defect in Picat 3.9#12's `sat` module, not in the model. When
`all_different/1` (or `all_distinct/1`) is posted on variables that are also
defined from 0/1 variables by a linear equality such as `Z #= 2 * A + B`, the
solver returns assignments that break the equalities. `sat_all_different_probe.pi`
next to this file reproduces it without the driver: two variables over 0..3,
all different, each equal to `2 * A + B` over its own two bits, give 192
solutions under `sat` and the correct 12 under `cp`, whether `all_different`
is posted before or after the equalities. Pairwise `#!=` gives 12 under both.

Repair (attempt 2): the same model with `import cp.`, which returned the 24
solutions of the reduced case in a probe.
