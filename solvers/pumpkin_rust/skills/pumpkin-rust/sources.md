# Sources for `pumpkin-rust`

Tested with pumpkin-solver 0.5.0, Rust 1.98.1 (image `dcp-eval/pumpkin_rust:v1`), Linux with Docker.

Existing skills: none recorded. This skill was refactored from the DCP-Bench integration skill, which is not a public skill.

Refactored from the DCP-Bench integration skill; examples verified inside the dcp-eval/pumpkin_rust:v1 image.

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://crates.io/crates/pumpkin-solver> — the crate, its feature list and
  the `cargo add pumpkin-solver` installation route, accessed 2026-09-18.
  Records that Pumpkin is a lazy-clause-generation CP solver from ConSol Lab at
  TU Delft, and that the library API lives in `pumpkin-core`.
- <https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/> — the crate-level
  documentation, whose worked examples are the source for `Solver::satisfy`,
  `Solver::optimise` with `LinearSatUnsat`, and `get_solution_iterator`.
  Constraints are posted as `solver.add_constraint(<constructor>(vars, .., tag)).post()`.
- <https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/core/proof/struct.ConstraintTag.html>
  — what a constraint tag is for.
- <https://github.com/consol-lab/pumpkin> — repository, licence (MIT OR Apache-2.0) and changelog.
- The vendored crate sources of `pumpkin-solver`, `pumpkin-core`,
  `pumpkin-constraints` and `pumpkin-conflict-resolvers` 0.5.0 (the crates.io
  packages, fetched with `cargo vendor` inside the image). These are authoritative
  over the rendered documentation, and every signature in this skill was taken from them.
- The DCP-Bench driver's `run` loop (`solvers/pumpkin_rust/rust/driver/src/lib.rs` in the
  repository) — the reference for the satisfy, optimise, blocking-clause and
  `OptimisationResult` handling used in the examples.

Every claim below was checked by compiling and running it inside the
integration image, not taken from documentation alone.

- `pumpkin_solver::element` indexes **0-based**: a table `[10, 20, 30, 40]` at
  index 1 yields 20.
- `pumpkin_solver::division` truncates toward zero: `-7 / 2` is `-3`, not `-4`.
- The modulo decomposition `a == k*q + r` with `0 <= r < k` reproduces
  `23 mod 7 == 2`. Pumpkin has no modulo constraint of its own; the constructor
  list in `pumpkin-constraints/src/` is the whole vocabulary.
- `.reify(flag)` on a posted constraint pins an indicator in both directions
  (3 solutions over `x in 0..2` and the flag), `.implied_by(flag)` alone is
  one-way (4 solutions).
- `all_different` in `pumpkin-constraints/src/constraints/all_different.rs`
  expands to pairwise `binary_not_equals`, so it carries no dedicated
  propagator. That is read off the source; the consequence for solving time is
  an expectation, not something benchmarked here.
- `Literal::scaled` returns `AffineView<Literal>`, which does not mix with
  `AffineView<DomainId>` terms in one `vec!` (E0308). `Literal::get_integer_variable()`
  returns the 0/1 `AffineView<DomainId>`, which does. `!lit` negates.
- `pumpkin-solver`'s build script runs `git rev-parse HEAD` and panics when git
  is not on PATH (`Failed to execute git command`). Without `NO_CHECKERS=true`
  it compiles proof checkers from a `tests/` directory the published crate does
  not ship, and fails with `No such file or directory`.
- `DomainId::scaled(0)` and `Literal::scaled(0)` panic at once with
  `Multiplication by zero is not invertable` (`AffineView::new` asserts the scale).
  `scaled` on a view that is already scaled multiplies the scale without that
  check, so `x.scaled(2).scaled(0)` builds, and the constraint then panics during
  search with `attempt to divide by zero` at `pumpkin-core/src/math/num_ext.rs`.
- `TransformableVariable` has to be imported for `x.scaled(k)` (`no method named
  'scaled' found for struct 'DomainId'`); `PredicateConstructor` for
  `disequality_predicate` on an integer variable.
- The linear constraints accept a plain `Vec<DomainId>` where every coefficient is
  1: `equals(vec![x, y], 3, tag)` solves with 3 solutions.
