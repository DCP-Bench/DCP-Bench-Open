# Setup: pumpkin_rust

Rust library API of the Pumpkin lazy-clause-generation constraint solver.

## Outcome

Ready. All eleven required readiness checks pass against the built image, and
the integration is in the shared pilot suite in `tests/test_solvers.py`.

## Files created

- `solvers/pumpkin_rust/metadata.yaml` — id `pumpkin_rust`, name "Pumpkin (Rust)",
  language `rust`, paradigm `cp`, extension `.rs`, enumeration and compilation true.
- `solvers/pumpkin_rust/Dockerfile`
- `solvers/pumpkin_rust/run.py` — compiles the submission and runs it
- `solvers/pumpkin_rust/rust/driver/` — the prebuilt driver library crate, with
  `Cargo.lock` committed
- `solvers/pumpkin_rust/rust/main.rs` — the binary shim that splices the submission in
- `solvers/pumpkin_rust/readiness_test.py`, `readiness.json` and its evidence
- `solvers/pumpkin_rust/skills/pumpkin-rust/` — the modelling skill
- `tests/fixtures/model.rs` and two lines in `tests/test_solvers.py` — pilot coverage
- `generate_site.py` — a `rust` row in `LANGUAGES` and `.rs` in `EXTENSION_LANGUAGE`

Nothing outside `solvers/pumpkin_rust/` was changed except those last two, which
register the new language with the catalogue. `runner/runtime.py` is untouched;
`run.py` imports only its `finish` helper.

## Versions

- base image `rust:1.98.1-slim-bookworm@sha256:ebd900bae66fd508b466cef82d64a83a5fb34682e4c8b2797a42908bddc95a57`
- rustc / cargo 1.98.1
- `pumpkin-solver` =0.5.0, `serde_json` =1.0.151, whole graph pinned by `Cargo.lock`
- image identity at readiness: `sha256:41d629d6670c7e6a9fdb365dfc4c72821139532548cbb3d9b9991b664cea1459`

## The instance-binding decision

The submission reads the instance, through a typed `Instance` wrapper baked into
the image — the first of the three patterns in the solver-setup skill, matching
`cpmpy_python` and `ortools_cp_sat_python`. Pumpkin's input is an API you call,
not a data file, so the other two patterns buy nothing here.

## Compilation strategy

Evaluation compiles inside a networkless, read-only container with a 512 MiB
tmpfs, so cargo cannot run at evaluation time. Instead the image prebuilds the
driver crate and every Pumpkin crate, keeps the rlibs (and the proc-macro
`.so`s) under `/opt/rust`, and run.py invokes `rustc` once against them. Only
the one-file submission compiles per evaluation: measured 0.2-1.3 s, against a
300 s budget. Copying a Cargo target directory into tmpfs was the alternative
and was rejected: 152 MiB per container, charged to the memory cgroup.

## Problems hit, and the fix

- `pumpkin-solver`'s build script calls `git` and, without `NO_CHECKERS=true`,
  compiles proof checkers from a `tests/` directory the published crate omits.
  The Dockerfile installs git for the build layer only and sets NO_CHECKERS.
- `python3-minimal` has no `json` module; the image needs full `python3`.
- Copying only `*.rlib` out of the target directory leaves the proc-macro
  dependencies behind, which rustc reports as "can't find crate" for the driver
  rather than for the missing crate. Copying `*.so` too fixes it.

## Capabilities and limits

Satisfaction, minimisation, maximisation and enumeration all tested. Optimality
is reported only on `OptimisationResult::Optimal`; a solution found but not
proven optimal is reported as a timeout, never as success. Pumpkin has no
modulo, no global cardinality, no automaton and no dedicated all-different
propagator (it decomposes to pairwise disequalities); the modelling skill says
so and gives the decompositions.
