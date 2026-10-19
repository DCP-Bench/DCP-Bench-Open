# Infeasible at post

**Problem:** three pairwise-different values, each in 0..=1.
**Shows:** that `post()` returns `Result`, and that an `Err` means the constraint already conflicts.
**Run:** `cargo run --release`
**Expected:** `infeasible: a constraint conflicts when it is posted`
