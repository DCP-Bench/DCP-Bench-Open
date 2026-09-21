---
name: exact
description: Write a DCP-Bench submission for the exact integration - one Python file defining build(instance), using the Pb builder from dcp_pb to state a pseudo-Boolean model for the Exact solver. Use when generating or repairing a model for solver ID exact.
---

# Exact submissions

A submission is one Python file defining:

```python
from dcp_pb import Pb


def build(instance):
    ...
    return pb, outputs
```

`dcp_pb` ships inside the image.

```python
from dcp_pb import Pb


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]

    pb = Pb()
    x = pb.bools(len(values))
    pb.weighted_sum_le(weights, x, capacity)
    pb.maximise(list(zip(values, x)))
    return pb, {"x": x}
```

## What makes this integration different

Exact is pseudo-Boolean, so two things the SAT and MaxSAT integrations have to
work around are simply available:

- **Integer variables are native.** `pb.int(lo, hi)` declares bounds and costs
  nothing per value. A wide domain is not the problem it is under a one-hot
  encoding, so bounds can be generous where the instance warrants it.
- **The objective is a linear expression.** `pb.minimise(terms)` takes the
  expression itself. There is no auxiliary objective variable to build and no
  `link` call to forget.

The objective is declared on the builder, not returned:

```python
    pb.minimise([(cost[i], choice[i]) for i in range(n)])
    return pb, outputs               # still two values
```

Optimality is reported only when Exact proves it. A search that runs out of
budget is a timeout, never an answer, even though Exact has a solution in hand
at that point.

## Rules that break a submission

- **Never write to stdout.** The runner owns it for the JSONL protocol. Use
  `sys.stderr`.
- **Never solve.** No `runFull`, no `toOptimum`. The runner owns the search and
  the budget.
- **Read every instance-dependent quantity from `instance`.**
- Only one file is staged, so there are no helper modules.

## Variables

| Call | Meaning |
| --- | --- |
| `pb.int(lo, hi)` | integer variable on `[lo, hi]` |
| `pb.ints(n, lo, hi)` / `pb.int_grid(r, c, lo, hi)` | several |
| `pb.bool()` / `pb.bools(n)` / `pb.bool_grid(r, c)` | 0/1 variables |
| `pb.constant(v)` | a variable fixed to `v` |
| `pb.negate(flag)` | the complement of a 0/1 variable |

**`pb.bool()` renders as true/false in the declared outputs; `pb.int(0, 1)`
renders as 0 or 1.** The brief says which the problem declares, so pick to
match it.

## Constraints

Linear constraints take `(coefficient, Var)` pairs:

| Call | Meaning |
| --- | --- |
| `pb.le(terms, bound)` / `ge` / `eq` | `sum(coefficient * var)` against a constant |
| `pb.between(terms, low, high)` | both bounds in one constraint |
| `pb.sum_eq(vars, bound)` / `sum_le` / `sum_ge` | unweighted sums |
| `pb.weighted_sum_eq(coeffs, vars, bound)` / `_le` / `_ge` | weighted sums |
| `pb.same(a, b)` | `a == b` |
| `pb.at_most(flags, k)` / `at_least` / `exactly` / `any` | cardinality over 0/1 variables |

Everything that is not linear goes through **channelling**: 0/1 indicators tied
to a variable by `sum(v * y_v) == x` with `sum(y_v) == 1`, built once per
variable on first use.

| Call | Meaning |
| --- | --- |
| `pb.is_value(var, v)` | a 0/1 variable that is 1 exactly when `var == v` |
| `pb.indicators(var)` | the whole `{value: flag}` map |
| `pb.different(a, b)` / `pb.all_different(vars)` | disequality |
| `pb.count(flags, target)` | `target` equals how many flags are 1 |
| `pb.element(index, array, value)` | `array[index] == value`, constant array, **0-based** |

Channelling costs one 0/1 variable per value, so `all_different` over wide
domains is where a model gets expensive. That is the one place to keep domains
tight.

There is no multiplication of two variables, no division and no modulo. Exact
itself has `addMultiplication`, which this layer does not wrap.

## Outputs

Names must be the ones `generation.brief` declares. A leaf may be a `Var`, a
plain `int` or a plain `bool`, nested to any depth.

## Enumeration

With an objective, the runner proves the optimum, pins the objective there, and
then enumerates: each answer is blocked through the indicators of its declared
outputs, so every solution returned is optimal.

## Failure routing

| Result | Usual cause here |
| --- | --- |
| `suboptimal_solution` | The objective expression is not the quantity the reference optimises, or the direction is inverted. |
| `invalid_output` | Wrote to stdout, or used `pb.int(0, 1)` where the brief declares a boolean. |
| `invalid_solution` | A constraint is missing. |
| `execution_timeout` | The optimum could not be proven. Wide domains under `all_different` are the usual cause, because of the channelling. |
| `no_solution` | Overconstrained, or bounds exclude the intended values. |

## Environment

Python 3.12, `exact` 2.2.1. Exact bounds its own search, so the runner passes
the remaining budget to `toOptimum` and `runFull` directly. The container is
networkless, read-only apart from `/tmp`, single-CPU and 2 GiB.

See [the builder's surface](references/dcp-pb-api.md) for every signature.
