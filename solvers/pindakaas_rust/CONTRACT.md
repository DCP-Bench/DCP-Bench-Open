# pindakaas_rust: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how Pindakaas in
Rust expresses it. Runner: [run.py](run.py), which compiles [rust/main.rs](rust/main.rs)
with the submission spliced in and runs the binary. The harness is the `dcp_pindakaas`
library, [rust/driver/src/lib.rs](rust/driver/src/lib.rs): it defines `Instance`, `Out`,
the helpers that encode what Pindakaas lacks, and `run`, which owns solving, enumeration
and printing.

**This integration is for satisfaction problems only.** Pindakaas 0.6.0 has no optimiser
and the harness adds none: `Out` has no `minimise` or `maximise`. Do not write a model for
a problem whose brief declares an objective.

## Submission file

One Rust file, `model.rs`. `main.rs` is

```rust
use dcp_pindakaas::prelude::*;
include!("/input/model.rs");
fn main() { dcp_pindakaas::run(build); }
```

so the file is a list of items (functions, structs, consts, `use` declarations) in the
root of a binary crate that has already glob-imported the prelude. The prelude gives:
`Instance`, `Out`, `Node`, `IntoNode`, `Res`, `Cadical`, `IntVar`, `Lit`, `BoolVal`,
`LinExp`, `Linear`, `Comparator`, `LinearEncoder`, `StaticLinEncoder`, `Formula`,
`TseitinEncoder`, `Unsatisfiable`, the traits `ClauseDatabase` and `ClauseDatabaseTools`,
the harness helpers listed under Helpers, the `pindakaas` crate itself, and `serde_json`'s
`Value` and `json!`. Anything else comes from `std` or from `dcp_pindakaas::pindakaas::...`;
no other crate is linked. Do not define `fn main`, do not write `#![...]` crate attributes
or `//!` doc comments, and do not use `extern crate`.

## Entrypoint

```rust
fn build(inst: &Instance, s: &mut Cadical) -> Res<Out>
```

