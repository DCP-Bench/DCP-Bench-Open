# The driver surface, exactly

Signatures from `solvers/pumpkin_rust/rust/driver/src/lib.rs`, which is what the
image compiles a submission against. `Var` is `DomainId`, `Lit` is `Literal`,
and `Term` is `AffineView<DomainId>` — one `coefficient * variable` summand.

## Widening into a linear constraint

Pumpkin's linear constraints take a homogeneous `Vec<Term>`, so a `Var` and a
`Lit` cannot share a `vec![]` untouched. Widen both:

```rust
pub fn t(v: impl IntoTerm) -> Term;                       // 1 * v
pub fn c(coefficient: i32, v: impl IntoTerm) -> Term;     // k * v
pub fn terms<T: IntoTerm + Copy>(vs: &[T]) -> Vec<Term>;
pub fn weighted<T: IntoTerm + Copy>(coefficients: &[i32], vs: &[T]) -> Vec<Term>;
```

`IntoTerm` is implemented for `Var`, `Lit`, `Term` and references to them.
`weighted` panics when the two slices differ in length.

## Instance

```rust
impl Instance {
    pub fn has(&self, key: &str) -> bool;
    pub fn get(&self, key: &str) -> &Value;
    pub fn keys(&self) -> Vec<String>;
    pub fn int(&self, key: &str) -> i32;
    pub fn int_or(&self, key: &str, fallback: i32) -> i32;
    pub fn size(&self, key: &str) -> usize;
    pub fn flag(&self, key: &str) -> bool;
    pub fn ints(&self, key: &str) -> Vec<i32>;
    pub fn flags(&self, key: &str) -> Vec<bool>;
    pub fn strings(&self, key: &str) -> Vec<String>;
    pub fn matrix(&self, key: &str) -> Vec<Vec<i32>>;
    pub fn cube(&self, key: &str) -> Vec<Vec<Vec<i32>>>;
    pub fn len(&self, key: &str) -> usize;
}
```

Every accessor panics naming the key and the value it found. A panic leaves the
process with a nonzero exit, which the runner reports as an execution error with
the message on stderr — loud, and never a silent default.

## Cp

