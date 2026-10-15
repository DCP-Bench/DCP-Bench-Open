---
name: gurobipy
description: Gurobi's Python API (gurobipy) for linear, integer and binary optimisation models, covering install, variables, linear and indicator constraints, minimise or maximise, reading solutions, and enumerating all or all optimal solutions. Use when writing, debugging or explaining gurobipy models, or when the user has chosen Gurobi from Python for an optimisation or feasibility problem.
license: Apache-2.0
compatibility: Requires Python 3.10+ and pip install gurobipy (tested with gurobipy 13.0.3 on Python 3.12). The pip wheel runs under a size-limited licence without a key (2000 variables and 2000 constraints; 200 variables with quadratic terms); larger models need a Gurobi licence.
metadata:
  domain: constraint-programming
  solver: gurobi
  paradigm: mip
---

# Gurobi (Python, `gurobipy`)

Gurobi solves linear and mixed-integer models by branch-and-cut. Two ideas to keep: every
constraint must be linear (or an indicator, a general constraint, or a product linearised by
hand), and the result is a **status** that must be checked before any value is read.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Runnable examples: `assets/`, one folder per pattern; encodings in [references/encodings.md](references/encodings.md)

## Install

```bash
pip install gurobipy numpy scipy
python3 -c "import gurobipy as gp; print(gp.gurobi.version())"   # (13, 0, 3) when tested
```

