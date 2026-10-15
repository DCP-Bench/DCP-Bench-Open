---
name: docplex
description: DOcplex (docplex.mp), the Python modelling API of IBM CPLEX, for mixed-integer linear models with integer, binary and continuous variables, linear, indicator and logical constraints, optimisation and enumeration of solutions. Use when writing, debugging or explaining a model with docplex or CPLEX in Python, or when a problem such as assignment, scheduling, packing or selection should be modelled with docplex.
license: Apache-2.0
compatibility: Requires Python 3 with the docplex and cplex packages (tested with docplex 2.32.264, cplex 22.2.0.1, Python 3.12). The pip cplex package is the CPLEX Community Edition, limited to 1000 variables and 1000 constraints per model; no key or network is needed
metadata:
  domain: constraint-programming
  solver: CPLEX
  paradigm: mip
---

# DOcplex (Python, CPLEX)

DOcplex is the Python modelling API of IBM CPLEX. You build a `docplex.mp` `Model` from
variables and constraints, then `solve()` hands it to CPLEX, which proves optimality for
mixed-integer programs. The one idea to keep: the model must be **linear**. A product of two
variables, a division or a remainder of a variable is refused by CPLEX or by Python, and
[encodings](references/encodings.md) show the linear forms that do the same job.

This skill covers the `docplex.mp` modelling API. It does not cover the native `cplex` Python
API, the C++ or Java APIs, or CP Optimizer (`docplex.cp`).

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Program shape](#program-shape)
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Speed](#speed)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Runnable examples: `assets/`, one folder per pattern, each with a README and `model.py`

## Install

```bash
pip install docplex cplex
python3 -c "from docplex.mp.model import Model; m = Model(); x = m.integer_var(0, 3); m.maximize(x); print(m.solve().objective_value)"
```

The second command prints `3.0`. The PyPI `cplex` package is the **Community Edition**: no key,
but at most 1000 variables and 1000 constraints per model (indicators count as constraints); more
raises `DOcplexLimitsExceeded` (code 1016). A licensed CPLEX installation lifts this; its setup is outside
this skill. Details: [getting started](https://ibmdecisionoptimization.github.io/docplex-doc/getting_started_python.html).

Tested with Python 3.12, docplex 2.32.264 and cplex 22.2.0.0.

## Quick start

```python
from docplex.mp.model import Model

m = Model(name="quick")
x = m.integer_var(0, 10, name="x")
y = m.integer_var(0, 10, name="y")
m.add_constraint(x + 2 * y >= 8, ctname="cover")
m.minimize(3 * x + 2 * y)

sol = m.solve()
if sol is None:
    print("no solution:", m.solve_details.status)
else:
    print(m.solve_details.status, sol.objective_value, sol[x], sol[y])
```

Prints `integer optimal solution 8.0 0 4.0`. Run it as `python3 quick.py`.

## Program shape

A model is usually a script that reads its data, solves, and prints the answer. When a harness
runs the script with the instance file as `sys.argv[1]` and reads one JSON object per line from
stdout, this is the shape to write. The examples in `assets/` do not print JSON; see below. The output lines are fixed by that
harness; DOcplex does not define them:

```python
import json
import sys

from docplex.mp.model import Model

with open(sys.argv[1]) as f:                  # the instance path is the only argument
    data = json.load(f)
weights, values, capacity = data["weights"], data["values"], data["capacity"]

m = Model(name="knapsack")
m.parameters.mip.tolerances.mipgap = 0        # exact optimum, see Solving
take = m.binary_var_list(len(weights), name="take")
m.add_constraint(m.scal_prod(take, weights) <= capacity, ctname="capacity")
m.maximize(m.scal_prod(take, values))

sol = m.solve()
status = m.solve_details.status
if sol is None:
    if status == "integer infeasible":
        print(json.dumps({"status": "unsatisfiable"}))   # proven infeasible
    else:
        raise SystemExit(f"no answer: {status}")         # never print a guess
elif status != "integer optimal solution":
    raise SystemExit(f"optimum not proven: {status}")
else:
    print(json.dumps({"take": [round(sol[t]) for t in take]}))
```

Three rules this shape follows:

- Read the status string after `solve()`, never only `None`. `None` covers infeasible, unbounded
  and stopped-without-a-solution.
- Print only a solution whose status is `integer optimal solution`. A feasible model with no
  objective also reports that status, so one check covers optimisation and satisfaction.
- Exit non-zero (`SystemExit` with a message) for every other case, so no guess is printed.

The examples in `assets/` print plain text for a reader. The line shape above is what a harness
needs. [Product mix](assets/product-mix/model.py) and [set cover](assets/set-cover/model.py) show
the optimisation side, and [infeasible staffing](assets/infeasible-staffing/model.py) shows reading
the infeasible status without an exception.

## Modelling

Full API: [`Model`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html)

| Need | API |
|---|---|
| integer variable | [`integer_var(lb, ub, name=)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.integer_var); `lb` defaults to 0, `ub` to `m.infinity` (1e20) |
| binary, continuous | [`binary_var(name=)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.binary_var), [`continuous_var(lb, ub)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.continuous_var) |
| lists of variables | [`integer_var_list(n, lb, ub)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.integer_var_list), [`binary_var_list(n)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.binary_var_list) |
| indexed variables | [`binary_var_matrix(rows, cols)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.binary_var_matrix) and [`binary_var_dict(keys)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.binary_var_dict): dicts keyed by tuples or names |
| sums | [`m.sum(...)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.sum); [`m.scal_prod(vars, coefs)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.scal_prod) for weighted sums |
| constraint | [`m.add_constraint(e <= f, ctname=)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.add_constraint); many at once: [`add_constraints(list)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.add_constraints) |
| not equal | `m.add_constraint(a != b)` |
| minimise / maximise | [`m.minimize(e)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.minimize), [`m.maximize(e)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.maximize) |
| indicator: `c == 1` forces a constraint | [`add_indicator(c, e <= f)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.add_indicator); `active_value=0` for `c == 0` |
| reified equality | [`add_equivalence(c, a == b)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.add_equivalence) |
| constraint implies constraint | [`add_if_then(e <= f, g == h)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.add_if_then) |
| absolute value, max, min | [`m.abs(e)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.abs), [`m.max(a, b)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.max), [`m.min(a, b)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.min), used as `m.add(d == m.abs(e))` |
| and, or of binaries | [`m.logical_and(a, b)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.logical_and), [`m.logical_or(a, b)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.logical_or), used as `m.add(z == ...)` |

Patterns the table does not show (all-different, element, counting, binary times integer,
division, disjunctions): [references/encodings.md](references/encodings.md). Each block there
is a complete fragment that defines its own variables.

**Helper cost.** Each helper adds variables and constraints of its own, which count against
the Community Edition limit. Measured on integer variables in 0..9, counting the result
variable or indicator binary that the helper is posted with:

| Posting | Adds variables | Adds constraints |
|---|---|---|
| `m.add_constraint(a != b)` | 1 | 2 |
| `m.add(d == m.abs(a - b))` | 5 | 4 |
| `m.add(y == m.max(a, b))` | 4 | 6 |
| `m.add_equivalence(c, a == b)` | 1 | 1 |
| `m.add_indicator(c, a <= b)` | 1 | 1 |
| `m.add_if_then(a >= 3, b == 0)` | 1 | 2 |

Helpers posted once per pair of items multiply quickly; an assignment matrix is often smaller.

Read sizes and coefficients from your data, not from one example. Python can branch on data
only: `if x == 1:` raises `TypeError`, because `x == 1` is a constraint.

## Solving

Status values: [`solve_details`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.solve_details). `solve()` returns a solution object, or `None` when there is no solution to report.
The strings below are the exact values of `m.solve_details.status`, as measured.

| `solve_details.status` | code | `solve()` returns | Meaning |
|---|---|---|---|
| `integer optimal solution` | 101 | solution | proven optimal (or, with no objective, feasible) |
| `integer optimal, tolerance` | 102 | solution | optimal within `mipgap`; not exact, see [Common issues](#common-issues) |
| `time limit exceeded` | 107 | solution | stopped by the time limit with an incumbent; not proven optimal; check `m.solve_details.mip_relative_gap` |
| `time limit exceeded, no integer solution` | 107 | `None` | stopped by the time limit before any solution was found |
| `integer infeasible` | 103 | `None` | proven: no solution |
| `integer unbounded` | 118 | `None` | the objective is unbounded |
| `integer infeasible or unbounded` | 119 | `None` | presolve could not tell which; see [Common issues](#common-issues) |
| `Non-convex QCP` | | `None` | CPLEX refused a product of variables; its message is printed to stdout |
| `populate solution limit exceeded` | | pool | `populate()` stopped at `mip.limits.populate`; see [All solutions](#all-solutions) |

Accept a result as an answer only when its status is `integer optimal solution`. Any other
status means that the value may be a guess, so a script exits non-zero instead of printing it:

```python
if m.solve_details.status != "integer optimal solution":
    raise SystemExit(f"not proven optimal: {m.solve_details.status}")
```

Reading values: `sol[x]`, `sol.get_value(x)` or `x.solution_value`; `sol.get_value(expr)` for an
expression; `sol.objective_value`. Integer values come back as near-integer floats: round them.

Parameters are set on the model, before `solve()`:

| Setting | Call | Note |
|---|---|---|
| time limit | [`m.set_time_limit(seconds)`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html#docplex.mp.model.Model.set_time_limit) | values under 1 second are raised to 1 with a warning |
| relative gap | `m.parameters.mip.tolerances.mipgap = 0` | default 1e-4; 0 proves the exact optimum |
| threads | `m.parameters.threads = 1` | default is chosen by CPLEX |
| random seed | `m.parameters.randomseed = 42` | |
| presolve | `m.parameters.preprocessing.presolve = 0` | 0 turns presolve off |
| solver log | `m.solve(log_output=True)` | prints the CPLEX log |

Errors: Python raises while the model is built (`TypeError`) or solved (`DOcplexLimitsExceeded`).
CPLEX refusals such as `Model has non-convex quadratic constraint` are printed, and `solve()` returns `None`
with the status `Non-convex QCP`. A script that must not print a guess treats `None` with any status
other than `integer infeasible` as a failure, as in the [program shape](#program-shape).

## All solutions

DOcplex has no separate call to list every solution, but `populate()` fills a solution
pool, and a loop of no-good cuts works without any pool settings. Both are complete for
integer and binary decision variables.

**Solution pool** (use this for more than a few dozen solutions; see [Speed](#speed)):

```python
m.parameters.mip.pool.intensity = 4       # enumerate all solutions
m.parameters.mip.pool.relgap = 1e75       # 1e75 = every feasible solution; 0 = optimal only
m.parameters.mip.pool.absgap = 1e75
m.parameters.mip.limits.populate = 1000000  # the default is 20 and stops early
pool = m.populate()                       # None if no solution
for s in pool:
    values = [round(s[t]) for t in take]
```

The status reads `all reachable solutions enumerated, integer optimal` when the pool is complete.
It reads `populate solution limit exceeded` when a limit stopped it: with the default limit of 20,
the 92 solutions of 8-queens stopped at 24 with that status, so raise `mip.limits.populate` first.
Auxiliary variables multiply solutions: two assignments that differ only in an auxiliary variable
count twice, so enumerate over decision variables and drop duplicates.

**No-good loop** ([example](assets/subset-sum-all/model.py)). Solve, read the decisions, forbid that
assignment, repeat until `solve()` returns `None`. It needs no pool settings, but it solves one
MIP per solution, so it is slow for many solutions. Use it for a few solutions or as a fallback:

```python
found = []
while True:
    sol = m.solve()
    if sol is None:
        break                      # m.solve_details.status: 'integer infeasible' means exhausted
    values = [round(sol[t]) for t in take]
    found.append(values)
    m.add_constraint(m.sum(1 - take[i] for i in range(n) if values[i] == 1)
                     + m.sum(take[i] for i in range(n) if values[i] == 0) >= 1)
```

A loop that ends with `None` and a status other than `integer infeasible` is incomplete. Raise an
error in that case rather than reporting the list as complete.

**All optimal solutions** ([example](assets/assignment-all-optimal/model.py)). Solve for the
optimum, post `cost == optimum` as a constraint, then enumerate as above. With the pool,
set `relgap` and `absgap` to 0 instead, and the pool holds only optimal solutions.

## Speed

Measured on one CPU, wall time of the whole script (Python start-up, model build, all solves),
on the instances of the add-solver toy problems:

| Script | Instance | Time |
|---|---|---|
| cryptarithm | send-more-money, two-two-four, ab-ab-aaa (infeasible) | 0.1 to 0.6 s each |
| graph-colouring | cycle6, k4-tail, petersen | 0.1 to 0.5 s each |
| knapsack | small (5 items), p01 (10 items) | 0.1 s each |
| jobshop, indicator encoding | small (3 jobs), ft06 (6 jobs by 6 machines) | 1.0 s, 0.5 s |
| n-queens, one solution | n3, n4, n8 | 0.1 s each |
| n-queens-all, no-good loop | n8, 92 solutions | 21 s |
| n-queens-all, `populate()` alone | n8, 92 solutions | 0.7 s |

The job shop timings are for those two instances only. The skill makes no claim about larger job
shops: time one on your data before relying on this encoding. When a time limit is set, a run that
hits it may return a solution that is not proven optimal, so check the status (see [Solving](#solving)).

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `TypeError: Cannot convert linear constraint to a boolean value` | `if x == 1:` or `bool(...)` on a constraint | branch on data, or use `add_indicator` |
| `TypeError: unsupported operand type(s) for //` or `%` | integer division or remainder of a variable | `a == k*q + r` with integer `q`, `r`; see [encodings](references/encodings.md) |
| `Model has non-convex quadratic constraint`, status `Non-convex QCP` | product of two variables | a binary times a bounded integer has a linear form in [encodings](references/encodings.md) |
| `DOcplexLimitsExceeded`, `CPLEX code=1016` | Community Edition limit of 1000 variables or constraints | reduce the formulation; enumeration adds rows of its own |
| status `integer optimal, tolerance` (102), maximum below the true optimum | default `mipgap` 1e-4. Measured: a 40-item knapsack (weights random 1..1000 with seed 27, values weight + 100, capacity half the total weight) gave 12860 with status 102 by default and 12861 with status 101 at `mipgap = 0` | set `m.parameters.mip.tolerances.mipgap = 0` before `solve()` |
| status `integer infeasible or unbounded` (119) | presolve cannot decide | `m.parameters.preprocessing.presolve = 0` and solve again: gives 103 or 118 |
| `has_objective()` is true after `m.minimize(5)` | any expression is an objective, even a constant | only no call, or `minimize(0)`, leaves a satisfaction model |
| `solve()` returns `None` | infeasible, unbounded, time limit with no solution, or refused by CPLEX | read `m.solve_details.status`, not only `None`; exit non-zero unless it is `integer infeasible` |
| script prints a solution although the status is `time limit exceeded` or `integer optimal, tolerance` | the answer is not proven optimal | print only on `integer optimal solution`; raise the time limit or accept the gap explicitly |
| `time limit exceeded, no integer solution`, `solve()` returns `None` | the limit ran out before the first solution | raise `set_time_limit`, or tighten the formulation |
| enumeration takes tens of seconds for a few dozen solutions | the no-good loop solves one MIP per solution | use the solution pool; see [Speed](#speed) |
| `populate()` returns about 20 solutions, status `populate solution limit exceeded` | `mip.limits.populate` is at its default of 20 | set `m.parameters.mip.limits.populate` to a larger value |
| `Time limit too small: 0.5 - using 1 instead` | `set_time_limit` below one second | use at least 1 |
| `integer_var(0, name=)` has upper bound `1e20` | the default upper bound is `m.infinity` | give bounds explicitly |
| `binary_var_matrix` loop gives keys, not variables | it returns a dict keyed by `(i, j)` | index with `x[i, j]`, or build lists: `[[x[i, j] for j in cols] for i in rows]` |
| enumeration reports the same assignment twice | auxiliary variables differ between solutions | enumerate over decision variables only, or de-duplicate them |
| a loose big-M lets a binary at 0 carry `M` x 1e-5 through a constraint | integrality tolerance 1e-5 | derive M from the data bounds, or use indicators |
| `1.99999` instead of `2` | integer values are within the integrality tolerance (1e-5) | `round()` every integer value you read |
| `NameError` when a snippet from [encodings](references/encodings.md) is pasted alone | the snippet is a fragment that expects `m` and its own variables | paste it after the preamble at the top of that file |
| `ModuleNotFoundError: docplex` or `cplex` | the packages are not installed | run the [install](#install) step in the environment that runs the model |

## Further reading

- Documentation for agents: no `llms.txt` is published (checked: 404); start from the API reference.
- API reference: [`Model`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html), [`Solution`](https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.solution.html)
- Modelling guide: [docplex.mp index](https://ibmdecisionoptimization.github.io/docplex-doc/mp/index.html)
- Examples: [docplex-examples `examples/mp`](https://github.com/IBMDecisionOptimization/docplex-examples/tree/master/examples/mp)