`s` is a CaDiCaL solver, passed in empty: it is the clause database. Create literals and
integer variables, encode constraints into it, and return the declared outputs in an
`Out`. `run` calls `build` once, then solves. `Res<T>` is `Result<T, Unsatisfiable>`:
every encoding call returns a `Result`, and the submission propagates it with `?`.

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
out.put("x", &x).put("flags", &flags).put("k", 42i64);
Ok(out)
```

`put` takes an `IntVar` or `&IntVar` (an integer), a `Lit` or a `BoolVal` (a Boolean), an
`i64` or `bool` constant, or a `Vec`, `&[T]` or `&Vec<T>` of these, which gives nested
arrays. A repeated name panics. The harness does not compare names with the brief: a
missing or extra name is rejected by the evaluator. An `Out` with no outputs is an `error`.
Constants are reported verbatim. Leaves are integers and Booleans only: a Boolean is
written `true`/`false`. Integer outputs carry the full 64-bit range, but see the trap on
wide integer variables: a constant such as `30000000002i64` is fine, a variable with that
domain is not.

Before solving, the harness gives every integer output a view (an equality literal for its
minimum), because `IntVar::value` of a variable that has none returns the domain minimum
whatever the model says.

## Objective

None. This integration declares no objective: a satisfaction problem declares none, and an
optimisation problem is out of scope.

## Solving

The runner forces:

- Pindakaas's default encoders for `post` and the helpers, and CaDiCaL's default options.
  Search is CaDiCaL's; the submission cannot change it.
- One `solve()` per solution. After each solution the harness adds a blocking clause over
  the declared output leaves (constants carry no information and are left out; an integer
  of a single value is left out too), so solutions are distinct on the declared outputs
  and auxiliary variables do not repeat a row. Each solution is printed as it is found.
- The runner stops after `solution_limit` rows. Status: `limit` when the cap was reached,
  `complete` when the search space is exhausted after at least one row, `unsat` when there
  is no solution at all, `timeout` when the budget ended the search.
- An `Err(Unsatisfiable)` from `build` or from encoding the outputs is infeasibility:
  status `unsat`.
- Time budget: one terminate callback, set to `execution_timeout` from the start of the
  binary. It stops the search in about a millisecond, but **encoding does not poll it**: one
  big cardinality or integer encoding can run for seconds past the deadline. The runner
  kills a binary still running 15 s after the budget and reports `timeout`; a nonzero exit
  (a panic) is `error`.

## Compilation

Yes. One `rustc --edition 2021 -C opt-level=2 -C codegen-units=1 -D unused_must_use`
invocation on `main.rs`, linked against the prebuilt `libdcp_pindakaas.rlib` and its
dependencies (no Cargo, no network). `-D unused_must_use` turns an ignored `Result`, and so
an ignored encoding call, into a compile error. Budget: `compilation_timeout` (default
120 s); a failure or overrun is `compilation_error` with rustc's output on stderr. Warnings
go to stderr and do not fail the build. Compiling takes 5 to 20 s.

## Helpers

Pindakaas has literals, clauses, propositional formulas, and linear, pseudo-Boolean,
cardinality and count constraints over literals and integer variables. It has no
all-different, element, table, min/max, multiplication, modulo or reification. The prelude
supplies tested decompositions of these, in the form the standalone skill teaches; each
takes the solver first and returns `Res`:

| Helper | Effect |
| --- | --- |
| `post(s, expr, cmp, k)` | `expr <cmp> k`; panics when coefficients times ranges reach 2^62 |
| `define(s, expr) -> IntVar` | a fresh `z == expr`, domain = bounds of `expr`; `expr` has no constant |
| `post_if(s, &conds, expr, cmp, k)` | `conds -> expr <cmp> k`, in the safe form (see Traps) |
| `reify_le(s, expr, k) -> Lit` / `reify_eq(s, expr, k) -> Lit` | `b <-> expr <= k` / `b <-> expr == k` |
| `lit_of(s, boolval) -> Lit` | a literal for a literal-or-constant `BoolVal` |
| `all_different(s, &xs)` | at most one variable per value |
| `count_eq(s, &xs, v, &c)` | `c == #{i : xs[i] == v}` |
| `element_const(s, &idx, &arr, &r)` / `element_var(s, &idx, &xs, &r)` | `r == arr[idx]` / `r == xs[idx]`, 0-based |
| `table(s, &xs, &rows)` | `xs` is one of the rows |
| `minimum(s, &xs, &m)` / `maximum(s, &xs, &m)` | `m == min(xs)` / `m == max(xs)` |
| `times(s, &x, &y, &z)` | `z == x * y`, cases on `x`'s values (small domain) |
| `mod_const(s, &x, k, &r)` | `r == x mod k`, `x >= 0`, `k > 0` constant |
| `abs_eq(s, &x, &a)` | `a == |x|` |
| `iv(&x)`, `bx(boolval)`, `scaled(&x, c)` | integer variable, `BoolVal` or `c * x` as a `LinExp` term |

## Traps

These are the failures found while building this integration. The first three give silent
wrong answers.

- **`encode_implied` over integer terms narrows the variables for good.** `b -> x + y <= 4`
  with `b` false still removes values from `x` and `y` (25 of 36 pairs survive). Use
  `post_if`, which defines the sum as a variable and puts only that variable's order
  literals behind the conditions. `encode_implied` is safe only over a sum of literals.
  An implication through `encode_implied` also makes `value()` disagree with the literals,
  so blocking clauses stop blocking and enumeration repeats forever.
- **`i64` overflow is silent.** `2^61 * x + 2^61 * y <= 2^62` over `0..4` accepts every pair.
  `post` panics when the sum of `|coefficient| * max|variable|` plus `|k|` reaches 2^62; a
  constraint posted with `s.encode(&Linear::new(..), &enc)` directly has no such guard.
