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
objective expression with a constraint. The harness optimises with `LinearSatUnsat` and
accepts only `OptimisationResult::Optimal`; `Satisfiable` or `Stopped` is `timeout`.
It then posts `var == optimum` and enumerates, adding a clause that blocks the reported
values of the declared output variables after each solution.

## Compilation

Yes. One `rustc --edition 2021 -C opt-level=2 -C codegen-units=1` invocation on
`main.rs`, linked against the prebuilt `libdcp_pumpkin.rlib` and its dependencies (no
Cargo, no network). Budget: `compilation_timeout` (default 120 s); a failure or overrun
is `compilation_error` with rustc's output on stderr. The binary then has
`execution_timeout`, measured from when it starts and so including `build` (the runner
kills it 15 s after that).

## Environment

Image `dcp-eval/pumpkin_rust:v1`: Rust 1.98.1, `pumpkin-solver` 0.5.0, `serde_json`
1.0.151 (Cargo.lock committed, built `--locked`).

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
