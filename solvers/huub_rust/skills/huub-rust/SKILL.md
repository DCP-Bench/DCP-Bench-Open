---
name: huub-rust
description: Huub, a constraint programming solver written in Rust (crate huub 100.1.0) that uses lazy clause generation, with integer and Boolean decision variables, linear, element, table, cumulative and disjunctive constraints, and proven optimisation. Use when writing, debugging or explaining a constraint or optimisation model in Rust with Huub, or when the user has chosen Huub.
license: Apache-2.0
compatibility: Requires Rust with cargo (tested with Rust 1.98.1), huub 100.1.0 from crates.io (MPL-2.0), and a C++ compiler (g++) on PATH, because huub builds the CaDiCaL SAT solver. Needs network access, or a vendored copy of the crates.
metadata:
  domain: constraint-programming
  solver: huub
  paradigm: cp
---

# Huub (Rust)

Huub is a constraint programming solver with lazy clause generation, written in Rust. You
create decision variables on a `Model`, post constraints with its builders, then lower the
model to a `Solver` and solve. Two rules matter most. **Every `post()` returns a `Result`**:
an ignored `Err` silently drops a constraint. **A `Bool` is a view, and so is an integer**:
a view can be a variable, a constant or a derived expression.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Runnable examples: `assets/`, one folder per pattern

## Install