```rust
pub struct Cp { pub solver: Solver }

// variables
pub fn int(&mut self, lo: i32, hi: i32) -> Var;
pub fn ints(&mut self, n: usize, lo: i32, hi: i32) -> Vec<Var>;
pub fn grid(&mut self, rows: usize, cols: usize, lo: i32, hi: i32) -> Vec<Vec<Var>>;
pub fn sparse(&mut self, values: &[i32]) -> Var;
pub fn bool(&mut self) -> Lit;
pub fn bools(&mut self, n: usize) -> Vec<Lit>;
pub fn bool_grid(&mut self, rows: usize, cols: usize) -> Vec<Vec<Lit>>;
pub fn constant(&mut self, value: i32) -> Var;
pub fn always(&mut self) -> Lit;
pub fn never(&mut self) -> Lit;
pub fn lower_bound(&self, v: impl IntoTerm) -> i32;
pub fn upper_bound(&self, v: impl IntoTerm) -> i32;
pub fn tag(&mut self) -> ConstraintTag;

// linear, constant right-hand side
pub fn eq(&mut self, terms: Vec<Term>, rhs: i32);
pub fn ne(&mut self, terms: Vec<Term>, rhs: i32);
pub fn le(&mut self, terms: Vec<Term>, rhs: i32);
pub fn lt(&mut self, terms: Vec<Term>, rhs: i32);
pub fn ge(&mut self, terms: Vec<Term>, rhs: i32);
pub fn gt(&mut self, terms: Vec<Term>, rhs: i32);

// linear, variable right-hand side
pub fn sum_eq(&mut self, terms: Vec<Term>, target: impl IntoTerm);
pub fn sum_le(&mut self, terms: Vec<Term>, target: impl IntoTerm);
pub fn sum_ge(&mut self, terms: Vec<Term>, target: impl IntoTerm);
pub fn same(&mut self, a: impl IntoTerm, b: impl IntoTerm);
pub fn differ(&mut self, a: impl IntoTerm, b: impl IntoTerm);
pub fn sum(&mut self, terms: Vec<Term>) -> Var;

// arithmetic
pub fn times(&mut self, a: impl IntoTerm, b: impl IntoTerm, product: impl IntoTerm);
pub fn div(&mut self, numerator: impl IntoTerm, denominator: impl IntoTerm, quotient: impl IntoTerm);
pub fn abs(&mut self, signed: impl IntoTerm, magnitude: impl IntoTerm);
pub fn max(&mut self, vars: Vec<Term>, target: impl IntoTerm);
pub fn min(&mut self, vars: Vec<Term>, target: impl IntoTerm);

// globals
pub fn all_different(&mut self, vars: Vec<Term>);
pub fn element(&mut self, index: impl IntoTerm, array: Vec<Term>, value: impl IntoTerm);
pub fn element_of(&mut self, index: impl IntoTerm, array: &[i32], value: impl IntoTerm);
pub fn table(&mut self, vars: Vec<Term>, rows: Vec<Vec<i32>>);
pub fn forbidden(&mut self, vars: Vec<Term>, rows: Vec<Vec<i32>>);
pub fn cumulative(&mut self, starts: Vec<Term>, durations: &[i32], demands: &[i32], capacity: i32);

// Booleans
pub fn any(&mut self, literals: Vec<Lit>);
pub fn all(&mut self, literals: Vec<Lit>);
pub fn bool_le(&mut self, weights: &[i32], literals: &[Lit], rhs: i32);
pub fn bool_sum_eq(&mut self, weights: &[i32], literals: &[Lit], target: Var);
pub fn exactly(&mut self, literals: &[Lit], count: i32);
pub fn at_most(&mut self, literals: &[Lit], count: i32);
pub fn at_least(&mut self, literals: &[Lit], count: i32);

// reification
pub fn is(&mut self, v: impl IntoTerm, value: i32) -> Lit;   // both directions
pub fn iff_eq(&mut self, flag: Lit, terms: Vec<Term>, rhs: i32);
pub fn iff_le(&mut self, flag: Lit, terms: Vec<Term>, rhs: i32);
pub fn iff_ge(&mut self, flag: Lit, terms: Vec<Term>, rhs: i32);
pub fn iff_is(&mut self, flag: Lit, v: impl IntoTerm, value: i32);
pub fn when_eq(&mut self, flag: Lit, terms: Vec<Term>, rhs: i32);   // flag -> only
pub fn when_le(&mut self, flag: Lit, terms: Vec<Term>, rhs: i32);
pub fn when_ge(&mut self, flag: Lit, terms: Vec<Term>, rhs: i32);
```

## Model

```rust
impl Model {
    pub fn new() -> Model;
    pub fn put(&mut self, name: &str, value: impl IntoNode) -> &mut Model;
    pub fn minimise(&mut self, objective: Var) -> &mut Model;
    pub fn maximise(&mut self, objective: Var) -> &mut Model;
}
```

`IntoNode` covers `Var`, `Lit`, `i32`, `bool`, `Vec<T>`, `&[T]` and `&Vec<T>`
for any `T: IntoNode`, so nesting works to any depth. A `Lit` renders as JSON
`true`/`false`; a `Var` as an integer. `put` panics on a repeated name.

## Reaching past the wrapper

`cp.solver` is the real `pumpkin_solver::Solver`. Every Pumpkin constraint
function needs a `ConstraintTag`, which `cp.tag()` mints:

```rust
let tag = cp.tag();
cp.solver
    .add_constraint(dcp_pumpkin::pumpkin_solver::all_different(terms(&xs), tag))
    .post();
```

The posting methods are `.post()`, `.implied_by(lit)` and, for a constraint with
a defined negation, `.reify(lit)`.

## How the driver solves

1. Calls `build`, then takes a default brancher and a resolution conflict
   resolver.
2. With an objective, runs `LinearSatUnsat` under the evaluator's time budget.
   Only `OptimisationResult::Optimal` is reported as a solution; `Satisfiable`
   (found but unproven) becomes a timeout.
3. Emits the solution, then fixes the objective at its proven value and
   continues, so any further solutions are optimal too.
4. Enumerates by adding a clause that rules out the previous **declared-output**
   values, not the full assignment — two full assignments often agree on every
   declared output, and the evaluator counts distinct declared outputs.
5. Ends with exactly one status: `limit` (requested count reached), `complete`
   (search exhausted with at least one solution), `unsat`, `timeout`, or `error`.
