---
name: hermax
description: Write a DCP-Bench submission for the hermax integration - one Python file defining build(instance) against hermax.model.Model, with any objective declared as soft clauses on model.obj. Use when generating or repairing a model for solver ID hermax.
---

# hermax (MaxSAT) submissions

A submission is one Python file defining `build(instance)`, written against
hermax's own modelling layer:

```python
from hermax.model import Model


def build(instance):
    ...
    return m, outputs
```

Always two values. There is no objective in the return: hermax models carry
their objective on `m.obj`, and the runner reads it off the solve result.

```python
from hermax.model import Model


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]

    m = Model()
    take = m.bool_vector("take", len(values))
    m &= (sum(weights[j] * take[j] for j in range(len(values))) <= capacity)

    # Maximising the value carried means paying for what is left behind.
    for j, value in enumerate(values):
        m.obj[value] += take[j]
    return m, {"x": take}
```

## The objective is soft clauses

`m.obj[weight] += literal` adds a soft clause that **pays `weight` when the
literal is false**. That polarity is the whole trick:

- **minimise** a total: pay when the literal is *true*, so write `~lit`.
  `m.obj[cost[i][j]] += ~x[i][j]` charges `cost[i][j]` for using pairing
  `(i, j)`.
- **maximise** a total: pay when the literal is *false*, so write the literal
  itself. `m.obj[value] += take[j]` charges for every item left behind, and the
  minimum total forgone is the maximum total taken.

Either way the solver minimises the broken weight, which is what MaxSAT is.
`m.obj += expression` also works and reads well for small models, but see the
next section before reaching for it.

## Do not route the objective through an integer variable

Declaring `total = m.int(...)` and tying it with
`m &= (sum(c[j] * x[j] for j in ...) == total)` is the single most expensive
mistake available here. That equality has to be encoded as a pseudo-Boolean
constraint over the full range of the sum.

Measured on a four-by-four assignment problem with costs up to 125: the
soft-clause form builds and solves in **0.21 s**, the auxiliary-variable form
spends **43 s inside `build` alone** before solving starts. Same model, same
answer.

Only introduce an integer objective variable when the brief declares the
objective value as an output. Even then, keep the soft clauses as the objective
and let the variable be tied separately, or narrow its bounds to the values the
sum can actually reach.

## The modelling surface

Constraints are posted with `m &= constraint`.

| Need | Call |
| --- | --- |
| one Boolean | `m.bool(name)` |
| Booleans | `m.bool_vector(name, n)`, `m.bool_matrix(name, rows, cols)` |
| integers | `m.int(name, lb, ub)`, `m.int_vector(...)`, `m.int_matrix(...)` |
| named choices | `m.enum(name, choices)`, `m.enum_vector(...)` |
| cardinality | `bv.at_most_one()`, `bv.at_least_one()`, `bv.exactly_one()` |
| all-different | `iv.all_different()` |
| ordering | `iv.increasing()`, `iv.lexicographic_less_than(other)` |
| aggregates | `m.sum_var(items)`, `m.max(vec)`, `m.min(vec)`, `iv.running_sum()` |
| value tests | `x == v`, `x != v`, `x.in_range(lo, hi)`, `x.forbid_value(v)` |
| scheduling | `m.interval(...)`, `m.cumulative(starts, durations, demands, cap)` |

A matrix gives `.row(i)`, `.col(j)` and `.flatten()`; the row and column views
carry the cardinality helpers, so `m &= x.row(i).exactly_one()` is the direct
way to say "exactly one per row".

Linear constraints accept ordinary Python sums over variables:
`m &= (sum(w[j] * x[j] for j in range(n)) <= cap)`.

## Outputs

`outputs` maps each name the brief declares to variables of this model. A
vector or matrix can be handed over whole — the runner reads
`result[container]` and gets back nested lists of `bool` or `int`, matching
whichever the brief asked for. Leaves must be `IntVar` or `Literal`; do not put
plain Python values in the dictionary.

Booleans render as `true`/`false`. If the brief declares 0/1 integers, use
`m.int(name, 0, 1)` instead of `m.bool(name)`.

## What the runner does

1. Imports the submission and calls `build(instance)`.
2. Calls `model.solve(time_limit=...)` with whatever budget is left.
3. Treats only `optimum` (with an objective) and `sat` (without one) as an
   answer. `interrupted_sat` means a solution was found without proving it
   best, and is reported as a timeout, never as a result.
4. Emits the solution, then posts a blocking clause over the **declared
   outputs** and solves again.
5. Stops with `complete` when the cost rises above the first one, which is when
   the optimal solutions are exhausted, or when the model goes `unsat`.

So enumeration covers optimal solutions only, and two submissions that declare
different outputs are blocked differently even for the same problem.

## Reasoning to record

Say which way the soft-clause polarity runs and why, in one line. If an integer
variable appears anywhere near the objective, say what its bounds are and why
they are narrow enough to encode.
