# pumpkin_rust: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how Pumpkin in
Rust expresses it. Runner: [run.py](run.py), which compiles [rust/main.rs](rust/main.rs)
with the submission spliced in and runs the binary. The harness is the `dcp_pumpkin`
library, [rust/driver/src/lib.rs](rust/driver/src/lib.rs): it defines `Instance`,
`Model` and `run`, which owns solving, enumeration and printing.

## Submission file

One Rust file, `model.rs`. `main.rs` is

```rust
use dcp_pumpkin::prelude::*;
include!("/input/model.rs");
fn main() { dcp_pumpkin::run(build); }
```

so the file is a list of items (functions, structs, consts) in the root of a binary crate
that has already glob-imported the prelude: `Instance`, `Model`, `Node`, `IntoNode`,
`Dir`, `Var` (`DomainId`), `Lit` (`Literal`), `Term` (`AffineView<DomainId>`), `Solver`,
the `pumpkin_solver` crate, `TransformableVariable` (for `.scaled(k)` / `.offset(k)`),
`serde_json::Value` and `json!`. Everything else must come from `std` or be reached
through `pumpkin_solver::...`; no other crate is linked.

## Entrypoint

```rust
fn build(inst: &Instance, solver: &mut Solver) -> Model
```

`solver` is `pumpkin_solver::Solver` itself; post constraints on it with Pumpkin's own
constructors. `run` calls `build` once and then solves.

## Instance

`inst` wraps the instance JSON. Its accessors panic, naming the field and the value found,
instead of defaulting; integers must fit in `i32`; arrays are `Vec`s, 0-based:

| Accessor | Returns |
| --- | --- |
| `inst.int(k)` / `inst.int_or(k, fallback)` | `i32` |
| `inst.size(k)` | `usize` (a nonnegative int) |
| `inst.flag(k)` | `bool` (a JSON Boolean) |
| `inst.ints(k)` / `inst.flags(k)` / `inst.strings(k)` | `Vec<i32>` / `Vec<bool>` / `Vec<String>` |
| `inst.matrix(k)` | `Vec<Vec<i32>>` (rows may differ in length) |
| `inst.cube(k)` | `Vec<Vec<Vec<i32>>>` |
| `inst.len(k)` | length of an array field |
| `inst.has(k)` / `inst.keys()` | presence / sorted field names |
| `inst.get(k)` | the raw `&serde_json::Value`, for any other shape |

A panic ends the process nonzero, reported as status `error`.

## Outputs

Return a `Model` holding the declared outputs:

```rust
let mut m = Model::new();
m.put("x", xs);   // Var, Lit, i32, bool, Node, Vec<T>, &[T] or &Vec<T> of these
m
```

Nested `Vec`s give nested arrays. A `Var` renders as an integer, a `Lit` as
`true`/`false`, `i32`/`bool` constants verbatim. `put` panics on a repeated name; an empty
`Model` is an `error`. A declared name missing from the model is only a warning on stderr
from the harness, so the evaluator, not the run, rejects it. A `Term` (`x.scaled(k)`)
is not an output: tie it to a fresh `Var` with `equals`.

## Objective

`m.minimise(var)` or `m.maximise(var)`, where `var` is a single `Var`; tie it to the
objective expression with a constraint.

## Solving

- `run` uses the `Solver` it passed to `build` (`Solver::default()`), Pumpkin's
  `default_brancher()` and a `ResolutionResolver`; the model cannot change them.
- With an objective it calls `optimise` with `LinearSatUnsat`: `Optimal` is the first
  solution, `Unsatisfiable` is `unsat`, and `Satisfiable`, `Stopped` or `Unknown` is
  `timeout`. It then posts `var == optimum` and enumerates with `satisfy`.
- After each solution it adds a clause over the `Var` and `Lit` leaves of the model
  (each must differ from its reported value); `i32`/`bool` constant leaves are not
  part of it. `Unsatisfiable` from `satisfy` is exhaustion (`complete`, or `unsat` with
  nothing reported); `Unknown` is `timeout`; it stops at `limit` once enough are out.
- The budget is `execution_timeout`, counted from the binary's start (so `build` spends
  it); each `optimise`/`satisfy` call gets what is left as a `TimeBudget`. The runner
  kills a binary still running 15 s after that and reports `timeout`; a nonzero exit (a
  panic) is `error`.

## Compilation

Yes. One `rustc --edition 2021 -C opt-level=2 -C codegen-units=1` invocation on
`main.rs`, linked against the prebuilt `libdcp_pumpkin.rlib` and its dependencies (no
Cargo, no network). Budget: `compilation_timeout` (default 120 s); a failure or overrun
is `compilation_error` with rustc's output on stderr. The binary then has
`execution_timeout` (see [Solving](#solving)).

## Environment

Image `dcp-eval/pumpkin_rust:v1`: Rust 1.98.1 (`rustc` and `cargo` on `PATH` under
`/usr/local/cargo/bin`), `pumpkin-solver` 0.5.0, `serde_json` 1.0.151 as the JSON
library (reached through the prelude's `Value` and `json!`), Python 3.11.2 for the
runner. The harness crate and all its dependencies were built once at image build
(Cargo.lock committed, `--locked`, with `NO_CHECKERS=true` and a temporary `git` for
`pumpkin-solver`'s build script) and kept only as `/opt/rust/libdcp_pumpkin.rlib` plus
`/opt/rust/deps/*.rlib` and proc-macro `.so` files. `git`, the Cargo registry and the
target directory were then removed, so no crate can be fetched or rebuilt; submissions
never need them, because `rustc` links only against those prebuilt artifacts. The
evaluator runs the container with no network, a read-only root file system, user 65534,
`HOME=/tmp`, a 512 MiB writable `/tmp` and `/input` read-only. For an ad hoc build,
override the entrypoint and run the runner's `rustc` command (`RUSTC` in
[run.py](run.py)) with the file mounted at `/input/model.rs`: `docker run --rm --network
none -v $PWD/model.rs:/input/model.rs:ro --entrypoint sh dcp-eval/pumpkin_rust:v1 -c
'rustc --edition 2021 /opt/rust/main.rs -o /tmp/c --extern
dcp_pumpkin=/opt/rust/libdcp_pumpkin.rlib -L dependency=/opt/rust/deps'`.

## Traps

- **No `fn main`**, and no `#![...]` crate attributes or `//!` doc comments: the file is
  `include!`d next to the harness's `main`.
- **No `extern crate` or new dependencies**: only `dcp_pumpkin` is passed to rustc.
  Prelude names need no `use`; reach other Pumpkin items through `pumpkin_solver::`.
- **Do not print to stdout** (`println!`): the binary's stdout is the runner protocol.
  Use `eprintln!` for logs.
- **The objective must be a `Var`**, not a `Lit`, `Term` or expression.

## Example

The pilot fixture [tests/fixtures/model.rs](../../tests/fixtures/model.rs) (instance
fields `n`, `optimize`; outputs `x`, `y`):

```rust
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.int("n");
    let x = solver.new_bounded_integer(0, n);
    let y = solver.new_bounded_integer(0, n);
    let mut m = Model::new();
    m.put("x", x);
    m.put("y", y);
    let tag = solver.new_constraint_tag();
    if inst.flag("optimize") {
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![x.scaled(-1), y.scaled(-1)], -n, tag))
            .post();
        let total = solver.new_bounded_integer(0, 2 * n);
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![x.scaled(1), y.scaled(1), total.scaled(-1)], 0, tag))
            .post();
        m.minimise(total);
    } else {
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![x.scaled(1), y.scaled(1)], n, tag))
            .post();
    }
    m
}
```