Official: [crate page](https://crates.io/crates/huub), [API reference](https://docs.rs/huub/100.1.0/huub/), [repository](https://github.com/huub-solver/huub), [project site](https://huub.solutions).

```bash
cargo new my-model && cd my-model
cargo add huub@=100.1.0
cargo run --release           # first build; it compiles CaDiCaL with g++, takes about 40 s
```

| Requirement | Why |
|---|---|
| `g++` (or any C++ compiler that `cc` finds) | `pindakaas-cadical` compiles CaDiCaL with the `cc` crate. Without it the build fails in that crate's build script |
| Network to crates.io, or a vendored copy | `cargo add` and the first build download huub and its dependencies |

Pin the version exactly (`=100.1.0`): the examples were tested against it. Release builds are
much faster to search with, so use `--release` for anything that is timed.

## Quick start

Put this in `src/main.rs` of the project above. It finds `x` and `y` with `x + y = 7` and `x <= y`.

```rust
use huub::model::Model;
use huub::solver::{Solver, Valuation};

fn main() {
    let mut m = Model::default();
    let x = m.new_int_decision(0..=5);
    let y = m.new_int_decision(0..=5);
    m.linear(x + y).eq(7).post().unwrap();
    m.linear(x).le(y).post().unwrap();

    let (mut solver, map): (Solver, _) = m.lower().to_solver().unwrap();
    let outputs = vec![map.get(&mut solver, x), map.get(&mut solver, y)];
    solver
        .solve()
        .all_solutions(outputs.clone())
        .on_solution(|sol| println!("x = {}, y = {}", outputs[0].val(sol), outputs[1].val(sol)))
        .satisfy();
}
```

`unwrap` turns a conflict at post into a panic, which is fine for a script. In a function that
returns `Result`, propagate the error with `?` instead.

## Modelling

Crate API: [docs.rs](https://docs.rs/huub/100.1.0/huub/). Every constraint ends in `.post()?`,
or `.define()` when it returns a new view.

| Need | Call |
|---|---|
| integer in a range | `m.new_int_decision(0..=5)`, `m.new_int_decisions(n, 0..=5)`; Boolean: `m.new_bool_decision()` |
| linear `<=`, `<`, `==`, `!=`, `>=`, `>` | `m.linear(x * 3 - y * 2 + 5).le(z).post()?` (also `eq`, `ne`, `lt`, `ge`, `gt`) |
| constraint holds iff a Boolean | `.reified_by(b)`; one way only: `.implied_by(b)`; the indicator: `.reify()` gives a `View<bool>` |
| all different | `m.unique(xs.clone()).post()?` |
| allowed tuples (positive table only) | `m.table(vars).values(rows).post()?` |
| `array[index] == value`, 0-based | `m.element(array).index(i).result(r).post()?`, or `.define()` for a new view |
| `\|x\|`, `x / y`, `x * y`, `x^2` | `m.abs(x).define()`, `m.div(x, y).define()` (truncates), `m.mul(x, y).define()`, `m.pow(x, 2).define()` |
| min / max of variables | `m.minimum(xs).define()`, `m.maximum(xs).result(hi).post()?` |
| membership in a set | `m.contains(huub::Set::from_iter([1i64..=2, 7..=7])).member(x).define()` |
| tasks sharing a resource | `m.cumulative().start_times(s).durations(d).usages(u).capacity(c).post()?` |
| tasks on a unary resource | `m.disjunctive().start_times(s).durations(d).post()?` (durations are constants) |
| rectangles that do not overlap | `m.no_overlap().origins(o).sizes(z).post()?` (`origins` and `sizes` are `Vec<Vec<View>>`) |
| first occurrence order | `m.value_precede(xs).post()?` |
| Boolean formula | `m.proposition(BoolFormula::Atom(b) \| BoolFormula::Atom(d)).post()?` |
| sum of Booleans or counts | `m.linear(bs.iter().copied().sum::<IntLinearExp>()).eq(2).post()?`; a count of `x == v` is the same, with `x.eq(v)` in the sum |

Views of mixed kinds in one sum need `IntLinearExp::from(v)` or `b.into()`.

**Not available:** `circuit`, `subcircuit`, `regular`, `count`, `global_cardinality`, `lex`,
`inverse`, `nvalue`, `among`, `bin_packing`. Write them as decompositions. A count is a linear
sum of `x.eq(v)`. The circuit decomposition is in [circuit-decomposition](assets/circuit-decomposition/README.md),
and modulo is `k*q + r == x` with `0 <= r <= k-1`.

**Writing constraints.** Write `x * 3`, not `3 * x`. `x % 3` does not compile. `x == y` on two views
posts nothing: use `m.linear(x - y).eq(0)`.

Examples: [maximise-production](assets/maximise-production/README.md), [schedule-makespan](assets/schedule-makespan/README.md),
[element-table](assets/element-table/README.md), [infeasible-post](assets/infeasible-post/README.md).

## Solving

Lower the model once: `let (mut solver, map): (Solver, _) = m.lower().to_solver()?;`. Map each
`View` you need with `map.get(&mut solver, view)`. Adding constraints after lowering has no effect
on the solver.

**Optimisation.** `minimize(objective)` and `maximize(objective)` take an integer view and return
`(Status, Option<i64>)`. They must be the **first** solve on that solver: after another solve the
bound is stale and `minimize` can report a wrong value. See [schedule-makespan](assets/schedule-makespan/README.md).

| Call | Result | Meaning |
|---|---|---|
| `minimize` / `maximize` | `(Complete, Some(v))` | optimum `v`, proven |
| | `(Unsatisfiable, _)` | no solution |
| | `(Satisfied, Some(v))` | stopped with an incumbent `v`; not proven |
| | `(Unknown, _)` | stopped with nothing |
| `satisfy` after `all_solutions(views)` | `Complete` | every distinct solution over `views` was listed |
| | `Satisfied` | stopped early, with solutions |
| | `Unknown` | stopped early, with none |
| | `Unsatisfiable` | infeasible |

**Enumerating optimal solutions.** Prove the optimum first, pin it, then enumerate on a second
solve. `assuming(Some(pin))` takes an `Option`, and `None` means no pin.

```rust
let pin = objective.lit(&mut solver, IntLitMeaning::Eq(best));   // needs huub::actions::IntDecisionActions
let status = solver.solve().assuming(Some(pin)).all_solutions(outputs).on_solution(|_| rows += 1).satisfy();
```

Do not chain `minimize(..).all_solutions(..)`: it fires on improving solutions and panics when the
objective is constant. [all-optimal-solutions](assets/all-optimal-solutions/README.md) has the full program.

**Distinct solutions.** `all_solutions(views)` lists distinct assignments over `views`, so auxiliary
variables do not repeat a row. Views you do not list are not enumerated.

**Time limits.** Set a terminate callback. It is called about every ten conflicts, and the solver
stops within about a millisecond of the signal:

```rust
let deadline = std::time::Instant::now() + std::time::Duration::from_secs(10);
solver.set_terminate_callback(Some(move || {
    if std::time::Instant::now() >= deadline {
        huub::solver::TerminationSignal::Terminate
    } else {
        huub::solver::TerminationSignal::Continue
    }
}));
```

The solver does not check a count between solutions, so a callback can receive more solutions
than the count you set (a cap of 5 gave 8 in the spike). Count in the callback and drop the extras
when the number matters.

**Values.** `view.val(sol)` gives `i64` for an integer view and `bool` for a Boolean view
(`use huub::solver::Valuation;`). Integer domains are 64-bit.

## Common issues

| Symptom | Cause | Fix |
|---|---|---|
| A constraint has no effect; a solution violates it | `post()` returned `Err`, and the result was ignored | Write `post()?`, or `.unwrap()`. Never `let _ =` or `.ok()` on a `post()` |
| `post()` never returns on two 2-term equalities over the same pair | Huub hangs on that pattern | Post `le` and `ge` instead of `eq` for those constraints |
| Memory explodes with `y == 3*x` on large domains | A 2-term equality with a coefficient other than 1 | Post `le` and `ge` instead of `eq` |
| Optimum reported too low or high after another solve | `minimize` is not the first solve | Solve for the optimum on a fresh solver, first |
| `all_solutions` panics with a constant objective | Mixed `minimize` and `all_solutions` | Use `minimize`, then pin and enumerate separately |
| Maximisation climbs one value per step | A loose objective and the default search | Slow but correct. Tested on small cases: `IntBrancher::new_in(&mut s, vec![obj], DecisionSelection::InputOrder, DomainSelection::IndomainMax)` (in `huub::solver::branchers`) speeds it up. The effect on large models is not measured |
| Panic when lowering (`new_int_decision(5..=3)`) | An empty domain | Give a valid range, `lo..=hi` with `lo <= hi` |
| Panic on `element(vec![false, ...])` or a length mismatch in `table`, `cumulative` or `disjunctive` | Wrong element type or lengths | Use `i64` arrays of matching length |
| `element` accepts one index past the end | `element` over a constant `Vec<bool>` ending in `true` | Use a `Vec<i64>` of 0/1, or restrict the index domain |
| Wrong index by one | `element` is 0-based | Index with `i - 1` for 1-based data |
| `define()` returns a variable with the full `i64` range | `define` on `linear`, `minimum`, `maximum`, `mul` or `pow` | Create the variable yourself and pass it to `.result(v)` |
| Does not compile: `3 * x`, `x % 3`, `x * y` | Operator forms Huub does not provide | Write `x * 3`; decompose modulo; use `m.mul(x, y)` |
| `x == y` on views posts nothing | `==` on views is Rust equality | Use `m.linear(x - y).eq(0)` |
| Does not compile: sum of `View<i64>` and `View<bool>` | Mixed view kinds | `IntLinearExp::from(v)` or `b.into()` |
| `cannot find function circuit` | Huub has no circuit builder | Use the decomposition in [circuit-decomposition](assets/circuit-decomposition/README.md) |
| Off-by-one in a 1-based array | `element` is 0-based | Index `i - 1` |

## Further reading

- Crate and API reference: <https://docs.rs/huub/100.1.0/huub/>
- Project site and repository: <https://huub.solutions>, <https://github.com/huub-solver/huub>
- Runnable examples: `assets/`, each folder with `README.md`, `Cargo.toml` and `src/main.rs`

