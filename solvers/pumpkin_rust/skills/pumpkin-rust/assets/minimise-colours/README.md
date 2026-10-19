# Minimise the number of colours (optimise)

**Problem:** colour the Petersen graph (10 vertices, 15 edges) so that no edge joins two equal colours, using as few colours as possible.
**Shows:** counting distinct values with `maximum` and a minimised bound, reporting `optimum + 1` as the count, `OptimisationResult::Optimal`.
**Run:** `NO_CHECKERS=true cargo run --quiet`
**Expected:** `chromatic number: 3`
