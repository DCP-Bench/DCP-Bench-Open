---
name: pindakaas-rust
description: Pindakaas, a Rust library that encodes Boolean and integer constraints (clauses, propositional formulas, linear, pseudo-Boolean and cardinality constraints, integer variables) into CNF and solves them with the bundled CaDiCaL SAT solver (crate pindakaas 0.6.0). Use when writing, debugging or explaining a SAT or pseudo-Boolean model in Rust with Pindakaas, when a constraint has to be hand-encoded to clauses, or when the user has chosen Pindakaas.
license: Apache-2.0
compatibility: Requires Rust with cargo (tested with Rust 1.98.1), pindakaas 0.6.0 from crates.io (MPL-2.0), and a C++ compiler (g++) on PATH, because the crate builds the CaDiCaL SAT solver. Needs network access, or a vendored copy of the crates.
metadata:
  domain: sat
  solver: cadical
  paradigm: sat
---

# Pindakaas (Rust)

Pindakaas is a library of CNF encodings with a SAT solver attached. You create literals and
integer variables on a solver, encode constraints into it, and solve. It has **no optimiser,
no enumeration and no global constraints** (no all-different, element, table, min/max,
multiplication, reification): those are clauses and linear constraints that you write. Three
rules matter most. **Every encoding call returns a `Result`**: propagate it with `?`.
**`encode_implied` over integer terms narrows the variables for good** and gives wrong
answers: use the safe form below. **An integer variable has to have a view before you read
it** or `value()` returns the domain minimum.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Runnable examples: `assets/`, one folder per pattern

## Install

