# Sources for `huub-rust`

Tested with huub 100.1.0 (crate, MPL-2.0), Rust 1.98.1 and g++ 12.2 on Linux with Docker.
The skill text is Apache-2.0.

Existing skills: not searched for beyond the spike that preceded this skill. Run
`npx skills find huub` before a public release.

Documentation this skill's instructions were written from:

- <https://crates.io/crates/huub> — the crate, version 100.1.0, licence MPL-2.0.
- <https://docs.rs/huub/100.1.0/huub/> — the crate-level API reference.
- <https://github.com/huub-solver/huub> — repository and changelog.
- <https://huub.solutions> — project site.
- The vendored crate sources of `huub` 100.1.0 with its locked dependencies (fetched with
  `cargo vendor` in a Rust 1.98.1 container). Every signature in this skill was read from them:
  `model/expressions.rs` (the builders: `linear`, `element`, `unique`), `lower.rs`
  (`LoweringError`, which has a `Simplification` and a `Lowering` conflict variant),
  `solver.rs` (`Status`, `set_terminate_callback`), `solver/solution.rs` (`AnyView`, `Value`,
  `Valuation`), and `constraints.rs` (`Conflict`).

Every claim below was checked by compiling and running it, not from documentation alone.

- `m.lower().to_solver()` returns `(Solver, LoweringMap)`; `map.get(&mut solver, view)` maps a
  model view to a solver view. Constants work through `map.get` (`42.into()`, `true.into()`).
- `minimize` and `maximize` return `(Status, Option<i64>)`. Proven optimum is `(Complete, Some)`,
  infeasibility `(Unsatisfiable, None)`, a stopped search with an incumbent `(Satisfied, Some)`.
- `minimize` after another solve on the same solver returns a stale value (the spike's
  optimum-after-solve trap).
- `all_solutions(views).satisfy()` returns `Complete` when every distinct solution over `views` has
  been listed, and enumerates distinct assignments over the listed views only.
- `assuming(Some(lit))` pins an objective value found with `IntLitMeaning::Eq(v)`; enumeration
  under the pin lists only optimal solutions (10 of 10 in `assets/all-optimal-solutions`).
- Two 2-term equalities over one pair (`x + y == c`, `x - y == d`) hang in `post()` (spike, not
  rerun for this skill). Two inequalities per equality do not: the `le` and `ge` form of a 2-term
  equality with coefficient 3 on a 10^9 domain solves in the readiness suite (`eq2_helper`).
- `element` is 0-based; a 1-based index is `index(i - 1)`.
- `div` truncates toward zero; `mul`, `pow`, `abs`, `minimum` and `maximum` work through `define()`
  or `.result(v)`. `define()` on `linear`, `minimum`, `maximum`, `mul` and `pow` gives the full
  `i64` domain.
- `new_int_decision(5..=3)` panics when the model is lowered. A `post()` after `lower()` has no
  effect on the solver.
- A post that conflicts (`unique` of three values over `0..=1`) returns `Err` at `post()`.
- Circuit by decomposition (successors all different, plus a visiting order that follows them
  through `element`) gives 24 tours on five nodes (`assets/circuit-decomposition`).
- The cumulative schedule with durations 3, 2, 2, usages 1, 2, 1 and capacity 2 has makespan 5.
- The production example (maximise `3x + 2y` under `x + y <= 4`, `x + 3y <= 6`) has optimum 12.
- The `count_eq` pattern (exactly two of four values equal 2 in `0..=2`) has 24 solutions.
- Time limit: the terminate callback stops the search within about a millisecond of the deadline,
  checked on a 2-second budget in the readiness suite (`timeout_cleanup`).
- A tiny submission compiles in about 0.3 s with `-C opt-level=2` in the harness image; the spike
  measured 5 to 10 s for larger models.
- The build needs g++ for CaDiCaL: without it `pindakaas-cadical` fails in its build script.
- Quick start and all six `assets/` run in a Rust 1.98.1 image with g++ (`cargo run --release`),
  and print the expected lines.
