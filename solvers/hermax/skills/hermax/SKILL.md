---
name: hermax
description: Write a DCP-Bench submission for the hermax integration - one Python file defining build(instance), using the MaxSat builder from dcp_maxsat to encode the problem into weighted MaxSAT. Use when generating or repairing a model for solver ID hermax.
---

# hermax (MaxSAT) submissions

A submission is one Python file defining:

```python
from dcp_maxsat import MaxSat


def build(instance):
    ...
    return sat, outputs                        # satisfaction
    return sat, outputs, ("minimize", total)   # optimisation
```

`dcp_maxsat` ships inside the image and does the clause encoding, so a
submission states the problem rather than writing CNF.

```python
from dcp_maxsat import MaxSat


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]

    sat = MaxSat()
    take = sat.bools(len(values))
    sat.bool_sum_le(weights, take, capacity)
    profit = sat.int(0, sum(values))
    sat.link_bool_sum(values, take, profit)
    return sat, {"x": take, "profit": profit}, ("maximize", profit)
```

## The objective is a variable, not an expression

A MaxSAT solver minimises the weight of the soft clauses it breaks. It has no
notion of an expression to optimise. So the contract here is:

**Build an integer variable, tie it to the quantity you care about, and hand
that variable over.** The runner turns its one-hot literals into soft units, one
per value, so the cost the solver minimises moves with the variable.

`link_bool_sum(weights, lits, var)` and `link_sum(terms, var)` are how the tie
is made. They are the most important calls in this integration: without one, the
objective variable is free and the answer is meaningless.

```python
    cost = sat.int(0, upper_bound)
    sat.link_bool_sum(prices, chosen, cost)      # cost == sum(prices * chosen)
    return sat, outputs, ("minimize", cost)
```

**Give the objective variable a tight upper bound.** It is one-hot encoded, so
its domain size is its cost in variables and in soft clauses. Derive the bound
from the instance rather than picking a round number.

Optimality is reported only when the solver proves it. A solution found without
that proof is reported as a timeout, never as an answer.

## Rules that break a submission

- **Never write to stdout.** The runner owns it for the JSONL protocol. Use
  `sys.stderr`.
- **Never solve.** The runner owns the search and the budget.
- **Read every instance-dependent quantity from `instance`.**
- Only one file is staged, so there are no helper modules.

## Variables and constraints

Identical to the SAT surface, because the encoding is the same:

| Call | Meaning |
| --- | --- |
| `sat.bool()` / `bools(n)` / `bool_grid(r, c)` | Boolean variables as positive literals |
| `sat.int(lo, hi)` / `int_from(values)` | one-hot integer variable |
| `sat.ints(n, lo, hi)` / `int_grid(r, c, lo, hi)` | several |
| `sat.constant(v)`, `sat.always()`, `sat.never()` | fixed values |
| `sat.clause(lits)`, `implies(a, b)`, `iff(a, b)` | raw logic |
| `sat.at_most(lits, k)` / `at_least` / `exactly` | cardinality |
| `sat.bool_sum_le(weights, lits, bound)` / `_ge` / `_eq` | weighted sums over literals |
| `sat.sum_eq(vars, bound)` / `sum_le` / `sum_ge` | sums of integer variables |
| `sat.weighted_sum_eq(coeffs, vars, bound)` / `_le` / `_ge` | weighted sums of them |
| `sat.linear_eq(terms, bound)` / `_le` / `_ge` | over `(coefficient, IntVar)` pairs |
| `sat.link_bool_sum(weights, lits, var)` | **ties a variable to a weighted sum of literals** |
| `sat.link_sum(terms, var)` | **ties a variable to a linear expression** |
| `sat.link_count(lits, var)` | ties a variable to how many literals are true |
| `sat.same(x, y)` / `different(x, y)` / `all_different(vars)` | relations |
| `sat.is_value(x, v)` | the literal for `x == v` |

An `IntVar` is a direct encoding: `x.literal(v)` is the literal for `x == v`, or
`None` when `v` is outside the domain. Keep domains small; one variable per
value is the cost.

Negative values, negative coefficients and zero coefficients are all handled by
the linear helpers.

There is no multiplication of two variables, no division, no modulo, no element
and no cumulative.

## Outputs

Names must be the ones `generation.brief` declares. A leaf may be an `IntVar`
(renders as an integer), a literal (renders as a boolean), a plain `int` or a
plain `bool`. Where the brief declares the objective value as an output, hand
back the objective variable itself.

## Enumeration

After proving the optimum, the runner blocks the declared outputs and solves
again, keeping only answers at the same cost. Once the best remaining cost rises
above the optimum, the optimal solutions are exhausted and the status is
`complete`.

## Failure routing

| Result | Usual cause here |
| --- | --- |
| `suboptimal_solution` | The objective variable is not tied to the quantity the reference optimises, or the direction is inverted. Check the `link_*` call first. |
| `invalid_output` | Wrote to stdout, or handed back a literal where the brief wants an integer. |
| `invalid_solution` | A constraint is missing. |
| `execution_timeout` | The encoding is too large, or the optimum could not be proven. A wide objective domain is the usual cause. |
| `no_solution` | Overconstrained, or a domain excludes the intended values. |

## Environment

Python 3.12, `hermax` 1.2.5 solving with **EvalMaxSAT**, and `python-sat[pblib]`
1.9.dev15 used only for its cardinality and pseudo-Boolean encoders. No hermax
backend can be time-bounded in process, so the runner supervises the search in a
child process and kills it on budget. The container is networkless, read-only
apart from `/tmp`, single-CPU and 2 GiB.

See [the builder's surface](references/dcp-maxsat-api.md) for every signature.
