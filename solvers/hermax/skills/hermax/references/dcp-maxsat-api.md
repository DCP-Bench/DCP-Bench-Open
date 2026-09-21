# The `dcp_maxsat` surface, exactly

Signatures from `solvers/hermax/dcp_maxsat.py`, which the image installs at
`/opt/runner/dcp_maxsat.py`. The encoding is the same as the SAT integration's;
what this one adds is the `link_*` family, which ties a variable to an
expression so it can serve as an objective.

## IntVar

An integer variable under a direct (one-hot) encoding.

```python
class IntVar:
    values: list[int]          # the domain, in order
    lits: list[int]            # lits[i] is true exactly when the value is values[i]
    def literal(self, value) -> int | None   # the literal for `self == value`
    def read(self, truth) -> int             # the value taken, given the true literals
    def terms(self, coefficient=1) -> list[tuple[int, int]]
```

`literal` returns `None` for a value outside the domain, which is the idiom for
skipping impossible combinations when writing clauses by hand.

## Sat

```python
class MaxSat:
    pool: IDPool
    clauses: list[list[int]]

    # variables
    def bool(self) -> int
    def bools(self, n) -> list[int]
    def bool_grid(self, rows, cols) -> list[list[int]]
    def always(self) -> int
    def never(self) -> int
    def int(self, lo, hi) -> IntVar
    def int_from(self, values) -> IntVar
    def ints(self, n, lo, hi) -> list[IntVar]
    def int_grid(self, rows, cols, lo, hi) -> list[list[IntVar]]
    def constant(self, value) -> IntVar

    # raw logic
    def clause(self, lits) -> None
    def implies(self, antecedent, consequent) -> None
    def iff(self, left, right) -> None

    # cardinality over literals
    def at_most(self, lits, bound) -> None
    def at_least(self, lits, bound) -> None
    def exactly(self, lits, bound) -> None

    # weighted sums over literals
    def bool_sum_le(self, weights, lits, bound) -> None
    def bool_sum_ge(self, weights, lits, bound) -> None
    def bool_sum_eq(self, weights, lits, bound) -> None

    # linear constraints over integer variables
    def linear_le(self, terms, bound) -> None    # terms are (coefficient, IntVar)
    def linear_ge(self, terms, bound) -> None
    def linear_eq(self, terms, bound) -> None
    def sum_eq(self, vars, bound) -> None
    def sum_le(self, vars, bound) -> None
    def sum_ge(self, vars, bound) -> None
    def weighted_sum_eq(self, coefficients, vars, bound) -> None
    def weighted_sum_le(self, coefficients, vars, bound) -> None
    def weighted_sum_ge(self, coefficients, vars, bound) -> None

    # tying a variable to a sum, which is how an objective is built
    def link_bool_sum(self, weights, lits, var) -> None
    def link_sum(self, terms, var) -> None
    def link_count(self, lits, var) -> None

    # relations
    def is_value(self, var, value) -> int
    def same(self, left, right) -> None
    def different(self, left, right) -> None
    def all_different(self, vars) -> None
```

## How the encodings work

- **One-hot integers.** `int_from` allocates one literal per value, posts the
  at-least-one clause and a pairwise at-most-one. So `x == v` is a literal, and
  the cost of a variable is the size of its domain.
- **Linear constraints** flatten to pseudo-Boolean sums over those one-hot
  literals, with the weight of "x takes v" being v. Each term is shifted down by
  its own minimum so every weight is non-negative, and the shift moves the
  bound; this is what makes negative domains and negative coefficients work.
  Constraints that are already decided, because every term is fixed or the bound
  lies outside the attainable range, are resolved without calling the encoder.
- **Cardinality** uses `pysat.card` with a sequential counter, except the
  at-most-one inside an integer variable, which is pairwise because it is small.
- **`all_different`** posts an at-most-one per value across the variables that
  can take it, rather than pairwise disequalities.
- **`link_*`** turns `sum == var` into one pair of half-reified bounds per value
  of `var`: taking that value forces the sum below it and above it. Exactly one
  value holds, so together they pin the sum. A value the sum cannot reach is
  ruled out directly.

## What the runner does

1. Imports the submission and calls `build(instance)`.
2. Turns the objective variable's one-hot literals into soft units: minimising
   makes "not this value" cost `value - min`, maximising makes it cost
   `max - value`. Exactly one value holds, so the broken weight is the objective
   shifted by a constant, and comparing costs compares objective values.
3. Solves in a **child process**, because no hermax backend accepts
   `solve(time_limit=...)` or implements `set_terminate`; the parent kills the
   child on budget and supplies the status the child never reached.
4. Emits a solution only on `SolveStatus.OPTIMUM`. `INTERRUPTED_SAT` means found
   but not proven best, which is reported as a timeout.
5. Blocks the **declared outputs** and solves again, stopping once the best
   remaining cost exceeds the optimum.
6. Ends with one status: `limit`, `complete`, `unsat`, `timeout` or `error`.
