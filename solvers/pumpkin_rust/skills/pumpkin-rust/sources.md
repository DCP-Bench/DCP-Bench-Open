# Sources for `pumpkin-rust`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://crates.io/crates/pumpkin-solver> — the crate, its feature list and
  the `cargo add pumpkin-solver` installation route, accessed 2026-09-18.
  Records that Pumpkin is a lazy-clause-generation CP solver from ConSol Lab at
  TU Delft, and that the library API lives in `pumpkin-core`.
- <https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/> — the crate-level
  documentation, whose worked examples are the source for `Solver::satisfy`,
  `Solver::optimise` with `LinearSatUnsat`, and `get_solution_iterator`.
- The vendored crate sources of `pumpkin-solver`, `pumpkin-core`,
  `pumpkin-constraints` and `pumpkin-conflict-resolvers` 0.5.0, read inside the
  build container. These are authoritative over the rendered documentation, and
  every signature in this skill was taken from them.
- `solvers/pumpkin_rust/rust/driver/src/lib.rs`, `run.py` and `Dockerfile` in
  this repository — the driver contract this skill describes.

Every claim below was checked by compiling and running it inside the
integration image during the run recorded at
`generation/runs/20260918T0000Z-pumpkin-a7f3`, not taken from documentation
alone.

- `cp.element` and `cp.element_of` index **0-based**: a table `[10, 20, 30, 40]`
  at index 1 yields 20.
- `cp.div` truncates toward zero: `-7 / 2` is `-3`, not `-4`.
- The modulo decomposition `a == k*q + r` with `0 <= r < k` reproduces
  `23 mod 7 == 2`. Pumpkin has no modulo constraint of its own; the constraint
  list in `pumpkin-constraints/src/constraints/` is the whole vocabulary.
- `cp.is` pins an indicator in both directions, through
  `NegatableConstraint::reify`; `implied_by` alone is half-reification and
  leaves the indicator free.
- `all_different` in `pumpkin-constraints/src/constraints/all_different.rs`
  expands to pairwise `binary_not_equals`, so it carries no dedicated
  propagator. That is read off the source; the consequence for solving time is
  an expectation, not something benchmarked here.
- `Literal` is a 0/1 `AffineView<DomainId>`, which is why a `Lit` enters a
  linear constraint through `t(...)` and negates with `!`.
- `pumpkin-solver`'s build script shells out to `git` and, without
  `NO_CHECKERS=true`, compiles proof checkers from a `tests/` directory the
  published crate does not ship. Both are handled in the Dockerfile.
- A zero coefficient in a linear constraint panics inside Pumpkin with "attempt
  to divide by zero" at `pumpkin-core/src/math/num_ext.rs`. `AffineView::new`
  asserts `scale != 0`, but `AffineView::scaled` multiplies the existing scale
  without rechecking, so a zero-scaled view escapes that assert; Pumpkin's own
  `boolean_less_than_or_equals` and `boolean_equals` scale by their weights and
  reach the same path. Observed on the `three_sum` instance, whose `nums`
  contains a zero; absorbed in the driver and guarded by the `zero_coefficients`
  check in `readiness_test.py`.
- Proc-macro dependencies build to `.so` rather than `.rlib`, so an image that
  copies only `*.rlib` out of the Cargo target directory fails at link time with
  a misleading "can't find crate" for the driver itself.
