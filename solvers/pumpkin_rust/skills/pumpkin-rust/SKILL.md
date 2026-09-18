---
name: pumpkin-rust
description: Write a DCP-Bench submission for the pumpkin_rust integration - one Rust file defining `build`, using the driver's Cp/Instance/Model surface over the Pumpkin lazy-clause-generation constraint solver. Use when generating or repairing a model for solver ID pumpkin_rust.
---

# Pumpkin (Rust) submissions

A submission is **one Rust file** that defines exactly one function:

```rust
fn build(inst: &Instance, cp: &mut Cp) -> Model
```

The image splices that file into a binary that already imports the driver
prelude, owns `main`, and speaks the evaluator's runner protocol. So the file
declares no crate, no `use` of the driver, no `main`, and never solves anything
itself. Build the model from `inst`, declare the outputs, return.

```rust
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let n = inst.size("n");
    let queens = cp.ints(n, 0, n as i32 - 1);
    cp.all_different(terms(&queens));
    for i in 0..n {
        for j in (i + 1)..n {
            let d = (j - i) as i32;
            cp.ne(vec![t(queens[i]), c(-1, queens[j])], d);
            cp.ne(vec![t(queens[i]), c(-1, queens[j])], -d);
        }
    }
    let mut m = Model::new();
    m.put("queens", queens);
    m
}
```

## Rules that break a submission

- **Never write to stdout.** The driver owns stdout for the JSONL protocol, so a
  single `println!` corrupts the run and the evaluator reports `invalid_output`.
  Log with `eprintln!`.
- **Never define `main`,** and never call `cp.solver.satisfy`/`optimise`
  yourself. The driver does that, with the evaluator's budget and solution limit.
- **Read every instance-dependent quantity from `inst`.** A model that types the
  example's numbers in is the one failure this whole benchmark exists to catch.
  A constant belonging to the *problem* rather than the instance may be mirrored,
  with a comment saying so.
- **Everything is `i32`.** Pumpkin's linear constraints take `i32` coefficients
  and right-hand sides. `inst.int` already fails loudly on a value that does not
  fit; keep intermediate products inside `i32` by bounding them yourself.
- Only one file is staged, so there are no helper modules. Write plain functions
  above or below `build` in the same file if it helps.

## Reading the instance

`inst` panics with the offending key and the value it found rather than
substituting a default, so a schema mismatch is loud.

| Call | Returns |
| --- | --- |
| `inst.int("n")` | `i32` scalar |
| `inst.size("n")` | the same scalar as `usize`, for lengths and loops |
| `inst.int_or("k", 0)` | scalar, or the fallback when the field is absent |
| `inst.flag("strict")` | `bool` scalar |
| `inst.ints("weights")` | `Vec<i32>` |
| `inst.flags("fixed")` | `Vec<bool>` |
| `inst.strings("names")` | `Vec<String>` |
| `inst.matrix("distance")` | `Vec<Vec<i32>>`, row-major, ragged allowed |
| `inst.cube("cost")` | `Vec<Vec<Vec<i32>>>` |
| `inst.len("weights")` | length of an array field |
| `inst.has("k")` | whether the field exists |
| `inst.get("k")` | the raw `serde_json::Value`, for anything irregular |

`python -m generation.brief PROBLEM` prints the field names and shapes this has
to match, plus the declared output names.

## Variables

| Call | Meaning |
| --- | --- |
| `cp.int(lo, hi)` | one integer variable on `[lo, hi]` |
| `cp.ints(n, lo, hi)` | `Vec<Var>` of length `n` |
| `cp.grid(rows, cols, lo, hi)` | `Vec<Vec<Var>>` |
| `cp.sparse(&[1, 3, 8])` | integer variable whose domain is exactly those values |
| `cp.bool()` / `cp.bools(n)` / `cp.bool_grid(r, c)` | Boolean variables (`Lit`) |
| `cp.constant(v)` | a variable fixed to `v`, where a constraint wants a variable |
| `cp.always()` / `cp.never()` | the constant true / false literal |
| `cp.lower_bound(x)` / `cp.upper_bound(x)` | current bounds, before search |

A `Lit` is a 0/1 integer variable, so it can go straight into a linear
constraint; `!lit` is its negation.

## Linear constraints

Pumpkin's linear constraints take a homogeneous list of `coefficient * variable`
summands and a **constant** right-hand side. Build the list with `t(x)` for
`1 * x`, `c(k, x)` for `k * x`, `terms(&xs)` for a whole slice at coefficient 1,
and `weighted(&ws, &xs)` to pair coefficients with variables.

```rust
cp.eq(vec![t(x), t(y)], 10);            // x + y == 10
cp.le(weighted(&costs, &picks), 100);   // sum(costs[i] * picks[i]) <= 100
cp.ne(vec![t(a), c(-1, b)], 3);         // a - b != 3
```

`eq`, `ne`, `le`, `lt`, `ge`, `gt` all take `(Vec<Term>, i32)`.

When the right-hand side is itself a variable, use the `sum_*` family, which
moves it across for you: `cp.sum_eq(terms(&xs), total)`, `cp.sum_le`,
`cp.sum_ge`. `cp.same(a, b)` and `cp.differ(a, b)` are the two-variable cases.

`cp.sum(terms(&xs))` returns a fresh variable equal to the sum, already bounded
from the summands' own bounds — the usual way to build an objective.

## Arithmetic and globals