- `greater_than_or_equals`, `greater_than`, `less_than` and `plus` exist in
  `pumpkin-constraints` 0.5.0 and behave as named (2, 2 and 2 solutions, and 3
  solutions of `a + b == 2`). An earlier version of this skill said there was no
  `greater_than_or_equals`; that was wrong for 0.5.0.
- A `SatisfactionResult` borrows the solver and the resolver: matching on it at the
  end of `main` or while calling `add_clause` fails to compile (E0597, E0499).
  Binding it with `let` first, and adding the blocking clause after the match, compiles.
- Enumeration by blocking the printed variables gives every distinct answer once:
  10 coin-change solutions, and 2 optimal selections after posting the optimum.
- `cumulative` with capacity 1 and unit demands gives a non-overlapping schedule:
  durations 3, 2, 2 with a precedence give makespan 7.
- The optimum of the production example is 12 (`x = 4, y = 0`); the optimum of the
  partition example is 6, with the heavier group of weight 6.
- `[[bin]] path = "models/<problem>.rs"` with no `src/main.rs` builds and runs, with
  `serde_json = "=1.0.151"` as the instance reader (graph colouring from `instances/petersen.json`).
- The instance reader (`read_instance` with `serde_json::from_str`) compiles and reads the
  JSON, and `serde_json::json!` prints the answer.
- `maximum(colours, top, tag)` with `LinearSatUnsat::Minimise` on `top` proves the Petersen
  graph needs 3 colours (`top` optimum 2, colours start at 0): the `minimise-colours` example.
- Timing, `jobshop` from the toy problems, release build: ft06 (optimum 55) and small (optimum 11)
  each finished in about 1.7 s wall time, including `cargo run` with the binary already built.
- The git requirement is read from `pumpkin-solver/build.rs`: `Command::new("git").args(["rev-parse", "HEAD"])`
  with `.expect`. Only stdout is read, so a git outside a repository works (the exit status is not
  checked). A stub that exits 0 with no output also built in verification, leaving `GIT_SHA` empty.
- Offline build: `cargo vendor` run in the image with network, then `CARGO_HOME` holding a config that
  replaces crates-io with the vendored directory, and `--network none`. The project-level `.cargo/config.toml`
  form is standard cargo behaviour and was not run in this environment.

## Independent toy-problem test (round 1)

An independent agent solved the `add-solver` toy problems from this skill alone, using only
`problem.md` and `instances/`, with `scripts/run_toy_tests.py` as the checker. The agent had to add
the offline mounts and a git shim to build (see the Install section), so the result counts the skill
as tested with those harness steps. Result: **18/18 instances passed**, zero model repairs.

| Problem | Instance | Result |
|---|---|---|
| cryptarithm | ab-ab-aaa | PASS, infeasibility reported |
| cryptarithm | send-more-money | PASS, feasible solution |
| cryptarithm | two-two-four | PASS, feasible solution |
| graph-colouring | cycle6 | PASS, optimal (2) |
| graph-colouring | k4-tail | PASS, optimal (4) |
| graph-colouring | petersen | PASS, optimal (3) |
| jobshop | ft06 | PASS, optimal (55) |
| jobshop | small | PASS, optimal (11) |
| knapsack | p01 | PASS, optimal (309) |
| knapsack | small | PASS, optimal (15) |
| knapsack-all-optimal | fourteen | PASS, all 9 optimal solutions |
| knapsack-all-optimal | ties | PASS, all 5 optimal solutions |
| knapsack-all-optimal | unique | PASS, all 1 optimal solutions |
| n-queens | n3 | PASS, infeasibility reported |
| n-queens | n4 | PASS, feasible solution |
| n-queens | n8 | PASS, feasible solution |
| n-queens-all | n6 | PASS, all 4 solutions |
| n-queens-all | n8 | PASS, all 92 solutions |

Totals: 18/18 passed. Tester's models: `scratchpad/skill-refactor/pumpkin_rust/test/models/`; results: `scratchpad/skill-refactor/pumpkin_rust/test/results.txt`.
The tester's findings (install without network, no git in the image, no JSON reading, one model file outside `src/`, graph colouring count, time budget) are each addressed in SKILL.md: [Install](SKILL.md#install), [Offline builds](SKILL.md#offline-builds), [Modelling](SKILL.md#modelling), [Solving](SKILL.md#solving) and [Common issues](SKILL.md#common-issues).