- **An integer variable belongs to the first solver that encodes it.** Reusing one in a
  second solver gives wrong answers. There is one solver here; do not create another.
- **An ignored `Err` can drop a constraint.** The build fails on any ignored `Result`
  (`-D unused_must_use`), so write `?`. Do not write `let _ = ...;` or `.ok()` on an
  encoding call.
- **Domains are `IntVar::new(a..=b)`.** An empty range (`5..=3`) panics, later. A zero
  coefficient on an integer term panics ("attempt to divide by zero"); use `scaled`, or
  leave the term out. Coefficients on literals may be zero.
- **Big domains are expensive.** An integer variable has order and equality views that grow
  with its domain: `3x + 7y = 10^7` on domains of that size needs millions of variables,
  and `10^9` aborts the process with a C++ `bad_alloc` (status `error`). Keep domains small,
  derive tight bounds from the instance, and keep `x.at_least(..)`, `at_most` and `equals` off
  wide variables.
- **Encoding ignores the time budget.** A cardinality or pseudo-Boolean constraint with
  large coefficients (a Totalizer over weights of about 10^6) can take seconds to encode
  and does not stop at the deadline.
- **Operators.** Write `x.clone() * 3`, not `3 * x` (`3 * lit` is fine); there is no `Sum`
  for `LinExp`, so accumulate with `+=`. `LinExp`'s constant term and its value are private:
  keep constants on the right-hand side `k`, or define a variable. `x.equals(s, v)` cannot be
  called while a `sol` borrow of the solver lives (the harness reads values first).
- **No global constraint.** Use the helpers above, or write clauses over equality and order
  literals. Circuit, cumulative, regular, lex and inverse are not helpers: decompose them.
- **`println!` corrupts the protocol.** Use `eprintln!` for logs.
- **Constraints go in `build`.** The solver is solved only after `build` returns.

## Example

The pilot fixture [tests/fixtures/model_pindakaas.rs](../../tests/fixtures/model_pindakaas.rs)
(instance fields `n`, `optimize`; outputs `x`, `y`; satisfaction instances only):

```rust
fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.int("n");
    let x = IntVar::new(0..=n);
    let y = IntVar::new(0..=n);
    post(s, iv(&x) + iv(&y), Comparator::Equal, n)?;
    let mut out = Out::new();
    out.put("x", &x).put("y", &y);
    Ok(out)
}
```

## Environment

Image `dcp-eval/pindakaas_rust:v1`, built from `rust:1.98.1-slim-bookworm` pinned by digest:

- Rust 1.98.1 (`rustc` and `cargo` on `PATH`); `pindakaas` 0.6.0 with its default features
  plus `cadical` (CaDiCaL is compiled from the vendored source at image build), and
  `serde_json` 1.0.151. The driver's `Cargo.lock` is committed and built with `--locked`.
- The driver crate and all its dependencies were built once at image build. Only
  `/opt/rust/libdcp_pindakaas.rlib` and `/opt/rust/deps/*.rlib` are kept. The Cargo registry
  and the target directory are removed, so no crate can be fetched or rebuilt.
- `g++` is purged after the build. `libstdc++-12-dev` stays, because rustc links each
  submission through `cc` against the libstdc++ that the static CaDiCaL objects need.
  Submissions cannot compile C++.
- The evaluator runs the container with no network, a read-only root file system, user
  65534, `HOME=/tmp`, a 512 MiB writable `/tmp` and `/input` read-only. Python 3.11.2 runs
  the runner.

For an ad hoc build, mount the file at `/input/model.rs` and run the runner's `rustc`
command (`RUSTC` in [run.py](run.py)) with the same flags:

```
docker run --rm --network none -v $PWD/model.rs:/input/model.rs:ro --entrypoint rustc \
  dcp-eval/pindakaas_rust:v1 --edition 2021 -D unused_must_use /opt/rust/main.rs -o /tmp/c \
  --extern dcp_pindakaas=/opt/rust/libdcp_pindakaas.rlib -L dependency=/opt/rust/deps
```