| Call | Meaning |
| --- | --- |
| `cp.times(a, b, p)` | `a * b == p` |
| `cp.div(n, d, q)` | `n / d == q`, truncating toward zero; `d`'s domain must exclude 0 |
| `cp.abs(x, m)` | `\|x\| == m` |
| `cp.max(terms(&xs), m)` / `cp.min(terms(&xs), m)` | `max`/`min` of a list |
| `cp.all_different(terms(&xs))` | pairwise distinct |
| `cp.element(i, terms(&xs), v)` | `xs[i] == v`, **0-based** index |
| `cp.element_of(i, &constants, v)` | the same for a constant array |
| `cp.table(terms(&xs), rows)` | the assignment is one of `rows` |
| `cp.forbidden(terms(&xs), rows)` | the assignment is none of `rows` |
| `cp.cumulative(starts, &durations, &demands, capacity)` | resource usage never exceeds `capacity` |

`-7 / 2 == -3` and `element` being 0-based were both checked by running them,
not read off documentation.

## Booleans

| Call | Meaning |
| --- | --- |
| `cp.any(vec![a, b, c])` | at least one literal is true (a clause) |
| `cp.all(vec![a, b])` | every literal is true |
| `cp.at_most(&lits, k)` / `cp.at_least(&lits, k)` / `cp.exactly(&lits, k)` | cardinality |
| `cp.bool_le(&weights, &lits, rhs)` | `sum(weights[i] * lits[i]) <= rhs` |
| `cp.bool_sum_eq(&weights, &lits, target)` | the same sum equals a variable |

## Reification

`cp.is(x, v)` returns a fresh literal pinned to `x == v` in **both** directions,
which is what counting needs — a half-reified indicator is free to be false when
the condition holds, and quietly admits wrong solutions.

```rust
let hits: Vec<Lit> = xs.iter().map(|&x| cp.is(x, target)).collect();
let count = cp.int(0, xs.len() as i32);
cp.bool_sum_eq(&vec![1; hits.len()], &hits, count);
```

`iff_eq`, `iff_le`, `iff_ge` and `iff_is` pin a literal you already have.
`when_eq`, `when_le`, `when_ge` post only `flag -> constraint` and leave the
converse free; use those only when the converse genuinely does not matter.

## Outputs and the objective

```rust
let mut m = Model::new();
m.put("assignment", xs);          // Vec<Var>  -> JSON array
m.put("grid", rows);              // Vec<Vec<Var>> -> nested array
m.put("chosen", picks);           // Vec<Lit>  -> array of true/false
m.put("total", total);            // Var       -> integer
m.put("n", n as i32);             // a value the instance fixes
m.minimise(total);                // or m.maximise(total)
m
```

Names must be the ones `generation.brief` declares. `put` accepts `Var`, `Lit`,
`i32`, `bool`, and vectors or slices of those, nested to any depth.

**The objective must be a single variable**, so build it with `cp.sum(...)` or
constrain an auxiliary variable to the objective expression, then pass that.
Never bound the objective with a value taken from a known answer.

The driver reports success on an optimisation problem **only** when Pumpkin
proves the value optimal. A solution found but not proven optimal is reported as
a timeout rather than emitted, so a model that is merely slow shows up as
`execution_timeout`, never as a wrong answer.

## What Pumpkin does not have

These are absences to model around, not bugs:

- **No modulo constraint.** Decompose `a mod k == r` as `a == k*q + r` with
  `0 <= r < k`, using `cp.times` when `k` is itself a variable. Verified:
  `23 == 7*3 + 2`.
- **No `all_different` propagator.** Pumpkin decomposes it into pairwise
  disequalities, so it prunes no more than writing them out and costs O(n²)
  constraints. On a problem that leans on strong all-different propagation
  (large Latin squares, quasigroups), expect `execution_timeout` rather than a
  wrong answer.
- **No automaton, no regular, no 2-D no-overlap, no global cardinality, no
  circuit.** Encode with `table`, reified indicators, or `cumulative`.
- **No no-overlap constraint under that name.** `cp.cumulative(starts,
  &durations, &vec![1; n], 1)` is unary no-overlap.
- **No floats.** Scale a rational objective to integers and say so in a comment.

Anything else in the Pumpkin API is reachable directly: `cp.solver` is the real
`pumpkin_solver::Solver`, `cp.tag()` mints the constraint tag its constraint
functions require, and the crate is re-exported as
`dcp_pumpkin::pumpkin_solver`.

## Failure routing

| Evaluator result | Usual cause here |
| --- | --- |
| `compilation_error` | Rust type error. The full `rustc` diagnostic is in stderr; the commonest is mixing `Var` and `Lit` in one `vec![]` instead of widening both with `t(...)`. |
| `invalid_output` | The submission wrote to stdout, or declared an output the brief does not name. |
| `invalid_solution` | A constraint is missing or too weak — often a half-reified indicator that should have been `cp.is`. |
| `suboptimal_solution` | The objective direction is inverted, or the objective variable is not the quantity the reference optimises. |
| `execution_timeout` | The model is right but the encoding is too weak. Tighten variable bounds, add implied constraints, or record it as a performance limit. |
| `no_solution` | The model is overconstrained, or a `sparse`/bounded domain excludes the intended values. |

## Environment

Rust 1.98.1, `pumpkin-solver` 0.5.0, `serde_json` 1.0.151, pinned by a committed
`Cargo.lock`. Every Pumpkin crate is prebuilt into the image, so only the
submission compiles at evaluation time — typically under a second. The container
is networkless, read-only apart from a 512 MiB `/tmp`, single-CPU, and 2 GiB.

See [the driver's surface](references/driver-api.md) for the exact signature of
every call above and the types they accept.
