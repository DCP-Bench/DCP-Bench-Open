---
name: pumpkin-rust
description: Pumpkin, a constraint solver written in Rust (crate pumpkin-solver 0.5.0) with integer and Boolean variables, linear and global constraints, and proven optimisation. Use when writing, debugging or explaining a constraint or optimisation model in Rust with Pumpkin, or when the user has chosen Pumpkin.
license: Apache-2.0
compatibility: Requires Rust with cargo (tested with Rust 1.98.1), pumpkin-solver 0.5.0 from crates.io (MIT OR Apache-2.0), git on PATH while building, and network access or a vendored copy of the crates. Build with NO_CHECKERS=true.
metadata:
  domain: constraint-programming
  solver: pumpkin
  paradigm: cp
---

# Pumpkin (Rust)

Pumpkin is a constraint programming solver with lazy clause generation, written in Rust by ConSol Lab at TU Delft. You create variables on a `Solver`, post constraints built by Pumpkin's own constructors, then call `satisfy` or `optimise`. Keep one rule in mind: **a Boolean is a literal, not a variable**, and a linear constraint takes variables with explicit coefficients written as `scaled(k)`.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Runnable examples: `assets/`, one folder per pattern

## Install

Official: [crate page](https://crates.io/crates/pumpkin-solver), [repository](https://github.com/consol-lab/pumpkin), [API reference](https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/).

```bash
cargo new my-model && cd my-model
cargo add pumpkin-solver@=0.5.0
cargo add serde_json@=1.0.151     # only when the model reads an instance file
NO_CHECKERS=true cargo run        # first build; prints "Hello, world!"
```

| Requirement | Why |
|---|---|
| Network to crates.io, or a vendored copy (see [Offline builds](#offline-builds)) | `cargo add` and the first build download pumpkin-solver and its dependencies. Offline, they fail with `Could not resolve host: index.crates.io` |
| `git` on PATH while building | The build script runs `git rev-parse HEAD` and panics with `Failed to execute git command` if git is missing. Any git will do, even outside a repository: the build reads only its output |
| `NO_CHECKERS=true` | Without it the build script compiles proof checkers from a `tests/` directory the published crate does not ship, and fails with `No such file or directory` |

Pin the versions exactly (`=0.5.0`, `=1.0.151`): the examples were tested against them. Details: [crate docs](https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/).

**A model in its own file.** `cargo run` builds `src/main.rs`. A model kept elsewhere, such as `models/graph-colouring.rs`, needs a bin target that points at it; copying it over `src/main.rs` before each build also works, but the stale copy is easy to run by mistake:

```toml
[[bin]]
name = "model"
path = "models/graph-colouring.rs"
```

Then `NO_CHECKERS=true cargo run -- instance.json`. Verified with the file in `models/` and no `src/` directory.

### Offline builds

For a sandbox with no network (for example `docker run --network none`), fetch once on a machine with network access:

1. In the project, after the `cargo add` lines, run `cargo vendor vendor`. Cargo prints a `[source.crates-io]` block that replaces crates.io with the `vendor` directory.
2. Save that block as `.cargo/config.toml` in the project, or in a `CARGO_HOME` directory that the sandbox mounts.
3. Copy the project, `vendor/` and `Cargo.lock` into the sandbox and build with `NO_CHECKERS=true cargo run`.

Verified in a networkless container with an empty cargo registry: the vendored crates were mounted read-only, `CARGO_HOME` was set to a directory holding the replacement config, and git was on `PATH` (see the [Common issues](#common-issues) row on git).

## Quick start

Put this in `src/main.rs` of the project above. It finds `x` and `y` with `x + y = 7` and `x <= y`.

```rust
use std::time::Duration;

use pumpkin_solver::conflict_resolvers::resolvers::ResolutionResolver;
use pumpkin_solver::core::results::{ProblemSolution, SatisfactionResult};
use pumpkin_solver::core::termination::TimeBudget;
use pumpkin_solver::core::variables::TransformableVariable;
use pumpkin_solver::Solver;

fn main() {
    let mut solver = Solver::default();
    let x = solver.new_bounded_integer(0, 5);
    let y = solver.new_bounded_integer(0, 5);
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(vec![x.scaled(1), y.scaled(1)], 7, tag)).post();
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::less_than_or_equals(vec![x.scaled(1), y.scaled(-1)], 0, tag)).post();

    let mut brancher = solver.default_brancher();
    let mut resolver = ResolutionResolver::default();
    let mut termination = TimeBudget::starting_now(Duration::from_secs(10));
    let result = solver.satisfy(&mut brancher, &mut termination, &mut resolver);
    match result {
        SatisfactionResult::Satisfiable(found) => {
            let s = found.solution();
            println!("x = {}, y = {}", s.get_integer_value(x), s.get_integer_value(y));
        }
        SatisfactionResult::Unsatisfiable(..) => println!("no solution"),
        SatisfactionResult::Unknown(..) => println!("time limit reached"),
    }
}
```

## Modelling

Signatures: [references/pumpkin-api.md](references/pumpkin-api.md). Constructors: [crate API](https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/). Each constraint is posted as `solver.add_constraint(constructor(..., tag)).post()`.

| Need | API |
|---|---|
| integer in a range | [`new_bounded_integer(lo, hi)`](https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/core/struct.Solver.html) |
| integer with holes | `new_sparse_integer(vec![..])` |
| Boolean | `new_literal()`; constants `get_true_literal()`, `get_false_literal()` |
| sum `== k` | [`equals(terms, k, tag)`](https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/fn.equals.html) |
| `!=`, `<=`, `>=`, `<`, `>` | `not_equals`, `less_than_or_equals`, `greater_than_or_equals`, `less_than`, `greater_than`, same shape |
| `x + y == z` | `plus(x, y, z, tag)` |
| all different | [`all_different(vars, tag)`](https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/fn.all_different.html) |
| `array[index] == value`, index 0-based | `element(index, array, value, tag)` |
| allowed / forbidden tuples | `table(vars, rows, tag)` / `negative_table(vars, rows, tag)` |
| tasks sharing one resource | [`cumulative(starts, durations, demands, capacity, tag)`](https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/fn.cumulative.html) |
| `a * b == c` | `times(a, b, c, tag)` |
| `a / b == c`, truncates toward zero | `division(a, b, c, tag)` |
| absolute value `\|a\| == b` | `absolute(a, b, tag)` |
| maximum / minimum of variables | `maximum(vars, target, tag)` / `minimum(vars, target, tag)` |
| at least one literal true | `clause(lits, tag)` |
| every literal true | `conjunction(lits, tag)` |
| `sum(w[i] * lit[i]) <= k` | `boolean_less_than_or_equals(weights, lits, k, tag)` |
| `sum(w[i] * lit[i]) == var` | `boolean_equals(weights, lits, var, tag)` |
| constraint holds iff a flag is true | `add_constraint(c).reify(flag)` |
| flag implies the constraint (one way) | `add_constraint(c).implied_by(flag)` |

There is no modulo and no cardinality (count) constraint. Write `a == k*q + r` with `0 <= r < k` for modulo, and use `boolean_less_than_or_equals` with unit weights for "at most k of these literals".

**Terms.** `x.scaled(k)` and `x.offset(k)` need `use pumpkin_solver::core::variables::TransformableVariable;`. Where every coefficient is 1, a plain `Vec` of variables is accepted: `equals(vec![x, y], 3, tag)`.

**Literals.** A `Lit` is not a `Var`. In a linear constraint use `lit.get_integer_variable().scaled(k)`, so that literal and variable terms share one `vec!`; `!lit` negates. The `boolean_*` constraints take the literals directly.

**Zero coefficients.** `scaled(0)` on a plain variable panics at once with `Multiplication by zero is not invertable`. Scaling an already scaled view by 0 passes that check and fails later, during search, with `attempt to divide by zero`. Drop zero weights before building terms; if nothing is left, post over a constant instead of an empty list:

```rust
let terms: Vec<_> = w.iter().zip(&xs)
    .filter(|(&c, _)| c != 0)
    .map(|(&c, &v)| v.scaled(c))
    .collect();
```

**Tags.** A `ConstraintTag` names a constraint for Pumpkin's proof, and plays no part in solving. Use one tag for a group of constraints that say the same thing: [ConstraintTag](https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/core/proof/struct.ConstraintTag.html).

**Instance files.** Pumpkin does not read data. Parse the JSON with `serde_json` (see [Install](#install)); every value is a `serde_json::Value`, so convert with `as_i64()`, `as_array()` and so on:

```rust
fn read_instance() -> serde_json::Value {
    let path = std::env::args().nth(1).expect("usage: model <instance.json>");
    serde_json::from_str(&std::fs::read_to_string(path).expect("read instance")).expect("parse instance")
}

// in main:
let inst = read_instance();
let n = inst["n_nodes"].as_i64().expect("n_nodes") as usize;
let edges: Vec<(usize, usize)> = inst["edges"].as_array().expect("edges").iter()
    .map(|e| (e[0].as_i64().unwrap() as usize, e[1].as_i64().unwrap() as usize))
    .collect();
```

Print results with `serde_json::json!({ "colour": cols })` when the output must be JSON, so that the output is machine-readable.

**Counting distinct values (for example the number of colours).** Pumpkin has no count-distinct or cardinality constraint. Give each value a variable in `0..=n-1`, post `maximum(values, top, tag)`, and minimise `top` with `LinearSatUnsat`. Values start at 0, so the count is `optimum + 1`. See [minimise-colours](assets/minimise-colours/README.md).

## Solving

Objective: a single variable, given to `optimise` with [`LinearSatUnsat`](https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/core/optimisation/linear_sat_unsat/struct.LinearSatUnsat.html). Every call needs a brancher, a resolver and a time budget:

```rust
let mut brancher = solver.default_brancher();
let mut resolver = ResolutionResolver::default();   // pumpkin_solver::conflict_resolvers::resolvers
let mut termination = TimeBudget::starting_now(Duration::from_secs(10));
```

| Call | Result | Meaning |
|---|---|---|
| `satisfy` | `Satisfiable(found)` | `found.solution()` holds the values |
| | `Unsatisfiable(..)` | Proven: no solution (or none left, when enumerating) |
| | `Unknown(..)` | Time budget ran out; nothing proven |
| `optimise` | `Optimal(solution)` | Proven optimal; the only result to report as the optimum |
| | `Satisfiable(_)`, `Stopped(_, _)` | A solution was found but optimality is not proven |
| | `Unsatisfiable`, `Unknown` | As for `satisfy` |

[SatisfactionResult](https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/core/results/enum.SatisfactionResult.html) and [OptimisationResult](https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/core/results/enum.OptimisationResult.html).

Read values with `solution.get_integer_value(v)` (`use pumpkin_solver::core::results::ProblemSolution;`). It works for a literal too, giving `1` or `0`. Compile errors and panics both go to stderr, and a panic ends the process with a non-zero exit code. Check answers in your own program.

**Time budget.** Every example uses `TimeBudget::starting_now(Duration::from_secs(10))`. The job-shop instance ft06 (optimum 55, 6 jobs by 6 machines) solved in under 2 seconds of wall time with a release build. For a larger instance, a result of `Unknown` or `Stopped` means the budget ran out: raise the `Duration` (for example `from_secs(60)`) and report only `Optimal`. Do not report a value from a run that was cut off.

Examples: [satisfy-colouring](assets/satisfy-colouring/README.md), [maximise-production](assets/maximise-production/README.md), [minimise-partition](assets/minimise-partition/README.md), [minimise-colours](assets/minimise-colours/README.md), [infeasible-sums](assets/infeasible-sums/README.md), [scheduling-makespan](assets/scheduling-makespan/README.md).

## All solutions

Enumerate by solving again after each solution, with a clause that rules out the values just printed. Block only the variables you print: a clause over auxiliary variables lets the same printed answer appear twice.

```rust
let blocking: Vec<Predicate> = match solver.satisfy(&mut brancher, &mut termination, &mut resolver) {
    SatisfactionResult::Satisfiable(found) => {
        let solution = found.solution();
        let value = solution.get_integer_value(x);
        println!("x = {value}");
        vec![x.disequality_predicate(value)]
    }
    SatisfactionResult::Unsatisfiable(..) => break,   // every solution has been listed
    SatisfactionResult::Unknown(..) => break,         // time limit: the list may be incomplete
};
let tag = solver.new_constraint_tag();
solver.add_clause(blocking, tag);
```

A literal is blocked with `get_true_predicate()` or `get_false_predicate()`, whichever it is not. `disequality_predicate` needs `use pumpkin_solver::core::predicates::{Predicate, PredicateConstructor};`.

**All optimal solutions.** Run `optimise` first, then post `equals(vec![objective.scaled(1)], best, tag)`, and enumerate as above. See [all-optimal-solutions](assets/all-optimal-solutions/README.md) and [all-solutions](assets/all-solutions/README.md).

## Common issues

| Symptom | Cause | Fix |
|---|---|---|
| `no method named 'scaled' found for struct 'DomainId'` | `TransformableVariable` not imported | `use pumpkin_solver::core::variables::TransformableVariable;` |
| `no method named 'disequality_predicate'` | `PredicateConstructor` not imported | Import it from `pumpkin_solver::core::predicates` |
| `resolver does not live long enough` or `cannot borrow solver as mutable more than once` | The result of `satisfy` borrows the solver and resolver, and a `match` at the end of `main` keeps the borrow | Bind the result first: `let result = solver.satisfy(..); match result { .. }`; add clauses after the match |
| `Failed to execute git command` while building | git is not on PATH (slim container images often lack it) | Install git on the machine or in the container. Any git works, even outside a repository; a stub that exits 0 with no output also built in verification (the build then sets an empty `GIT_SHA`), but do not rely on a stub outside tests |
| `Could not resolve host: index.crates.io` | No network and no vendored crates | Build from vendored crates, see [Offline builds](#offline-builds) |
| `No such file or directory` while building | Checkers missing from the published crate | `NO_CHECKERS=true cargo build` |
| `cargo run` runs old code, or changes to the model have no effect | The model is in `models/` but `src/main.rs` is what gets built | Add a `[[bin]]` with `path` pointing at the model, see [Install](#install) |
| Unresolved `serde_json` when reading the instance | The JSON dependency was not added | `cargo add serde_json@=1.0.151` |
| `Unknown` or `Stopped` on a larger instance | Time budget ran out | Raise `TimeBudget::starting_now(Duration::..)`, see [Solving](#solving) |
| Colour count one too high | Colours start at 0, so the count is the optimum of the largest colour plus 1 | Report `optimum + 1`; see [Modelling](#modelling) |
| `Multiplication by zero is not invertable` | `scaled(0)` on a variable with zero weight | Filter zero coefficients, see [Modelling](#modelling) |
| `attempt to divide by zero` during search | A view already scaled, then scaled by 0 | As above: never let a coefficient reach 0 |
| Array index off by one | `element` is 0-based | Index from 0; check against the array length |
| Negative quotient one too high | `division` truncates toward zero: `-7 / 2 == -3` | For floor division, use `a == k*q + r` with `0 <= r < k` |
| Same printed answer twice | Blocking clause includes auxiliary variables | Block only the printed variables |
| Indicator is free when the constraint holds | `implied_by` is one-way | Use `.reify(flag)` for both directions |
| `expected AffineView<Literal>, found AffineView<DomainId>` | `lit.scaled(k)` gives a view of the literal, which cannot share a `vec!` with variable terms | Use `lit.get_integer_variable().scaled(k)` for every term |
| `optimise` returns `Satisfiable` or `Stopped` | Optimality not proven within the time budget | Report only `Optimal`; raise the time budget or simplify the model |

## Further reading

- Crate and API reference: <https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/>
- Repository and changelog: <https://github.com/consol-lab/pumpkin>
- Runnable examples: `assets/`, each folder with `README.md`, `Cargo.toml` and `src/main.rs`
