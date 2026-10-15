# The `hermax.model` surface

Signatures from hermax 1.2.5 as installed by `pip install hermax`. Full reference:
[API](https://hermax.readthedocs.io/en/latest/api.html).

## Model

```python
from hermax.model import Model

class Model:
    # variables
    def bool(self, name=None) -> Literal
    def bool_vector(self, name, length) -> BoolVector
    def bool_matrix(self, name, rows, cols) -> BoolMatrix
    def bool_dict(self, name, keys) -> BoolDict
    def int(self, name, lb, ub) -> IntVar
    def int_vector(self, name, length, lb, ub) -> IntVector
    def int_matrix(self, name, rows, cols, lb, ub) -> IntMatrix
    def int_dict(self, name, keys, lb, ub) -> IntDict
    def int_set(self, name, *, lb=None, ub=None, values=None) -> IntSetVar
    def enum(self, name, choices, nullable=False) -> EnumVar
    def enum_vector(self, name, length, choices, nullable=False) -> EnumVector
    def enum_matrix(self, name, rows, cols, choices, nullable=False) -> EnumMatrix
    def interval(self, name, *, start, duration, end) -> IntervalVar

    # derived integers
    def sum_var(self, items, name=None) -> IntVar
    def max(self, vec_or_items, name=None) -> IntVar
    def min(self, vec_or_items, name=None) -> IntVar
    def lower_bound(self, vec_or_items, name=None) -> IntVar
    def upper_bound(self, vec_or_items, name=None) -> IntVar
    def scale(self, x, factor, name=None) -> IntVar      # factor must be > 0
    def floor_div(self, x, divisor, name=None) -> IntVar

    # global: adds its own constraint, do not wrap in `m &=`
    def cumulative(self, starts, durations, demands, capacity, *, backend="auto") -> None

    # objective
    obj                       # obj[weight] += literal, or obj += expression
    tier_obj                  # lexicographic tiers
    def add_soft(self, constraint, weight)

    def solve(self, *, time_limit=None, sat_solver_name="g4",
              maxsat_backend="rc2", backend="auto", assumptions=None,
              incremental=True, ...) -> SolveResult
```

Constraints are posted with `model &= constraint`.

`cumulative` backends: `"time"` loops over every time tick (size grows with the horizon),
`"task"` adds pairwise indicators (size grows with the square of the task count), and
`"auto"` picks `"task"` when `N*N < horizon`, otherwise `"time"`.

## Containers

```python
BoolVector:  at_least_one()  at_most_one()  exactly_one()  is_in(...)
BoolMatrix:  row(i)  col(j)  flatten()
IntVector:   all_different()  increasing()  lexicographic_less_than(other)
             max  min  running_max()  running_min()  running_sum()  is_in(...)
IntMatrix:   row(i)  col(j)  flatten()
IntVar:      lb  ub  in_range(lo, hi)  forbid_value(v)  forbid_interval(lo, hi)
             distance_at_most(other, d)  piecewise(...)  scale(k)
EnumVar:     choices  is_in(...)  is_in_or_none(...)
```

`IntVar` supports `+ - *` with integers and other variables, and the six comparisons.
Linear constraints may have sums on both sides: `m &= (sum(a[i]) == sum(b[i]))`.
`all_different`, `increasing` and the other container methods take variables, not expressions:
give each expression its own `IntVar` first.
A literal is negated with `~lit`; literals combine with `|` and `&`. `x != v` on an
`IntVar` is a `Literal`. `x // k` is a `DivExpr`, not an `IntVar`; use `floor_div` when an
`IntVar` is needed.

A sum of variables is a `PBExpr`; a single `c * literal` is a `Term`. `m &= (pbexpr <= k)`
posts a pseudo-Boolean constraint.

## SolveResult

```python
result.status      # "sat" | "optimum" | "unsat" | "interrupted"
                   # | "interrupted_sat" | "unknown" | "error"
result.cost        # int, or None when the model declares no soft clauses
result.ok          # True for sat, optimum AND interrupted_sat
result.backend     # which solver actually ran
result[var]        # value; r[vector] is a list, r[matrix] a list of row lists (same shape)
                   # a PBExpr or Term raises TypeError here: compute the sum in Python
                   # from the decoded variables
```

`result.ok` is broader than "proven": it includes `interrupted_sat`, where a solution
exists but was not proven best. Test `result.status == "optimum"` for an optimal answer.
