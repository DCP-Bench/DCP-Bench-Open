---
name: pysat
description: Write a DCP-Bench submission for the pysat integration - one Python file defining build(instance), using the Sat builder from dcp_sat to encode the problem into CNF for PySAT. Use when generating or repairing a model for solver ID pysat.
---

# PySAT submissions

A submission is one Python file defining:

```python
from dcp_sat import Sat


def build(instance):
    ...
    return sat, outputs
```

`dcp_sat` ships inside the image. It does the encoding a SAT solver needs, so a
submission states the problem rather than writing clauses by hand.

```python
from dcp_sat import Sat


def build(instance):
    n = instance["n"]
    sat = Sat()
    queens = sat.ints(n, 1, n)          # one-hot, exactly-one already posted
    sat.all_different(queens)
    for i in range(n):
        for j in range(i + 1, n):
            for v in range(1, n + 1):
                for w in (v + (j - i), v - (j - i)):
                    other = queens[j].literal(w)
                    if other is not None:
                        sat.clause([-queens[i].literal(v), -other])
    return sat, {"queens": queens}
```

## What this integration cannot do

**There is no objective.** PySAT solves satisfaction problems. A problem whose
reference minimises or maximises is out of scope: return the objective as a
third element and the runner reports `unsupported_capability` rather than
passing off a merely feasible answer as optimal.

```python
    return sat, outputs, ("minimize", cost)   # refused, on purpose
```

Pick satisfaction problems. `python -m generation.brief PROBLEM` prints the
objective direction, and `next_work` will still offer optimisation pairs.

## Rules that break a submission

- **Never write to stdout.** The runner owns it for the JSONL protocol. Use
  `sys.stderr`.
- **Never solve.** No `Solver(...)`, no `solve()`. The runner owns the search
  and the budget.
- **Read every instance-dependent quantity from `instance`.** A model that types
  the example's numbers in is the failure this benchmark exists to catch.
- Only one file is staged, so there are no helper modules. Plain functions in
  the same file are fine.

## Variables

| Call | Meaning |
| --- | --- |
| `sat.bool()` / `sat.bools(n)` / `sat.bool_grid(r, c)` | Boolean variables, returned as positive literals |
| `sat.int(lo, hi)` | integer variable on `[lo, hi]`, one-hot encoded |
| `sat.int_from(values)` | integer variable whose domain is exactly `values` |
| `sat.ints(n, lo, hi)` / `sat.int_grid(r, c, lo, hi)` | several of them |
| `sat.constant(v)` | an integer variable fixed to `v` |
| `sat.always()` / `sat.never()` | a literal fixed true / false |

An `IntVar` is a direct encoding: `x.literal(v)` is the literal meaning `x == v`,
or `None` when `v` is outside the domain. Exactly-one over its values is posted
for you. That is why `x == v` is free to ask for and why iterating values is the
natural way to write a constraint here.

Keep domains small. A one-hot encoding costs one variable per value, so an
integer on `[0, 10000]` is ten thousand variables. Where the reference declares a
wide bound but the instance implies a tight one, derive the tight one.

## Constraints

| Call | Meaning |
| --- | --- |
| `sat.clause(lits)` | at least one literal is true |
| `sat.implies(a, b)` / `sat.iff(a, b)` | implication and equivalence over literals |
| `sat.at_most(lits, k)` / `at_least` / `exactly` | cardinality over literals |
| `sat.bool_sum_le(weights, lits, bound)` / `_ge` / `_eq` | weighted sum over literals |
| `sat.sum_eq(vars, bound)` / `sum_le` / `sum_ge` | sum of integer variables |
| `sat.weighted_sum_eq(coeffs, vars, bound)` / `_le` / `_ge` | weighted sum of integer variables |
| `sat.linear_eq(terms, bound)` / `_le` / `_ge` | the same over explicit `(coefficient, IntVar)` pairs |
| `sat.same(x, y)` / `sat.different(x, y)` | equality and disequality of integer variables |
| `sat.all_different(vars)` | pairwise distinct, encoded value by value |
| `sat.is_value(x, v)` | the literal for `x == v`, fixed false when out of domain |

Negative values, negative coefficients and zero coefficients are all handled:
the linear helpers shift each term to a non-negative weight and move the bound,
because the pypblib encoders want it that way. Verified on a mixed instance with
a `[-5, 5]` domain and coefficients `3` and `-2`.

There is no arithmetic beyond this. No multiplication of two variables, no
division, no modulo, no element, no cumulative. Where the reference needs one,
either express it through the one-hot literals directly — enumerate the values
and post a clause per combination — or pick a different problem.

## Outputs

```python
    return sat, {"queens": queens,      # list of IntVar -> list of ints
                 "chosen": picks,       # list of literals -> list of booleans
                 "grid": rows,          # nested lists work to any depth
                 "n": n}                # a value the instance fixes
```

Names must be the ones `generation.brief` declares. A leaf may be an `IntVar`, a
literal, a plain `int` or a plain `bool`.

**A literal renders as a boolean and an `IntVar` as an integer.** If the brief
declares an integer output, hand back an `IntVar`, not a literal.

## Enumeration

The runner blocks the previous **declared outputs** and solves again, so
consecutive solutions differ where the problem can see it. Two models of the
same CNF routinely agree on every declared output, which is why blocking the
full assignment would not be enough.

## Failure routing

| Result | Usual cause here |
| --- | --- |
| `unsupported_capability` | The submission declared an objective. This integration cannot optimise. |
| `invalid_output` | Wrote to stdout, or handed back a literal where the brief wants an integer. |
| `invalid_solution` | A constraint is missing. Often a one-hot value combination that was never ruled out. |
| `execution_timeout` | The encoding is too large or too weak. Tighten domains first; a one-hot variable per value is the usual culprit. |
| `no_solution` | Overconstrained, or a domain excludes the intended values. |

## Environment

Python 3.12, `python-sat[pblib]` 1.9.dev15, solving with **Glucose 4.2**.
PySAT raises `NotImplementedError` for limited solve on CaDiCaL and Lingeling,
so those cannot be stopped mid-search and are not used here. The container is
networkless, read-only apart from `/tmp`, single-CPU and 2 GiB.

See [the builder's surface](references/dcp-sat-api.md) for every signature.
