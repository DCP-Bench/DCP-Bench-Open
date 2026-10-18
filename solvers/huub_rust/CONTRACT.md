# huub_rust: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how Huub in
Rust expresses it. Runner: [run.py](run.py), which compiles [rust/main.rs](rust/main.rs)
with the submission spliced in and runs the binary. The harness is the `dcp_huub`
library, [rust/driver/src/lib.rs](rust/driver/src/lib.rs): it defines `Instance`, `Out`,
the helpers `eq2`, `count_eq` and `circuit`, and `run`, which owns lowering, optimisation,
enumeration and printing.

## Submission file

One Rust file, `model.rs`. `main.rs` is

```rust
use dcp_huub::prelude::*;
include!("/input/model.rs");
fn main() { dcp_huub::run(build); }
```

so the file is a list of items (functions, structs, consts, `use` declarations) in the
root of a binary crate that has already glob-imported the prelude. The prelude gives:
`Instance`, `Out`, `Node`, `IntoNode`, `Res`, `Model`, `View`, `IntLinearExp`,
`BoolFormula`, `Conflict`, `Set` (Huub's set type, for `contains`), `eq2`, `count_eq`,
`circuit`, and `serde_json`'s `Value` and `json!`. Anything else comes from `std` or from
`dcp_huub::huub::...`; no other crate is linked. Do not define `fn main`, do not write
`#![...]` crate attributes or `//!` doc comments, and do not use `extern crate`.

## Entrypoint

```rust
fn build(inst: &Instance, m: &mut Model) -> Res<Out>
```

`m` is Huub's own `huub::model::Model`, passed in empty. Post constraints on it with
Huub's modelling API and return the declared outputs in an `Out`. `run` calls `build`
once, then lowers and solves. `Res<T>` is `Result<T, Conflict<View<bool>>>`: every
`post()` returns a `Result`, and the submission propagates it with `?`.

## Instance

`inst` wraps the instance JSON. Accessors panic, naming the field and the value found,
instead of defaulting. Integers are `i64` (64-bit); arrays are `Vec`s, 0-based:

| Accessor | Returns |
| --- | --- |
| `inst.int(k)` / `inst.int_or(k, fallback)` | `i64` |
| `inst.size(k)` | `usize` (a nonnegative int) |
| `inst.flag(k)` | `bool` (a JSON Boolean) |
| `inst.ints(k)` / `inst.flags(k)` / `inst.strings(k)` | `Vec<i64>` / `Vec<bool>` / `Vec<String>` |
| `inst.matrix(k)` | `Vec<Vec<i64>>` (rows may differ in length) |
| `inst.cube(k)` | `Vec<Vec<Vec<i64>>>` |
| `inst.len(k)` | length of an array field |
| `inst.has(k)` / `inst.keys()` | presence / sorted field names |
| `inst.get(k)` | the raw `&serde_json::Value`, for any other shape |

A panic ends the process nonzero, reported as status `error` with the panic message.

## Outputs

Build an `Out`, `put` each declared output, and return it:

```rust
let mut out = Out::new();
out.put("x", x).put("flags", flags).put("k", 42i64);
Ok(out)
```

`put` takes a `View<i64>` (an integer), a `View<bool>` (a Boolean), an `i64` or `bool`
constant, or a `Vec`, `&[T]` or `&Vec<T>` of these, which gives nested arrays. A repeated
name panics. The harness does not compare names with the brief: a missing or extra name
is rejected by the evaluator. An `Out` with no outputs is an `error`. Constants are reported verbatim. Leaves are integers and
Booleans only: a Boolean is written `true`/`false`. Integer outputs carry the full 64-bit
range (the output `30000000002` is accepted).

## Objective

`out.minimise(view)` or `out.maximise(view)`, where `view` is one `View<i64>`. An objective
expression is tied to a view first, for example `let obj = m.new_int_decision(lo..=hi);
m.linear(x * 3 - y * 2 + 7).eq(obj).post()?;`, or with `.define()` on a variable whose
domain is known. Set at most one objective; a satisfaction problem sets none.

## Solving

The runner forces:

- The lowering defaults: `m.lower().to_solver()` with `int_eager_limit` 255 and restarts
  off. Search is Huub's default; the submission cannot change it.
- Phase 1, when there is an objective: `minimize` or `maximize` is the first and only
  solve on a fresh solver. Its result maps as follows:

  | Huub result | Reported |
  | --- | --- |
  | `(Complete, Some(v))` | optimum `v` proven; go on to phase 2 with the objective pinned to `v` |
  | `(Unsatisfiable, _)` | `unsat` |
  | `(Satisfied, Some(_))` | `timeout` with detail `the optimum was not proven`; no solution is emitted |
  | anything else | `timeout`; no solution is emitted |

- Phase 2: `assuming(pin)` (the pinned objective, or none) with `all_solutions` over the
  output views. Solutions are distinct on the declared outputs, so auxiliary variables do
  not repeat a row. Each solution is printed as it is found. The runner stops after
  `solution_limit` rows, and drops any further row the solver delivers before it stops.
  Status: `limit` when the cap was reached, `complete` when the search space is exhausted,
  `unsat` when there is no solution at all, `timeout` otherwise.
- Conflicts found while posting (an `Err` from a `post()`) or while lowering (a conflict in
  `to_solver()`) are infeasibility: status `unsat`.
- Time budget: one terminate callback for both phases, set to `execution_timeout` from the
  start of the binary (so `build` and lowering spend it). On expiry the solver stops in
  about a millisecond. The runner kills a binary still running 15 s after that and reports
  `timeout`; a nonzero exit (a panic) is `error`.

## Compilation

Yes. One `rustc --edition 2021 -C opt-level=2 -C codegen-units=1 -D unused_must_use`
invocation on `main.rs`, linked against the prebuilt `libdcp_huub.rlib` and its
dependencies (no Cargo, no network). `-D unused_must_use` turns an ignored `Result`, and so
an ignored `post()`, into a compile error. Budget: `compilation_timeout` (default 120 s); a
failure or overrun is `compilation_error` with rustc's output on stderr. Warnings go to
stderr and do not fail the build.

## Environment

Image `dcp-eval/huub_rust:v1`, built from `rust:1.98.1-slim-bookworm` pinned by digest:

- Rust 1.98.1 (`rustc` and `cargo` on `PATH`); Huub `huub` 100.1.0 with its locked
  dependencies (`pindakaas` 0.2.3, `pindakaas-cadical` 0.2.1, `bon` 3.10.2), and
  `serde_json` 1.0.151. The driver's `Cargo.lock` is committed and built with `--locked`.
- The driver crate and all its dependencies were built once at image build. Only
  `/opt/rust/libdcp_huub.rlib`, `/opt/rust/deps/*.rlib` and the proc-macro `.so` files
  are kept. The Cargo registry and the target directory are removed, so no crate can be
  fetched or rebuilt.
- `g++` and `g++-12` are purged after the build. `libstdc++-12-dev` (12.2.0-14+deb12u1)
  stays, because rustc links each submission through `cc` against the libstdc++ that the
  static CaDiCaL objects need. Submissions cannot compile C++.
- The evaluator runs the container with no network, a read-only root file system, user
  65534, `HOME=/tmp`, a 512 MiB writable `/tmp` and `/input` read-only. Python 3.11.2 runs
  the runner.

For an ad hoc build, mount the file at `/input/model.rs` and run the runner's `rustc`
command (`RUSTC` in [run.py](run.py)) with the same flags:

```
docker run --rm --network none -v $PWD/model.rs:/input/model.rs:ro --entrypoint rustc \
  dcp-eval/huub_rust:v1 --edition 2021 -D unused_must_use /opt/rust/main.rs -o /tmp/c \
  --extern dcp_huub=/opt/rust/libdcp_huub.rlib -L dependency=/opt/rust/deps
```

## Traps

These are the failures found while building this integration. The first two are the
ones the harness is built around.

- **An ignored `Err` drops a constraint silently.** Every `post()` returns a `Result`. The
  build fails on any ignored one (`-D unused_must_use`), so write `post()?`. Do not write
  `let _ = ....post();` or `.ok()`; both defeat the check.
- **A 2-term equality can hang in `post()`**: two 2-term equalities over the same pair, and
  also a single `a + b == c` over distinct pairs (seen with domains of about 5000). A 2-term
  equality with a coefficient other than 1 (`y == 3*x`) exhausts memory on large domains.
  Post every 2-term equality as two inequalities with `eq2(m, expr, rhs)?` (it posts `le`
  and `ge`).
- **A `minimize` after any other solve returns a stale bound.** The harness solves first;
  a submission never calls the solver.
- **Maximising a loose objective climbs one value per step.** The runner does not add an
  objective brancher, so a maximisation can be slow where the minimisation is not.
- **Circuit is not a builtin.** Use `circuit(m, &next)?` (`next[i]` is the successor of node
  `i`, with domain `0..=n-1`, `n >= 2`); it is a decomposition with a visiting order.
- **Constructs Huub lacks:** no `count`, `regular`, `lex`, `inverse`, `nvalue`, `among`,
  `bin_packing` or `global_cardinality`. Count with `count_eq(&xs, v)` in a linear
  constraint. Write modulo as a decomposition: `k*q + r == x` with `0 <= r < k`.
- **Operators.** Write `x * 3`, not `3 * x`; a product of two views is `m.mul(x, y)`;
  `x % 3` does not compile; `x == y` on views posts nothing (use `m.linear(x - y).eq(0)`).
  `IntLinearExp::from` takes only `i64` and `View<i64>`; a `View<bool>` does not convert. Put
  a Boolean in a sum with `std::iter::once(b).sum::<IntLinearExp>()`, a weighted Boolean as
  `x.eq(v) * w`, or go through a 0/1 integer view (`let bi: View<i64> = b.into();`).
- **`reified_by(b)` is an equivalence** (`b` false enforces the negation); `implied_by(b)`
  is the one-way form. Using `reified_by` where only one direction is meant makes the model
  infeasible, with no error, at solve time.
- **`no_overlap` nests per object and needs fixed sizes.** `origins[i][d]` and `sizes[i][d]`:
  the outer `Vec` is the object, the inner `Vec` the dimension. `vec![xs, ys]` compiles and
  runs but constrains almost nothing (3 rectangles: 31 overlapping solutions of 33). With
  sizes that are decision variables, Huub 100.1.0 can report overlapping solutions (about 1
  in 10^4 to 10^5 on random 4-object instances), and `strict(false)` drops valid solutions
  that contain zero-size objects. Use `no_overlap` with fixed sizes and the default strict
  mode; with variable sizes (rotation) post the pairwise disjunction.
- **`define()` on linear, minimum, maximum, mul and pow gives the domain `i64::MIN..=i64::MAX`.**
  Create the variable yourself and use `.result(v)`.
- **`element` is 0-based.** For 1-based data, index with `i - 1`. `element` over a constant
  `Vec<bool>` ending in `true` accepts one index past the end; use `Vec<i64>` of 0/1.
- **Domains are `a..=b`**, not `0..10`. An empty domain (`5..=3`) panics.
- **`table` is positive only**, and its rows and `element`/`cumulative`/`disjunctive`
  arrays must be `i64`, not `i32`, with matching lengths; a mismatch panics.
- **`println!` corrupts the protocol.** Use `eprintln!` for logs.
- **`post()` after `lower()` is ignored.** Constraints go in `build`, before the harness
  lowers the model.

## Example

The pilot fixture [tests/fixtures/model_huub.rs](../../tests/fixtures/model_huub.rs)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```rust
fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.int("n");
    let x = m.new_int_decision(0..=n);
    let y = m.new_int_decision(0..=n);
    let mut out = Out::new();
    if inst.flag("optimize") {
        m.linear(x + y).ge(n).post()?;
        let total = m.new_int_decision(0..=2 * n);
        m.linear(x + y).eq(total).post()?;
        out.put("x", x).put("y", y);
        out.minimise(total);
    } else {
        m.linear(x + y).eq(n).post()?;
        out.put("x", x).put("y", y);
    }
    Ok(out)
}
```
