# The `hermax.model` surface, exactly

Signatures taken from hermax 1.2.5 as installed in the integration image. The
image installs nothing of this repository's own beside `run.py`, so this is the
whole modelling vocabulary available to a submission.

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

    # global
    def cumulative(self, starts, durations, demands, capacity, *, backend="auto")

    # objective
    obj                       # obj[weight] += literal, or obj += expression
    tier_obj                  # lexicographic tiers
    def add_soft(self, constraint, weight)

    def solve(self, *, time_limit=None, sat_solver_name="g4",
              maxsat_backend="rc2", backend="auto", assumptions=None,
              incremental=True, ...) -> SolveResult
```

Constraints are posted with `model &= constraint`.

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

`IntVar` supports `+ - *` with integers and other variables, and the six
comparisons. A literal is negated with `~lit`, and literals combine with
`|` and `&`.

## SolveResult

```python
result.status      # "sat" | "optimum" | "unsat" | "interrupted"
                   # | "interrupted_sat" | "unknown" | "error"
result.cost        # int, or None when the model declares no soft clauses
result.ok          # True for sat, optimum AND interrupted_sat
result.backend     # which solver actually ran
result[var]        # value; a container yields nested lists
```

**`result.ok` is broader than "this is an answer."** It includes
`interrupted_sat`, where a solution exists but was never proven best. The
runner treats that as a timeout.

## Costs to keep in mind

- **Integer variables are encoded**, so a wide domain is not free the way it is
  in a CP or pseudo-Boolean solver. Bound them by what the instance can reach.
- **A pseudo-Boolean equality is the expensive shape.** `sum(c[j] * x[j]) == t`
  over a wide `t` dominated the run time of every model where it appeared.
  Measured: 43 s to build, against 0.21 s for the same problem expressed with
  soft clauses.
- `m.scale` rejects a non-positive factor, so a sign flip has to be written as
  a complement against a known upper bound.
- Solving with `time_limit` selects a portfolio backend, which is slightly
  slower than the default on easy models (3.15 s against 1.81 s on the
  four-by-four assignment problem) and is what makes the budget enforceable.
