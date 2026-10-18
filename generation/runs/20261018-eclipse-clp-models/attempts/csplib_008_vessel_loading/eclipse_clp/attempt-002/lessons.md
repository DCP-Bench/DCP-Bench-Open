# Lessons, csplib_008_vessel_loading, attempt 002

Accepted: 5 of 5 instances checked, retained.

- Convention: bottom = top - y_extent (top is the high edge), right = left + x_extent (exclusive). Same as the reference on `example`.
- Redundant cell-owner view (Owner per deck cell, Cv = (Owner #= k) times four reified bounds). Full deck (json:1 areas sum to 256): owners labelled first, `input_order`/`indomain_max`, then rotations, lefts, tops.
- Trap hit: a `foreach` loop in `cell_view` used the outer `Boxes` without `param/1`. The warning was `Singleton local variable Boxes`, the cell constraints silently did nothing, and json:1 timed out at 180 s. A plain recursive predicate fixed it.