The wheel bundles a size-limited licence: no key, no network needed, and a banner
`Restricted license - for non-production use only - expires 2027-11-29` is printed to stdout
when the default environment starts, that is at the first `gp.Model(...)`. Setting
`model.Params.OutputFlag = 0` after the model exists does **not** hide it (verified). To silence
the banner, create the environment with the flag: `env = gp.Env(params={"OutputFlag": 0})`, then
`gp.Model("name", env=env)` (verified: no banner, same status). Above the limits it fails with
`Model too large for size-limited license` (see [Common issues](#common-issues)).
Details: [pip package](https://pypi.org/project/gurobipy/) and
[size-limited licence](https://support.gurobi.com/hc/en-us/articles/360051597492).

## Quick start

```python
import gurobipy as gp
from gurobipy import GRB

model = gp.Model("quick")
x = model.addVar(lb=0, ub=10, vtype=GRB.INTEGER, name="x")
y = model.addVar(lb=0, ub=10, vtype=GRB.INTEGER, name="y")
model.addConstr(x + y >= 7, name="demand")
model.setObjective(3 * x + 2 * y, GRB.MINIMIZE)
model.optimize()

if model.Status == GRB.OPTIMAL:
    print("Objective:", model.ObjVal)
    print("x =", round(x.X), "y =", round(y.X))
else:
    print("Status:", model.Status)
```

Expected output: `Objective: 14.0`, then `x = 0 y = 7`.

## Modelling

Full reference: [Python API](https://docs.gurobi.com/projects/optimizer/en/current/reference/python.html)
([Model](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html),
[global functions](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/func_global.html),
[general constraint helpers](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/func_utility.html)).

| Need | API |
|---|---|
| one variable | [`addVar`](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html): `model.addVar(lb=0, ub=u, vtype=GRB.INTEGER, name="x")` |
| many variables | `model.addVars(n, m, ...)`, indexed `x[i, j]`; `lb` defaults to **0** |
| variables with string keys | `model.addVars(["a", "b", "c"], vtype=GRB.BINARY)`, indexed `x["a"]`; a list of strings is used as the keys directly |
| variables with mixed keys | `model.addVars([("a", 1), ("b", 2)], ...)` or `model.addVars(["r", "s"], [1, 2, 3], ...)` (tuple keys `x["r", 2]`); the keys are the tuples you pass |
| sum over one index | `x.sum(i, "*")` or `x.sum("*", j)` on a tupledict: `*` is a wildcard over that position (verified on string and integer keys); `x.sum()` sums all |
| matrix of variables | `model.addMVar((n, m), vtype=GRB.BINARY)`; `sum` and `@` need SciPy |
| a sum | [`gp.quicksum(...)`](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/func_global.html), faster than `sum()` on many terms |
| a constraint | `model.addConstr(expr <= rhs, name=...)`; also `>=`, `==`; `model.addConstrs(... for ...)` |
| conditional constraint | `model.addConstr((b == 1) >> (x + y <= 3))`, `b` binary: an [indicator](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html) |
| `y = abs(x)` | `model.addConstr(y == gp.abs_(v))`, where `v` is a **variable** |
| `y = max(...)`, `min(...)` | `gp.max_([a, b], constant=0)`, `gp.min_(a, b)`; variables only |
| `z = a and b`, `z = a or b` | `model.addConstr(z == gp.and_(a, b))`, `gp.or_`; binaries only |
| objective | `model.setObjective(expr, GRB.MINIMIZE)` or `GRB.MAXIMIZE`; none means satisfaction |
| negative or free domain | `lb=-5` explicitly, or `lb=-GRB.INFINITY` |
| read a result | `x.X` (value), `model.ObjVal`, `model.Status` |

Encodings for `!=`, all-different, element, disjunctions, products and `//`, `%`:
[references/encodings.md](references/encodings.md).

What raises, in this exact form (gurobipy 13.0.3):

| Code | Error |
|---|---|
| `model.addConstr(x != y)` | `GurobiError: Inequality constraints not supported` |
| `x // 2`, `x % 2` | `TypeError: unsupported operand type(s) for //` |
| `if x == 1:`, `bool(x <= y)` | `GurobiError: Constraint has no bool value`; branch on data, not decisions |
| `gp.abs_(a - b)` | `TypeError: ... is not a variable`; create an auxiliary variable first |
| `x` from model A used in model B | error; each variable belongs to one `Model` |

`x * y` over two variables builds a `QuadExpr`, a quadratic model. Gurobi accepts it, but
it is nonconvex and slower, and the size-limited licence caps it. Linearise when one factor
is binary or has a small range.

## Solving

Status codes: [status reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/numericcodes/statuscodes.html).
Parameters: [parameter reference](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html).

| `model.Status` | Value | Meaning |
|---|---|---|
| `GRB.OPTIMAL` | 2 | optimal (within `MIPGap`); `ObjVal` and `X` are valid |
| `GRB.INFEASIBLE` | 3 | proven to have no solution; use `computeIIS()` to see why |
| `GRB.INF_OR_UNBD` | 4 | infeasible or unbounded; set `DualReductions = 0` and re-solve to tell |
| `GRB.UNBOUNDED` | 5 | objective unbounded; says nothing about feasibility |
| `GRB.TIME_LIMIT` | 9 | stopped at `TimeLimit`; a solution exists only if `model.SolCount > 0` |
| `GRB.SUBOPTIMAL` | 13 | tolerances not met; a suboptimal solution is available |

Parameters you will set: `TimeLimit` (seconds), `Threads`, `Seed`, `MIPGap` (relative gap),
`OutputFlag` (0 silences the log, but for the licence banner create the `Env` with it; see [Install](#install)), `MIPFocus`.

**The default `MIPGap` is 1e-4, not 0.** Gurobi reports `OPTIMAL` when the gap is below it, so a
solution can be reported optimal and still be worse than the true optimum. Set `MIPGap = 0`
when the exact optimum matters. Observed: a 40-item strongly correlated knapsack (weights
`random.Random(3).randint(1, 1000)`, values `w + 100`, capacity `sum(w) // 2`) reports
`OPTIMAL 12950` by default, and `12951` with `MIPGap = 0` (bound 12951).

Errors: Python exceptions (`GurobiError`, `TypeError`) show in the traceback on stderr. A
solver problem is a status, not an exception: always test `model.Status` before reading `.X`.
Log lines go to stdout unless `OutputFlag = 0`.

Read integer variables with `round(x.X)`: values come back within `IntFeasTol` (1e-5) of an integer.

Examples: [satisfy](assets/satisfy/README.md), [maximise](assets/maximise/README.md), [minimise](assets/minimise/README.md),
[infeasible](assets/infeasible/README.md), [scheduling](assets/scheduling/README.md).

## All solutions

Use the solution pool. With `PoolSearchMode = 2` Gurobi keeps up to `PoolSolutions`
solutions; `PoolSolutions` above the number of feasible solutions makes the list exhaustive.
Read each one with `SolutionNumber` (set `model.Params.SolutionNumber = k`) and `Xn`
(the value in that solution; `X` is the current one).

| You want | Settings | Example |
|---|---|---|
| every feasible solution | `setObjective(0)` or no objective, `PoolSearchMode = 2`, `PoolSolutions = 2_000_000_000` | [all-solutions](assets/all-solutions/README.md) |
| every optimal solution | keep the objective, `MIPGap = 0`, `PoolSearchMode = 2`, `PoolGap = 0` | [all-optimal](assets/all-optimal/README.md) |

- Count with `model.SolCount`. The pool is exhaustive only when `SolCount` is **strictly below**
  `PoolSolutions` (and `Status` is `OPTIMAL`). If `SolCount == PoolSolutions`, the list may have
  been cut short: raise `PoolSolutions` and re-run. Verified: with `PoolSolutions = 2` and 3
  feasible solutions, the run still reports `OPTIMAL` and returns only 2. A count equal to the
  cap is not proof of completeness, because a 3-solution model with `PoolSolutions = 3` also
  returns 3.
- Auxiliary variables can make two pool entries differ only in values you do not care about:
  collect the outputs into a `set` of tuples before counting.
- `PoolGap = 0` with a kept objective returns exactly the optimal solutions; verified on a
  4-cycle (two minimum covers) and on "at most 2 of 4 binaries" maximised (6 solutions).

Pool reference: [Solution Pool guide](https://docs.gurobi.com/projects/optimizer/en/13.0/features/solutionpool.html)
and [parameters](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html)
(`PoolSearchMode`, `PoolSolutions`, `PoolGap`).

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `Inequality constraints not supported` | `addConstr(a != b)` | use the `!=` encoding in [encodings.md](references/encodings.md) |
| `Constraint has no bool value` | Python `if` or `bool()` on an expression | Branch on data; express the choice with an indicator |
| `is not a variable` from `abs_`, `max_` | argument is an expression | introduce a variable equal to it, then apply the helper |
| `Model too large for size-limited license` | pip licence limit exceeded | reduce variables or constraints (count them first), or use a full licence |
| `No module named 'scipy'` | `MVar.sum` or `@` used without SciPy | `pip install scipy` |
| `OPTIMAL` but a better solution exists | default `MIPGap` 1e-4 | `model.Params.MIPGap = 0` |
| `INFEASIBLE` on a model you expect feasible | a default `lb=0` hides negative values, or a wrong bound | set `lb` explicitly; `computeIIS()` and `model.write("m.ilp")` to find the conflict |
| `TIME_LIMIT` and no values | nothing found in time | check `SolCount` before reading; raise `TimeLimit`, tighten the formulation |
| solution cut off by a big-M constraint | M too small for the bounds | derive M from variable bounds; prefer indicators ([encodings](references/encodings.md)) |
| enumeration returns duplicates or too few | auxiliary variables; time limit hit | collect output tuples in a `set`; check `Status` is `OPTIMAL` |
| enumeration returns fewer solutions than exist, `Status` still `OPTIMAL` | pool truncated at `PoolSolutions` | `SolCount == PoolSolutions` means possibly cut short: raise `PoolSolutions` (e.g. 2_000_000_000) and re-run |
| licence banner still printed after `model.Params.OutputFlag = 0` | the flag was set after the environment started | `env = gp.Env(params={"OutputFlag": 0})` and `gp.Model(..., env=env)` |
| `KeyError` on `x["a"]` or `x[i, j]` | keys are not the ones you think: `addVars(n)` gives `0..n-1`, string lists give the strings, tuples stay tuples | print `list(x.keys())[:5]` and index with exactly those keys |
| `2.9999999` instead of `3` | integrality tolerance | `round(x.X)` |
| `GurobiError` about a variable from another model | variable reused across `Model`s | create variables in the model that uses them |

## Further reading

- Python API reference: https://docs.gurobi.com/projects/optimizer/en/current/reference/python.html
- Solution pool: https://docs.gurobi.com/projects/optimizer/en/13.0/features/solutionpool.html
- Status codes and parameters: https://docs.gurobi.com/projects/optimizer/en/current/reference/numericcodes/statuscodes.html, https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html
- Gurobi examples (Python): https://docs.gurobi.com/projects/examples/en/current/
- Size-limited licence: https://support.gurobi.com/hc/en-us/articles/360051597492
