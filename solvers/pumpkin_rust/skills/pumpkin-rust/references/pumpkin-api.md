# The Pumpkin surface, exactly

What a submission can call. The names under `pumpkin_solver::` are the
framework's own; `Instance`, `Model` and `Node` are the integration's harness,
which exists because Pumpkin has no notion of a JSON instance or of which
variables a benchmark problem declares as its answer.

## Solver

```rust
solver.new_bounded_integer(lo: i32, hi: i32) -> Var       // DomainId
solver.new_sparse_integer(values: Vec<i32>) -> Var
solver.new_literal() -> Lit                               // Literal
solver.get_true_literal() -> Lit
solver.get_false_literal() -> Lit
solver.new_constraint_tag() -> ConstraintTag

solver.add_constraint(constraint)
    .post()                  // the constraint holds
    .reify(flag)             // flag <-> the constraint
    .implied_by(flag)        // flag -> the constraint
```

`Var` is `DomainId`, `Lit` is `Literal`, `Term` is `AffineView<DomainId>`.

## Terms

`x.scaled(k)` and `x.offset(k)` come from `TransformableVariable`, which the
prelude brings into scope. A `Vec<Term>` is what the linear constraints take;
where every coefficient is 1, a `Vec<Var>` is accepted directly.

**`scaled(0)` is a trap.** `AffineView::scaled` multiplies the existing scale
without rechecking it, bypassing the non-zero assertion in `AffineView::new`,
and the zero-scaled view divides by zero inside a propagator during search. The
observed failure is a panic in `num_ext.rs`, far from the line that caused it.
Filter zero coefficients before building terms.

## Constraints

```rust
pumpkin_solver::equals(terms, rhs, tag)
pumpkin_solver::not_equals(terms, rhs, tag)
pumpkin_solver::less_than_or_equals(terms, rhs, tag)

pumpkin_solver::all_different(vars, tag)
pumpkin_solver::element(index, array, value, tag)      // index is 0-based
pumpkin_solver::table(vars, rows, tag)
pumpkin_solver::negative_table(vars, rows, tag)
pumpkin_solver::cumulative(starts, durations, demands, capacity, tag)

pumpkin_solver::times(a, b, product, tag)
pumpkin_solver::division(numerator, denominator, quotient, tag)
pumpkin_solver::absolute(signed, magnitude, tag)
pumpkin_solver::maximum(vars, target, tag)
pumpkin_solver::minimum(vars, target, tag)

pumpkin_solver::clause(literals, tag)                  // at least one is true
pumpkin_solver::conjunction(literals, tag)             // all are true
pumpkin_solver::boolean_less_than_or_equals(weights, literals, rhs, tag)
pumpkin_solver::boolean_equals(weights, literals, target_var, tag)
```

There is no `greater_than_or_equals`: negate every term and the bound. There is
no cardinality constraint: use `boolean_less_than_or_equals` with all-ones
weights, over negated literals for a lower bound.

`all_different` decomposes into pairwise disequalities, so it propagates no more
strongly than writing them out.

## Instance

```rust
inst.has(key) -> bool          inst.get(key) -> &Value
inst.keys() -> Vec<String>     inst.len(key) -> usize
inst.int(key) -> i32           inst.int_or(key, fallback) -> i32
inst.size(key) -> usize        inst.flag(key) -> bool
inst.ints(key) -> Vec<i32>     inst.flags(key) -> Vec<bool>
inst.matrix(key) -> Vec<Vec<i32>>
inst.cube(key) -> Vec<Vec<Vec<i32>>>
inst.strings(key) -> Vec<String>
```

Every accessor panics naming the offending key and the value it found, rather
than substituting a default, so a schema mismatch is a loud failure instead of
a wrong answer.

## Model

```rust
let mut m = Model::new();
m.put(name, value);     // Var, Lit, i32, bool, Node, or a Vec of those
m.minimise(objective);  // objective is a single Var
m.maximise(objective);
```

A `Var` renders as a number, a `Lit` as `true`/`false`. `put` panics on a
repeated name.

## What the runner guarantees

With an objective it calls `optimise` and accepts only
`OptimisationResult::Optimal`. `Satisfiable` and `Stopped` both mean a solution
exists that was never proven optimal, and both are reported as a timeout, so
the evaluator never receives an unproven answer to compare against the
reference optimum.

## Compilation

One `rustc` invocation against prebuilt rlibs, no network, no cargo. Typical
cost is 0.2 to 1.3 seconds. A submission cannot add dependencies; everything it
needs is in the prelude or in `std`.
