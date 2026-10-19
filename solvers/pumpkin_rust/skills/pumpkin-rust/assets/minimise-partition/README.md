# Balanced split (minimise)

**Problem:** split the weights 3, 1, 4, 2, 2 into two groups so that the heavier group is as light as possible.
**Shows:** Boolean choices with `boolean_equals` for both groups (negated literals for the second), a max-style bound by `less_than_or_equals`, `minimise`.
**Run:** `NO_CHECKERS=true cargo run --quiet`
**Expected:** `heavier group weight: 6`
