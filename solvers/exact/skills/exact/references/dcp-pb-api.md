# The `dcp_pb` surface, exactly

Signatures from `solvers/exact/dcp_pb.py`, which the image installs at
`/opt/runner/dcp_pb.py`.

## Var

```python
class Var:
    name: str          # the identifier Exact knows it by
    lower: int
    upper: int
    boolean: bool      # only affects how a declared output renders
    def values(self) -> range
```

`boolean` is set by `Pb.bool` and by nothing else. It decides whether a declared
output comes back as `true`/`false` or as `0`/`1`; it has no effect on solving.

## Pb

```python
class Pb:
    solver: exact.Exact       # the real solver, for anything not wrapped here
    objective: tuple | None   # (terms, minimise) once declared

    # variables
    def int(self, lo, hi) -> Var
    def ints(self, n, lo, hi) -> list[Var]
    def int_grid(self, rows, cols, lo, hi) -> list[list[Var]]
    def bool(self) -> Var
    def bools(self, n) -> list[Var]
    def bool_grid(self, rows, cols) -> list[list[Var]]
    def constant(self, value) -> Var
    def negate(self, flag) -> Var

    # linear constraints, terms are (coefficient, Var)
    def le(self, terms, bound) -> None
    def ge(self, terms, bound) -> None
    def eq(self, terms, bound) -> None
    def between(self, terms, low, high) -> None
    def sum_eq(self, vars, bound) -> None
    def sum_le(self, vars, bound) -> None
    def sum_ge(self, vars, bound) -> None
    def weighted_sum_eq(self, coefficients, vars, bound) -> None
    def weighted_sum_le(self, coefficients, vars, bound) -> None
    def weighted_sum_ge(self, coefficients, vars, bound) -> None
    def same(self, left, right) -> None

    # channelling and what it buys
    def indicators(self, var) -> dict[int, Var]
    def is_value(self, var, value) -> Var
    def different(self, left, right) -> None
    def all_different(self, vars) -> None
    def count(self, flags, target) -> None
    def element(self, index, array, value) -> None

    # cardinality over 0/1 variables
    def at_most(self, flags, bound) -> None
    def at_least(self, flags, bound) -> None
    def exactly(self, flags, bound) -> None
    def any(self, flags) -> None

    # objective
    def minimise(self, terms) -> None
    def maximise(self, terms) -> None
```

A zero coefficient is dropped rather than passed to Exact.

## How the encodings work

- **Integer variables are Exact's own**, declared with bounds. Nothing is
  encoded, so a wide domain costs nothing until channelling is asked for.
- **Channelling** creates one 0/1 indicator per value of a variable, with
  `sum(y_v) == 1` and `sum(v * y_v) == x`. It is built on first use and cached,
  so a model that never asks for `is_value`, `different`, `all_different`,
  `count` or `element` never pays for it. This is the expensive part of the
  layer, and it is where a wide domain does start to cost.
- **`element`** uses the index's indicators and a pair of big-M bounds per
  position, with the span taken from the constant array.

## What the runner does

1. Imports the submission and calls `build(instance)`.
2. With an objective, calls `toOptimum` with the remaining budget. `"SAT"` there
   means the optimum was proven; `"TIMEOUT"` means it was not, and Exact still
   holds a solution in that case, so only `"SAT"` is treated as an answer.
3. Pins the objective at the proven optimum. Exact minimises internally, so a
   maximisation's optimum comes back negated and is flipped before pinning.
4. Calls `runFull` for each further solution, blocking the previous assignment
   of the **declared outputs** through their indicators.
5. Ends with one status: `limit`, `complete`, `unsat`, `timeout` or `error`.
