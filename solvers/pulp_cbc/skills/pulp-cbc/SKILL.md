---
name: pulp-cbc
description: PuLP 3.x for Python, a modelling library for linear and mixed-integer programs solved by its bundled CBC solver. Use when writing, debugging or explaining PuLP models, when a linear or integer program must be solved in Python with PuLP or CBC, or when enumerating all or all optimal solutions.
license: Apache-2.0
compatibility: Requires Python 3.10+ and PuLP 3.x (tested with 3.3.2, which bundles CBC 2.10.3). PuLP 4.0 is not tested here; its removal of PULP_CBC_CMD is taken from the migration guide (unverified). See Common issues.
metadata:
  domain: constraint-programming
  solver: cbc
  paradigm: mip
---

# PuLP with CBC (Python)

PuLP builds a linear or mixed-integer model in Python and hands it to a solver; the solver bundled with PuLP 3.x is CBC. Keep one idea in mind: **every constraint and the objective must be linear**. PuLP refuses products and quotients of variables, so each non-linear pattern needs a linear encoding ([Encoding the constraints](#encoding-the-constraints)).

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Encoding the constraints](#encoding-the-constraints)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Runnable examples: `assets/`, one folder per pattern

## Install

```bash
pip install "pulp>=3.3,<4"
python3 -c "import pulp; print(pulp.__version__, pulp.PULP_CBC_CMD().available())"
```

The second line prints the version and the path of the bundled `cbc` binary (`3.3.2 /…/cbc`). PuLP 4.0 was published on PyPI on 2026-10-14. It is not installed in the tested image, so its API changes are unverified here; the range stops below 4 until this skill is tested against it. Details: [installing PuLP](https://coin-or.github.io/pulp/main/installing_pulp_at_home.html), [migrating to 4.0](https://coin-or.github.io/pulp/guides/how_to_migrate_to_v4.html) (read, not run).

## Quick start

```python
import pulp

prob = pulp.LpProblem("quick", pulp.LpMaximize)
x = prob.add_variable("x", lowBound=0, upBound=4, cat="Integer")
y = prob.add_variable("y", lowBound=0, upBound=4, cat="Integer")
prob += x + 2 * y <= 7        # a constraint: the expression has a relation
prob += 3 * x + 2 * y         # the objective: a bare expression

status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
if prob.sol_status == pulp.LpSolutionOptimal:
    print("Optimal:", pulp.value(x), pulp.value(y), pulp.value(prob.objective))  # Optimal: 4.0 1.0 14.0
else:
    print("Status:", pulp.LpStatus[status])
```

## Modelling

Full API: [PuLP reference](https://coin-or.github.io/pulp/technical/pulp.html).

| Need | API |
|---|---|
| variable (`cat` is `"Continuous"`, `"Integer"` or `"Binary"`) | [`prob.add_variable(name, lowBound, upBound, cat)`](https://coin-or.github.io/pulp/technical/pulp.html) |
| many variables; nested index sets give nested dicts | [`prob.add_variable_dicts(name, indices, lowBound, upBound, cat)`](https://coin-or.github.io/pulp/technical/pulp.html), then `x[i][j]` |
| sum of terms (linear time) | [`pulp.lpSum(...)`](https://coin-or.github.io/pulp/technical/pulp.html) |
| constraint (`<=`, `>=`, `==`), named | `prob += expr <= rhs, "name"` |
| objective: one bare expression | `prob += expr`, direction from `pulp.LpProblem(name, pulp.LpMaximize)` or `LpMinimize` |
| satisfaction problem | add no objective; `prob.objective` stays `None` |
| multiply by a constant, divide by a constant | `2 * x`, `x / 2` |
| value after solving | `var.varValue` (float), `pulp.value(expr)` |

A `Binary` variable is an `Integer` with bounds 0 and 1. An `Integer` without bounds has `lowBound` and `upBound` of `None`, which enumeration cannot use: bound every integer you need to enumerate.

Non-linear forms are rejected at build time: `x * y`, `x * x`, `abs(x)`, `x / y` and `x % 2` raise `TypeError`. `x != y` is not an error, but it adds nothing to the model: it returns a Python `True`.

## Encoding the constraints

`M` is a constant at least as large as the slack the constraint can need. A larger `M` is always correct but makes CBC slower, so use the smallest value the bounds allow:

- **Rule:** for `left <= right + M*(1-c)`, take `M` at least `max(left - right)` over the variable bounds. Compute it from the bounds, e.g. `M = max(left) - min(right)`.
- **`!=` rule:** when `a, b` are in `0..u`, `a - b` lies in `-u..u`, so `M = u+1` is enough. Example: `a, b` in `0..3` gives `M = 4`.

| Constraint | Linear encoding |
|---|---|
| `a != b`, with `a, b` in `0..u` (so `M = u+1`) | binary `o` (`o = 1` means `a < b`): `a <= b - 1 + (u+1)*(1-o)` and `a >= b + 1 - (u+1)*o` |
| `d = abs(a - b)`, minimised | `d >= a - b` and `d >= b - a` (minimisation pulls `d` down) |
| `c = 1` implies `left <= right` | `left <= right + M*(1-c)`, `M` from the rule above |
| `c = 1` if and only if `x >= 3`, `x` in `0..5` | `x >= 3 - 3*(1-c)` and `x <= 2 + 3*c` |
| `z = a AND b`, binaries | `z <= a`, `z <= b`, `z >= a + b - 1` |
| `v = TABLE[idx]`, `idx` a decision | binaries `ch[j]`: `sum(ch) == 1`, `idx == sum(j*ch[j])`, `v == sum(TABLE[j]*ch[j])` |
| all different `x[0..n-1]` in `1..m` | binaries `p[i][v]`: each row sums to 1, `x[i] == sum(v*p[i][v])`, each value sums to at most 1 |
| disjunction: one of `L_k <= R_k` holds | one binary `b_k` per branch: `L_k <= R_k + M*(1-b_k)`, `sum(b_k) >= 1` |
| no overlap of two jobs on one machine | one binary per pair of jobs: `end[i] <= start[j] + H*(1-o)` and `end[j] <= start[i] + H*o`, `H` the sum of durations |
| job shop: operations of each job in order, machines not shared at once, makespan | start variable per operation; `start[j,k] >= start[j,k-1] + dur[j,k-1]` along each job; one no-overlap binary per pair of operations on the **same** machine (not per pair of jobs); `makespan >= start[j,last] + dur[j,last]`; minimise `makespan` |

Runnable versions: [assets/encodings](assets/encodings/README.md) (`!=`, `abs`, element, reification), [assets/schedule-single-machine](assets/schedule-single-machine/README.md) (disjunction for no-overlap on one machine) and [assets/job-shop-makespan](assets/job-shop-makespan/README.md) (multi-machine job shop with precedence and makespan).

## Solving

Solver options: [configure a solver](https://coin-or.github.io/pulp/guides/how_to_configure_solvers.html). CBC parameters are in [solvers](https://coin-or.github.io/pulp/technical/solvers.html).

`PULP_CBC_CMD(msg=True, timeLimit=None, gapRel=None, gapAbs=None, threads=None, logPath=None, timeMode="elapsed", options=None, warmStart=False, ...)`. `msg=True` (the default) prints CBC's log to stdout; `msg=False` silences it; `logPath` writes the log to a file; `timeMode="cpu"` counts CPU seconds instead of wall-clock seconds.

**Use `msg=False` whenever the script's stdout is parsed or compared** (a grader, a test, or any line-by-line reader): CBC's log lines are written to the same stream. Use `logPath="cbc.log"` if you still want the log.

Two status attributes answer two questions. Read both:

| `pulp.LpStatus[prob.status]` | `prob.status` | Meaning |
|---|---|---|
| `Optimal` | 1 | CBC stopped with a solution. It may still be unproven (see `sol_status`) |
| `Not Solved` | 0 | Not solved, or a time limit ended with no solution |
| `Infeasible` | -1 | proven: no solution |
| `Unbounded` | -2 | the objective is unbounded |

| `prob.sol_status` | Value | Meaning |
|---|---|---|
| `pulp.LpSolutionOptimal` | 1 | optimum proven (or, with no objective, a solution found and proven feasible) |
| `pulp.LpSolutionIntegerFeasible` | 2 | a feasible solution, optimality not proven (time limit) |
| `pulp.LpSolutionNoSolutionFound` | 0 | nothing found within the limits |
| `pulp.LpSolutionInfeasible` | -1 | proven infeasible |
| `pulp.LpSolutionUnbounded` | -2 | unbounded |

Check `prob.sol_status == pulp.LpSolutionOptimal` before you report an optimum. On a 200-item, 10-constraint knapsack with `timeLimit=2`, `LpStatus` read `Optimal` while `sol_status` was `2`.

**Satisfaction problems** (no objective) need three answers, and a time limit must not be reported as a proof of infeasibility:

```python
status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
if prob.sol_status == pulp.LpSolutionOptimal:           # satisfiable: a solution was found
    print("satisfiable")
elif pulp.LpStatus[status] == "Infeasible":             # unsatisfiable: proven
    print("unsatisfiable")
else:                                                   # a limit was hit: no answer
    print("unknown:", pulp.LpStatus[status])
```

Verified with PuLP's bundled CBC: a satisfiable model gives `Optimal` with `sol_status` 1; an unsatisfiable one gives `Infeasible` with `sol_status` -1; a model stopped by a time limit before any solution gives `Not Solved` with `sol_status` 0.

Read values only after a solve that found a solution (`sol_status` 1 or 2). After `Infeasible`, `varValue` and `pulp.value` return numbers that mean nothing. Integer outputs come back as floats (`4.0`), so round them.

Errors: a solver that cannot run raises `pulp.PulpSolverError` from `solve`; `PULP_CBC_CMD` refuses a `path=` argument for this reason (use `COIN_CMD(path=...)` for a custom binary). CBC's own messages appear in the stdout log (`msg=True`) or in `logPath`.

## All solutions

PuLP has no enumeration call. Solve, record the solution, add a **no-good cut** over binary decision variables that excludes it, and repeat until the status is no longer `Optimal`. Runnable: [assets/enumerate-latin-square](assets/enumerate-latin-square/README.md).

```python
# bins: the decision binaries; k: the number of solutions found so far
ones = [b for b in bins if round(b.varValue) == 1]
zeros = [b for b in bins if round(b.varValue) == 0]
prob += pulp.lpSum(1 - b for b in ones) + pulp.lpSum(zeros) >= 1, f"no_good_{k}"
```

| Need | Do |
|---|---|
| all solutions | the loop above; cut over decision binaries only |
| all **optimal** solutions | solve; require `sol_status == LpSolutionOptimal`; read `best = round(pulp.value(score))`; then add the named pin `prob += score == best, "optimum"`, where `score` is the objective kept in a variable (`score = pulp.lpSum(...)`, then `prob += score`), and run the loop. Runnable: [assets/all-optimal-committee](assets/all-optimal-committee/README.md) |
| no duplicates | auxiliary variables (flags, indicators) must not be in the cut; two solutions count as the same when their decision values match |
| integer decisions, not binary | encode each value with binaries first; a cut over raw integers is not linear |

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `TypeError: Non-constant expressions cannot be multiplied` | `x * y`, `x * x` | encode the product ([table](#encoding-the-constraints)) |
| `TypeError: bad operand type for abs()` | `abs(var)` | `d >= a - b`, `d >= b - a` with a minimisation |
| `TypeError` on `/` or `%` between variables | `x / y`, `x % 2` | encode, or use a constant divisor (`x / 2` is fine) |
| A `!=` constraint is missing, with no error | `p += x != y` adds nothing: `!=` returns a Python `True` | use the `!=` encoding |
| `UserWarning: Overwriting previously set objective` | two bare expressions added | build one objective expression |
| Output parser fails, or sees CBC log lines in the answer | `msg=True` is the default and prints CBC's log to stdout | pass `msg=False` whenever stdout is parsed; use `logPath` for the log |
| `Optimal` status, but the answer is not the optimum | time limit reached; `sol_status` is 2 | check `sol_status`; tighten the formulation or raise `timeLimit` |
| "Unsatisfiable" printed on a run that hit a time limit | `Not Solved` is not a proof of infeasibility | print "unsatisfiable" only for `LpStatus == "Infeasible"`; see the [satisfaction snippet](#solving) |
| `Not Solved`, no values after a time limit | no incumbent found in time | tighten the formulation, reduce big-M, or give more time |
| Garbage values after `Infeasible` | values are not defined | read values only when `sol_status` is 1 or 2 |
| `Unbounded` | a variable with no bound drives the objective | add upper bounds from the data |
| `DeprecationWarning`: `LpVariable(...)`, `LpVariable.dicts`, `constraints` as dict | PuLP 3.3.2 deprecates these | use `add_variable`, `add_variable_dicts` and `prob.constraints()`, as in this skill |
| `x[i, j]` raises `KeyError` | nested index sets give nested dicts | write `x[i][j]` |
| `PulpSolverError` mentioning `cbc` with `COIN_CMD` | `COIN_CMD` looks for `cbc` on `PATH`, not the bundled binary | use `PULP_CBC_CMD()` |
| `PulpSolverError: Use COIN_CMD if you want to set a path` | `PULP_CBC_CMD(path=...)` | use `COIN_CMD(path=...)` for a custom `cbc` binary |
| `PULP_CBC_CMD` not found after upgrading to PuLP 4.0 | PuLP 4.0 removed it and no longer bundles CBC (from the migration guide, not run here) | pin `pulp<4`, or follow the [4.0 migration guide](https://coin-or.github.io/pulp/guides/how_to_migrate_to_v4.html) |
| Long model builds slowly | `sum(...)` over long lists is quadratic (0.28 s for 3,000 terms, against 0.001 s for `lpSum`) | use `pulp.lpSum` |
| Wrong solutions, or none, after a disjunction or `!=` | big-M too small, so an inactive branch cuts off solutions | take `M` from the bounds: `max(left - right)`; for `!=` with `0..u`, `M = u+1` |
| Job shop schedule overlaps on a machine, or precedence broken | no-overlap binaries written per pair of jobs, or missing along a job's chain | one binary per pair of operations on the same machine; `start[j,k] >= start[j,k-1] + dur` for each job ([assets/job-shop-makespan](assets/job-shop-makespan/README.md)) |
| Enumeration never ends | an unbounded integer, or cuts over auxiliary variables | bound all integers; cut only over decision binaries |

## Further reading

- Documentation: [PuLP user guide](https://coin-or.github.io/pulp/) (no `llms.txt` is published)
- API reference: [PuLP technical reference](https://coin-or.github.io/pulp/technical/pulp.html), [solvers](https://coin-or.github.io/pulp/technical/solvers.html)
- Guides: [configure a solver](https://coin-or.github.io/pulp/guides/how_to_configure_solvers.html), [debug](https://coin-or.github.io/pulp/guides/how_to_debug.html), [warm start](https://coin-or.github.io/pulp/guides/how_to_mip_start.html), [migrate to 4.0](https://coin-or.github.io/pulp/guides/how_to_migrate_to_v4.html)
- Examples: [set partitioning](https://coin-or.github.io/pulp/CaseStudies/a_set_partitioning_problem.html) and [sudoku](https://coin-or.github.io/pulp/CaseStudies/a_sudoku_problem.html) case studies; runnable patterns in `assets/`