Official: [crate page](https://crates.io/crates/pindakaas), [API reference](https://docs.rs/pindakaas/0.6.0/pindakaas/), [repository](https://github.com/pindakaashq/pindakaas).

```bash
cargo new my-model && cd my-model
cargo add pindakaas@=0.6.0
cargo run --release           # first build; it compiles CaDiCaL with g++, takes about 30 s
```

| Requirement | Why |
|---|---|
| `g++` (or any C++ compiler that `cc` finds) | the crate compiles CaDiCaL with the `cc` crate; without it the build fails in a build script |
| Network to crates.io, or a vendored copy | `cargo add` and the first build download pindakaas and its dependencies |

Pin the version exactly (`=0.6.0`): the integer layer is new in 0.6 and the examples were
tested against it. Use `--release` for anything that is timed. The default features give
CaDiCaL; the `kissat` feature exists but Kissat cannot take a clause after a solve, so it
cannot enumerate.

## Quick start

`src/main.rs`: find `x` and `y` with `x + y = 7` and `x <= y` over `0..=5`, all solutions.

```rust
use pindakaas::constraint::linear::{Comparator, LinExp, Linear, LinearEncoder, StaticLinEncoder};
use pindakaas::decision::integer::IntVar;
use pindakaas::solver::cadical::Cadical;
use pindakaas::solver::{SolveResult, Solver};
use pindakaas::{ClauseDatabase, ClauseDatabaseTools, Unsatisfiable, Valuation};

fn main() -> Result<(), Unsatisfiable> {
    let mut s = Cadical::default();
    let enc = LinearEncoder::<StaticLinEncoder>::default();
    let x = IntVar::new(0..=5);
    let y = IntVar::new(0..=5);
    s.encode(&Linear::new(LinExp::from(x.clone()) + LinExp::from(y.clone()), Comparator::Equal, 7), &enc)?;
    s.encode(&Linear::new(LinExp::from(x.clone()) - LinExp::from(y.clone()), Comparator::LessEq, 0), &enc)?;
    let _ = x.equals(&mut s, 0)?; // a view, so that value() reads the model
    let _ = y.equals(&mut s, 0)?;
    loop {
        let (xv, yv) = match s.solve() {
            SolveResult::Satisfied(sol) => (x.value(&sol), y.value(&sol)),
            _ => break,
        };
        println!("x = {xv}, y = {yv}");
        let (bx, by) = (x.equals(&mut s, xv)?, y.equals(&mut s, yv)?);
        s.add_clause([!bx, !by])?; // block this solution
    }
    Ok(())
}
```

`s.encode(&constraint, &encoder)` is the generic entry point. An `Err(Unsatisfiable)` means
the clause database already holds a contradiction. Read values before touching the solver
again: the solution borrows it.

## Modelling

Imports: the quick start's, plus `pindakaas::constraint::propositional_logic::{Formula,
TseitinEncoder}`, `pindakaas::{BoolVal, Lit}` and `pindakaas::solver::{Assumptions,
TermSignal, TerminateCallback}` as needed. `Assumptions` is the trait for `solve_assuming`,
`TerminateCallback` the one for `set_terminate_callback`. API: [docs.rs](https://docs.rs/pindakaas/0.6.0/pindakaas/).

| Need | Write |
|---|---|
| Boolean variable | `let b: Lit = s.new_lit();` and `let (a, b, c) = s.new_lits();` |
| Clause | `s.add_clause([a, !b, c])?;` (an empty clause returns `Err`) |
| Boolean formula | `s.encode(&((a ^ b) \| c), &TseitinEncoder)?;` |
| Integer variable | `IntVar::new(lo..=hi)`; holes through `RangeList::from_iter` |
| Linear constraint | `s.encode(&Linear::new(x.clone() * 3 - y.clone() * 2 + z.clone(), Comparator::LessEq, 4), &enc)?;` |
| Cardinality, pseudo-Boolean | the same `Linear` over `Lit` terms: `LinExp::from(l)`, `lit * 5`; accumulate with `+=` |
| Order and equality literals | `x.at_least(&mut s, 3)?`, `x.at_most(&mut s, 3)?`, `x.equals(&mut s, 5)?`: each gives a `BoolVal` (a `Lit` or a constant) |
| All-different | per value, at most one variable equals it: a `Linear` over `x_i.equals(v)` literals, `<= 1` |
| Count | `sum of x_i.equals(v) literals - c == 0` |
| Element, constant array | `idx` in `0..len`, and for each `j`: clause `[!idx.equals(j), r.equals(a_j)]` |
| Element, variables | for each `j`: `idx == j` implies `x_j - r == 0` (safe implication, below) |
| Table | one selector literal per row, exactly one true, each implies `x_k == row_k` |
| Minimum / maximum | `m <= x_i` for all `i`, and for each value `v` a clause `[m >= v, !(x_1 >= v), ...]` |
| Multiplication, small factor | for each value `a` of `x`: `x == a` implies `a*y - z == 0` |
| Modulo by a constant `k` | `x = q*k + r` with `0 <= r < k` and `q` an integer variable |
| Absolute value | split on `x <= -1` with a literal and two safe implications |

A `BoolVal` is a literal or a constant: match it, or turn a constant into a fixed literal.
`!bv` negates either kind. Write `x.clone() * 3`, not `3 * x` (`3 * lit` works). There is no
`Sum` for `LinExp`: start from `LinExp::default()` and use `+=`. A `LinExp` constant and its
value are private, so keep constants on the right-hand side of `Linear::new`.

### Implication and reification over integers

`s.encode_implied(&conds, &linear, &enc)` is correct only when the sum is over literals.
Over integer terms it narrows the variables permanently: `b -> x + y <= 4` with `b` false
still removes values (25 of 36 pairs survive), and `value()` then disagrees with the
literals so that blocking clauses stop blocking. The safe form defines the expression as a
fresh variable and puts only that variable's literals behind the conditions:

```rust
fn define(s: &mut Cadical, e: LinExp) -> Result<IntVar, Unsatisfiable> {
    let mut n = LinExp::default();
    n += e; // folds the outer multiplier into the terms
    let (mut lo, mut hi) = (0i64, 0i64);
    for (x, c) in n.int_terms() {
        let (a, b) = (c * x.min(), c * x.max());
        lo += a.min(b);
        hi += a.max(b);
    }
    for (_, c) in n.bool_terms() {
        lo += c.min(0);
        hi += c.max(0);
    }
    let z = IntVar::new(lo..=hi);
    s.encode(&Linear::new(n - LinExp::from(z.clone()), Comparator::Equal, 0), &LinearEncoder::<StaticLinEncoder>::default())?;
    Ok(z)
}
// conds -> e <= k:  clause [!c1, !c2, ..., z.at_most(k)]       with z = define(e)
// b <-> e <= k:     b = z.at_most(k)                            (the literal itself)
// b <-> e == k:     b = z.equals(k)
```

`define` needs an expression with no constant term. The examples in `assets/` carry this and
the other helpers as tested code; `assets/conditional-constraints` shows all 51 solutions of
`b -> x + y <= 4` surviving.

## Solving

- **Solve:** `s.solve()` returns `SolveResult::Satisfied(sol)`, `Unsatisfiable(_)` or
  `Unknown` (the search was interrupted). `x.value(&sol)` gives an integer, `sol.value(lit)`
  a Boolean.
- **Enumerate:** after each solution add a blocking clause over the variables you care
  about: `[!x.equals(v), !y.equals(w), ...]`, a literal flipped for each Boolean. Stop
  when `add_clause` returns `Err` (that was the last solution) or `solve()` is
  `Unsatisfiable`. Projecting on a subset of variables gives distinct rows on that subset.
- **Optimise:** there is no optimiser. Define the objective as an integer variable and
  search linearly with an assumption: `solve_assuming(vec![bound])` where `bound` is
  `obj.at_most(&mut s, best - 1)?` (for a minimum), until `Unsatisfiable` or the bound is
  `BoolVal::Const(false)` (no better value in the domain). `assets/` has no optimisation
  example; the loop is ten lines.
- **Deadline:** `s.set_terminate_callback(Some(move || if Instant::now() >= deadline {
  TermSignal::Terminate } else { TermSignal::Continue }))` stops the search in about a
  millisecond, and `solve()` then returns `Unknown`. The closure must be `Send`, so share
  a flag through an `Arc<AtomicBool>`. **Encoding is not interruptible**: one large
  cardinality or pseudo-Boolean encoding can run for seconds past any deadline.
- **Reading values:** give every integer you will read at least one view
  (`let _ = x.equals(&mut s, x.min())?;`) before the first solve.
- **Encoders:** `StaticLinEncoder` picks MixedRadix for integer sums, Totalizer for
  pseudo-Boolean, cardinality and count constraints, and Product for at-most-one. Others
  (`AdderEncoder`, `DecisionDiagramEncoder`, sorting networks, `SequentialCounter`) exist;
  on one weighted knapsack the decision diagram solved in 0.75 s where the default
  Totalizer timed out, so try another when a weighted constraint is the bottleneck.

## Common issues

| Symptom | Cause and fix |
|---|---|
| Wrong answers or lost solutions behind a condition | `encode_implied` over integer terms narrows the variables; use `define` and put the condition on the variable's literals |
| `value()` returns the minimum of the domain | the variable has no view; call `x.equals(&mut s, x.min())?` before solving |
| Constraints silently accept everything | an `i64` overflow in the encoder: `sum |c| * max|x|` must stay under 2^62; check it before posting |
| Panic "attempt to divide by zero" | a zero coefficient on an integer term; leave the term out |
| Panic on `IntVar::new(5..=3)` or on `CardinalityOne` with `a` and `!a` | an empty domain or a trivially contradictory call; guard it |
| Wrong answers after reusing a variable in a second solver | an integer variable belongs to the first solver that encodes it; rebuild fresh variables for a new solver |
| Out of memory or a C++ `bad_alloc` abort | a wide domain: order and equality views grow with the domain (`3x + 7y = 10^7` needs millions of variables, `10^9` aborts). Keep domains small, derive tight bounds from the data, avoid `at_least`, `at_most` and `equals` on wide variables |
| An encoding runs past the deadline | encoding does not poll the terminate callback; keep weights and domains small |
| Compile error on `3 * x`, on `sum()`, or "borrowed" on `x.equals(..)` | write `x.clone() * 3`, accumulate with `+=`, and read `sol` values into plain integers before calling the solver again |
| `no method solve_assuming` or `set_terminate_callback` | import the traits `Assumptions` and `TerminateCallback` |
| `LinearEncoder::default()` "type annotations needed" | write `LinearEncoder::<StaticLinEncoder>::default()` or give the binding a type |
| Process aborts with "Coverage goal" using Kissat | Kissat is not incremental: a clause added after a solve aborts the process; use CaDiCaL |
| An ignored `Err` | write `?` on every encoding call; a compiler flag `-D unused_must_use` turns an ignored one into an error |

## Further reading

- API reference: <https://docs.rs/pindakaas/0.6.0/pindakaas/>
- Repository and changelog: <https://github.com/pindakaashq/pindakaas>
- Examples in `assets/`: `queens-enumeration`, `conditional-constraints`, `element-table-minmax`,
  `magic-square`, `infeasible-and-deadline`. Each is a cargo project that checks its own results.
