# Pumpkin 0.5.0 API: signatures

Signatures as compiled against `pumpkin-solver = "=0.5.0"`. Module paths are the ones the
examples import. Constructors are documented in the [crate API](https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/);
the solver type is [`Solver`](https://docs.rs/pumpkin-solver/0.5.0/pumpkin_solver/core/struct.Solver.html).

## Imports

```rust
use std::ops::ControlFlow;
use std::time::Duration;

use pumpkin_solver::conflict_resolvers::resolvers::ResolutionResolver;
use pumpkin_solver::core::DefaultBrancher;
use pumpkin_solver::core::optimisation::OptimisationDirection;
use pumpkin_solver::core::optimisation::linear_sat_unsat::LinearSatUnsat;
use pumpkin_solver::core::predicates::{Predicate, PredicateConstructor};
use pumpkin_solver::core::results::{OptimisationResult, ProblemSolution, SatisfactionResult, SolutionReference};
use pumpkin_solver::core::termination::TimeBudget;
use pumpkin_solver::core::variables::TransformableVariable;
use pumpkin_solver::Solver;
```

Import only what a program uses. `TransformableVariable` provides `scaled` and `offset`;
`PredicateConstructor` provides `disequality_predicate` on integer variables.

## Solver

```rust
Solver::default() -> Solver
solver.new_bounded_integer(lo: i32, hi: i32) -> DomainId     // integer variable
solver.new_sparse_integer(values: Vec<i32>) -> DomainId
solver.new_literal() -> Literal                              // Boolean
solver.get_true_literal() -> Literal
solver.get_false_literal() -> Literal
solver.new_constraint_tag() -> ConstraintTag
solver.add_constraint(c).post()                              // c holds
solver.add_constraint(c).reify(flag)                         // c holds iff flag
solver.add_constraint(c).implied_by(flag)                    // flag implies c
solver.add_clause(predicates: Vec<Predicate>, tag)           // blocking clauses
solver.default_brancher() -> brancher
solver.satisfy(&mut brancher, &mut termination, &mut resolver) -> SatisfactionResult
solver.optimise(&mut brancher, &mut termination, &mut resolver, procedure) -> OptimisationResult
```

`DomainId` is the integer variable type, `Literal` the Boolean one. `AffineView<DomainId>` is a
scaled or offset view, the type `Term`s are built from.

## Terms and literals

```rust
x.scaled(k: i32) -> AffineView<DomainId>     // k * x
x.offset(k: i32) -> AffineView<DomainId>     // x + k
lit.get_integer_variable()                   // the Boolean as a 0/1 integer view
lit.get_integer_variable().scaled(k)
!lit                                         // negated literal
x.disequality_predicate(v: i32) -> Predicate // x != v
lit.get_true_predicate() / lit.get_false_predicate()
```

A linear constraint takes `Vec<AffineView<DomainId>>`, or a `Vec<DomainId>` when every
coefficient is 1. `scaled(0)` panics on a plain variable (`Multiplication by zero is not
invertable`), and `scaled` on an already scaled view multiplies the scale without the check.

## Constraint constructors

Each returns a constraint for `add_constraint`. `tag` is a `ConstraintTag`.

```rust
equals(terms, rhs: i32, tag)            not_equals(terms, rhs, tag)
less_than_or_equals(terms, rhs, tag)    less_than(terms, rhs, tag)
greater_than_or_equals(terms, rhs, tag) greater_than(terms, rhs, tag)
plus(a, b, c, tag)                      // a + b == c, variables
all_different(vars, tag)                // pairwise binary_not_equals underneath
element(index, array, value, tag)       // array[index] == value, index 0-based
table(vars, rows: Vec<Vec<i32>>, tag)
negative_table(vars, rows, tag)
cumulative(starts, durations, demands, capacity: i32, tag)
cumulative_with_options(starts, durations, demands, capacity, options, tag)
times(a, b, product, tag)
division(numerator, denominator, quotient, tag)   // truncates toward zero
absolute(signed, magnitude, tag)
maximum(vars, target, tag)              minimum(vars, target, tag)
clause(literals: Vec<Literal>, tag)     // at least one true
conjunction(literals, tag)              // all true
boolean_less_than_or_equals(weights: Vec<i32>, literals, rhs: i32, tag)
boolean_equals(weights: Vec<i32>, literals, target: DomainId, tag)
```

`disjunctive_strict` also exists for no-overlap tasks, with its own task type; `cumulative`
covers the common case. The vendored source shows no `count`, cardinality or modulo
constructor.

## Optimisation

```rust
let procedure = LinearSatUnsat::new(
    OptimisationDirection::Minimise,      // or Maximise
    objective,                            // a single DomainId
    |_: &Solver, _: SolutionReference, _: &DefaultBrancher, _: &ResolutionResolver| {
        ControlFlow::<()>::Continue(())   // keep going after each improving solution
    },
);
```

The callback is called on each improving solution; `Continue(())` keeps the search going.
The result variants and what each means are in [SKILL.md](../SKILL.md#solving).

## Solutions and enumeration

```rust
found.solution() -> SolutionReference             // from SatisfactionResult::Satisfiable(found)
solution.get_integer_value(v) -> i32              // DomainId or Literal (1 or 0)
optimal.get_integer_value(objective) -> i32       // from OptimisationResult::Optimal(optimal)
```

Enumeration is a loop of `satisfy` and `add_clause` ([SKILL.md](../SKILL.md#all-solutions)).
After `Optimal`, post `equals(vec![objective.scaled(1)], best, tag)` before the loop to
enumerate optimal solutions only.
