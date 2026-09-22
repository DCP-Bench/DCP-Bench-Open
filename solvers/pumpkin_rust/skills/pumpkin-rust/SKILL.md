---
name: pumpkin-rust
description: Write a DCP-Bench submission for the pumpkin_rust integration - one Rust file defining build(inst, solver), posting constraints through pumpkin_solver's own constructors. Use when generating or repairing a model for solver ID pumpkin_rust.
---

# Pumpkin submissions

A submission is one Rust file defining `build`, written against Pumpkin's own
solver:

```rust
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    ...
    let mut m = Model::new();
    m.put("name", variables);
    m
}
```

`solver` is `pumpkin_solver::Solver`. No `main`, no `use` statements for the
common names, no dependency declarations: the image splices this file into a
binary that glob-imports the prelude first.

```rust
// Maximise the value carried without exceeding the knapsack capacity.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let values = inst.ints("values");
    let weights = inst.ints("weights");
    let capacity = inst.int("capacity");
    let n = values.len();

    let take: Vec<Lit> = (0..n).map(|_| solver.new_literal()).collect();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
            weights.clone(), take.clone(), capacity, tag))
        .post();

    let ceiling: i32 = values.iter().sum();
    let total = solver.new_bounded_integer(0, ceiling);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(values, take.clone(), total, tag))
        .post();

    let mut m = Model::new();
    m.put("x", take);
    m.maximise(total);
    m
}
```

## Posting a constraint

Every constraint follows the same three steps: take a fresh tag, build the
constraint, post it.

```rust
let tag = solver.new_constraint_tag();
solver.add_constraint(pumpkin_solver::equals(terms, rhs, tag)).post();
```

`.reify(flag)` in place of `.post()` makes the constraint hold exactly when
`flag` is true; `.implied_by(flag)` gives the one-way form.

## Variables

```rust
solver.new_bounded_integer(lo, hi)        // Var, an integer over [lo, hi]
solver.new_sparse_integer(vec![..])       // Var, with holes in the domain
solver.new_literal()                      // Lit, a Boolean
solver.get_true_literal()                 // Lit
solver.get_false_literal()                // Lit
```

A constant is `solver.new_bounded_integer(v, v)`, for the places a constraint
wants a variable and the model has a number.

## Terms

Linear constraints take a homogeneous `Vec<Term>`, so a coefficient is written
with Pumpkin's `scaled`:

```rust
vec![x.scaled(1), y.scaled(-1)]                                  // x - y
(0..n).map(|j| xs[j].scaled(w[j])).collect::<Vec<Term>>()        // weighted sum
```

**Never write `scaled(0)`.** Pumpkin multiplies the existing scale without
rechecking it, so a zero-scaled view divides by zero inside a propagator later.
Instance data holding a zero weight is ordinary, so filter first:

```rust
let terms: Vec<Term> = w.iter().zip(&xs)
    .filter(|(&c, _)| c != 0)
    .map(|(&c, &v)| v.scaled(c))
    .collect();
```

If that empties the list, post over a zero constant instead — an empty linear
constraint has no propagator to build.

Where every coefficient is 1, a plain `Vec<Var>` is accepted directly, which is
why `all_different(queens, tag)` needs no mapping.

## The constraints

| Need | Call |
| --- | --- |
| `sum(terms) == rhs` | `equals(terms, rhs, tag)` |
| `sum(terms) != rhs` | `not_equals(terms, rhs, tag)` |
| `sum(terms) <= rhs` | `less_than_or_equals(terms, rhs, tag)` |
| `sum(terms) >= rhs` | negate every term and the bound, then `less_than_or_equals` |
| all-different | `all_different(vars, tag)` |
| `a * b == c` | `times(a, b, c, tag)` |
| `a / b == c` | `division(a, b, c, tag)` |
| `|a| == b` | `absolute(a, b, tag)` |
| largest, smallest | `maximum(vars, target, tag)`, `minimum(vars, target, tag)` |
| `array[index] == value` | `element(index, array, value, tag)`, index 0-based |
| allowed tuples | `table(vars, rows, tag)` |
| forbidden tuples | `negative_table(vars, rows, tag)` |
| scheduling | `cumulative(starts, durations, demands, capacity, tag)` |
| at least one literal | `clause(literals, tag)` |
| every literal | `conjunction(literals, tag)` |
| `sum(w[i] * lit[i]) <= rhs` | `boolean_less_than_or_equals(weights, literals, rhs, tag)` |
| `sum(w[i] * lit[i]) == var` | `boolean_equals(weights, literals, target, tag)` |

There is no `greater_than_or_equals` and no cardinality constraint: "at most k
of these literals" is `boolean_less_than_or_equals(vec![1; n], lits, k, tag)`,
and "at least k" is the same over negated literals with bound `n - k`. A
literal is negated with `!lit`.

`all_different` decomposes into pairwise disequalities, so writing those out by
hand propagates no more weakly.

## Outputs and the objective

```rust
let mut m = Model::new();
m.put("queens", queens);      // Var, Lit, i32, bool, or a Vec of those
m.minimise(total);            // or m.maximise(total); the objective is a Var
m
```

`put` takes the name the brief declares. A `Var` renders as a number and a
`Lit` as `true`/`false`, so match whichever the brief asks for. The objective
must be a single `Var`: tie it to the quantity with an `equals` constraint, or
build it with `boolean_equals` over the literals directly.

## Reading the instance

`inst.int("k")`, `inst.size("k")`, `inst.flag("k")`, `inst.ints("k")`,
`inst.matrix("k")`, `inst.cube("k")`, `inst.strings("k")`, `inst.flags("k")`,
`inst.len("k")`, `inst.has("k")`, `inst.int_or("k", fallback)`. Each panics
naming the field rather than substituting a default.

## What the runner does

1. Calls `build`, then solves.
2. With an objective, proves the optimum and reports success only when Pumpkin
   proved it. A solution found but not proven optimal is a timeout, never an
   answer.
3. Fixes the objective at that value, then enumerates further solutions,
   blocking the **declared outputs** each time.
4. Ends with one status: `limit`, `complete`, `unsat`, `timeout` or `error`.

## Reasoning to record

Say where each variable's bounds come from in the instance, and say so
explicitly wherever a coefficient could be zero on some instance.
