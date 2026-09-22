---
name: exact
description: Write a DCP-Bench submission for the exact integration - one Python file defining build(instance) that returns an exact.Exact solver built with addVariable, addConstraint, addReification and setObjective. Use when generating or repairing a model for solver ID exact.
---

# Exact submissions

A submission is one Python file defining `build(instance)`, written against
Exact's own Python bindings:

```python
from exact import Exact


def build(instance):
    ...
    return solver, outputs                                 # satisfaction
    return solver, outputs, ("maximize", terms)            # optimisation
```

`terms` is the objective as `[(coefficient, variable_name), ...]`. The runner
sets it, proves the optimum, and pins it before enumerating.

```python
from exact import Exact


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]
    n = len(values)

    solver = Exact()
    x = [f"x{j}" for j in range(n)]
    for name in x:
        solver.addVariable(name, 0, 1)
    solver.addConstraint(list(zip(weights, x)), False, 0, True, capacity)
    return solver, {"x": x}, ("maximize", list(zip(values, x)))
```

## Variables are names

Exact identifies a variable by the string you gave it. There are no variable
objects, so a submission keeps its own lists of names and hands those back as
`outputs`.

```python
solver.addVariable(name, lower_bound=0, upper_bound=1, encoding="log")
```

**Integer variables are native**, declared by their bounds rather than encoded
value by value. A domain running into the thousands costs nothing here, which
is the main thing this integration can do that the SAT and MaxSAT ones cannot.

Values come back as integers. The evaluator compares a 0/1 integer and a
Boolean as equal, so a variable over 0..1 satisfies a Boolean output with no
special handling.

## Constraints

```python
solver.addConstraint(terms, use_lower_bound, lower_bound,
                     use_upper_bound, upper_bound)
```

One call carries both bounds, so:

| Meaning | Call |
| --- | --- |
| `sum >= k` | `addConstraint(terms, True, k)` |
| `sum <= k` | `addConstraint(terms, False, 0, True, k)` |
| `sum == k` | `addConstraint(terms, True, k, True, k)` |
| `lo <= sum <= hi` | `addConstraint(terms, True, lo, True, hi)` |

A coefficient of zero should be dropped rather than passed.

## Reification, and what it buys

```python
solver.addReification(head, True, terms, lower_bound)
# head == 1  <->  sum(terms) >= lower_bound
```

Verified in both directions. `addLeftReification` and `addRightReification`
give the one-way forms. This is how a condition becomes a variable you can
count, forbid or put in the objective.

`solver.addMultiplication(factors, True, low_name, True, high_name)` bounds a
product by other variables: with `["a", "b"]` bounded below and above by `"z"`,
it holds `z == a * b`.

## Channelling, when you need it

Exact reasons about linear constraints. Anything that talks about a variable
*taking a particular value* — all-different, counting occurrences, indexing an
array — needs 0/1 indicators, which cost one variable per value:

```python
# y[v] == 1 exactly when x == v
y = [f"x_is_{v}" for v in range(lo, hi + 1)]
for name in y:
    solver.addVariable(name, 0, 1)
solver.addConstraint([(1, name) for name in y], True, 1, True, 1)
solver.addConstraint([(v, y[v - lo]) for v in range(lo, hi + 1)] + [(-1, "x")],
                     True, 0, True, 0)
```

With those, all-different is "at most one variable takes each value", and a
count is a linear constraint over the indicators. **Build them only for the
variables that need them**, and keep those variables' domains tight: this is
the one place where a wide domain does cost, and it is worth saying in the
reasoning why the bound you chose is the right one.

## What the runner does

1. Imports the submission and calls `build(instance)`.
2. With an objective, calls `setObjective` then `toOptimum` with the remaining
   budget. **`"SAT"` there means the optimum was proven** — there is no
   `"OPTIMAL"`. `"TIMEOUT"` means it was not, and Exact still holds a solution
   in that case, so only `"SAT"` is treated as an answer.
3. Pins the objective at the proven optimum. Exact minimises internally, so a
   maximisation's optimum comes back negated and is flipped before pinning.
4. Calls `runFull` for each further solution and blocks with
   `invalidateLastSol(names)`, projected onto the **declared outputs**.
5. Ends with one status: `limit`, `complete`, `unsat`, `timeout` or `error`.

## Reasoning to record

Say where each variable's bounds come from in the instance. If you built
indicators, say for which variables and why their domains are small enough to
afford it.
