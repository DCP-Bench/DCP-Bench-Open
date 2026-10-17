---
name: mip-python
description: Python-MIP (import mip), a Python library for linear and mixed-integer programs, solved by its default solver CBC. Use when writing, debugging or explaining Python-MIP models, when a linear or integer program must be solved in Python with mip or CBC, when a logical or combinatorial constraint needs binaries and big-M encodings, or when enumerating all or all optimal solutions.
license: Apache-2.0
compatibility: Requires Python 3.10+ and mip (tested with 2.0.0, which installs cbcbox for CBC). No licence limits for CBC. Gurobi is used only if gurobipy is installed.
metadata:
  domain: constraint-programming
  solver: cbc
  paradigm: mip
---

# Python-MIP with CBC (Python)

Python-MIP builds a mixed-integer linear model in Python and solves it with CBC. Keep one idea in mind: **every constraint and the objective must be linear**. Products of variables, `abs`, `min`, `max` and `!=` need the encodings in [Encoding the constraints](#encoding-the-constraints).

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Encoding the constraints](#encoding-the-constraints)
- [Numbers](#numbers)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Runnable examples: [knapsack](assets/knapsack/README.md), [all-optimal-committee](assets/all-optimal-committee/README.md), [n-queens-all](assets/n-queens-all/README.md), [latin-square](assets/latin-square/README.md), [cryptarithm](assets/cryptarithm/README.md), [single-machine-schedule](assets/single-machine-schedule/README.md), [encodings](assets/encodings/README.md), [graph-colouring](assets/graph-colouring/README.md), [status-check](assets/status-check/README.md)

## Install

```bash
pip install mip
python3 -c "import mip; print(mip.__version__)"
```

Tested with `mip` 2.0.0 (which installs `cbcbox` 2.935, the CBC solver: `CBC devel (git:146ce89)`). Pin `mip==2.0.0` when results must reproduce. `mip.Model()` picks Gurobi when Gurobi (`gurobipy`) is installed and CBC otherwise, so pass `solver_name="CBC"` explicitly. Details: [Python-MIP site](https://www.python-mip.com).

## Quick start

```python
# Tiny integer program: choose whole numbers x and y in 0..4 to maximise 3x + 2y
# under x + 2y <= 7. Prints the proven optimum.
import mip

m = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")
m.verbose = 0                        # without this CBC's log goes to stdout
m.max_mip_gap = 0.0                  # OPTIMAL means proven, not within 0.01 %
m.max_mip_gap_abs = 0.0
x = m.add_var("x", lb=0, ub=4, var_type=mip.INTEGER)
y = m.add_var("y", lb=0, ub=4, var_type=mip.INTEGER)
# the capacity constraint
m += x + 2 * y <= 7
# the objective
m.objective = 3 * x + 2 * y
if m.optimize(max_seconds=10) == mip.OptimizationStatus.OPTIMAL:
    print("Optimal:", round(x.x), round(y.x), round(m.objective_value))
```

## Modelling

Full reference: [classes](https://python-mip.readthedocs.io/en/latest/classes.html).

| Need | API |
|---|---|
| variable; `var_type` is `mip.BINARY`, `mip.INTEGER` or `mip.CONTINUOUS` (default) | [`m.add_var(name, lb, ub, obj, var_type)`](https://python-mip.readthedocs.io/en/latest/classes.html) |
| many terms | [`mip.xsum(terms)`](https://python-mip.readthedocs.io/en/latest/classes.html) (Python's `sum` also builds an expression) |
| constraint with `<=`, `>=` or `==` | `m += expr <= rhs` or [`m.add_constr(expr, name)`](https://python-mip.readthedocs.io/en/latest/classes.html) |
| objective (a bare `m += expr` raises `TypeError`) | `m.objective = expr`; direction from `mip.Model(sense=mip.MAXIMIZE)` (default `MINIMIZE`) |
| constant in the objective | `expr + 5`; `m.objective_const` reports it and `objective_value` includes it |
| value after solving | `v.x` and `expr.x` (float, or `None` without a solution), `m.objective_value`, `m.objective_bound`, `m.gap` |
| variable by name, bounds, type | `m.var_by_name("x")`, `v.lb`, `v.ub`, `v.var_type` |

Syntax facts, all checked by running:
- `x * y`, `x * x`, `abs(x)` raise `TypeError`. Multiply by a number only (`2 * x`, `x / 2`).
- `x == 3` gives an expression object, which is always true in an `if`. Use `==` only inside `m += ...`, and compare values with `v.x` after solving.
- `m += 2 <= 3` raises `TypeError`: a constraint needs a variable.

## Encoding the constraints

`M` is a constant at least as large as the most the expression can exceed its bound. Compute it from the data: `M = max(L - R)` over the variable bounds. Too small an `M` cuts off solutions silently; a larger valid `M` only weakens the relaxation. Give every integer variable finite bounds from the data (`ub=`).

| Constraint | Linear form (`b`, `c`, `s`, `p`, `q` are binaries) |
|---|---|
| `x != v`, `x` integer in `lo..hi`, one binary `b` (`b = 1` means `x > v`) | `x <= v - 1 + (hi - v + 1) * b` and `x >= v + 1 - (v + 1 - lo) * (1 - b)` |
| `c = 1` implies `L <= R` | `L <= R + M * (1 - c)` |
| `c = 1` if and only if `x >= t`, `x` in `lo..hi` | `x >= t - (t - lo) * (1 - c)` and `x <= (t - 1) + (hi - t + 1) * c` ([example](assets/encodings/README.md)) |
| `d = abs(a - b)`, minimised | `d >= a - b`, `d >= b - a` |
| `d = abs(a - b)`, maximised | binary `s`: `d <= a - b + M * (1 - s)`, `d <= b - a + M * s` |
| `z = min(x, y)`, exact | binary `s`: `z <= x`, `z <= y`, `z >= x - M * (1 - s)`, `z >= y - M * s` |
| `z = max(x, y)`, exact | binary `s`: `z >= x`, `z >= y`, `z <= x + M * (1 - s)`, `z <= y + M * s` |
| `min` maximised, or `max` minimised (no binary needed) | `z <= x`, `z <= y` (or `z >= x`, `z >= y`) |
| `z = p * q`, binaries | `z <= p`, `z <= q`, `z >= p + q - 1` |
| `w = b * x`, `x` integer in `lo..hi` | `w <= hi * b`, `w >= lo * b`, `w <= x - lo * (1 - b)`, `w >= x - hi * (1 - b)` |
| `x` takes one value of `{v1, ..., vk}` | binaries `p[j]`: `sum p[j] == 1`, `x == sum vj * p[j]` |
| all different `x_0..x_{n-1}` with values in a set `V` (for example `range(lo, lo + k)`, or any list) | `p[i][v]` binary for `v` in `V`: `sum_v p[i][v] == 1`, `x_i == sum_v v * p[i][v]`, `sum_i p[i][v] <= 1` for each `v`. Values are the actual numbers, so an offset needs no change. Needs `k = len(V) >= n`, otherwise infeasible |
| `x < v` on integers | `x <= v - 1` (and `x > v` is `x >= v + 1`) |
| either `L1 <= R1` or `L2 <= R2` | binaries `b1 + b2 >= 1`, `L1 <= R1 + M1 * (1 - b1)`, `L2 <= R2 + M2 * (1 - b2)` |
| two jobs do not overlap on one machine | binary `o`: `s_j >= s_i + d_i - H * (1 - o)`, `s_i >= s_j + d_j - H * o`. `H` = sum of all durations, and bound each start by `s_i <= H - d_i` (valid without release dates, because some optimal schedule is left-justified). With release dates `r_i`, use `H` = latest release + sum of durations and `r_i <= s_i <= H - d_i` |
| `v = T[idx]` for a table `T` | binaries `ch[k]`: `sum ch[k] == 1`, `idx == sum k * ch[k]`, `v == sum T[k] * ch[k]` |

Worked code: [encodings](assets/encodings/README.md), [single-machine-schedule](assets/single-machine-schedule/README.md) (no overlap, big-M from data), [latin-square](assets/latin-square/README.md) (all different with binaries), [graph-colouring](assets/graph-colouring/README.md).

## Numbers

- Solution values are floats: `5.0`, not `5`. Round them (`round(v.x)`) before comparing or printing. A value can sit up to `m.integer_tol` (1e-6 by default) from an integer, and an expression over continuous variables can drift a little further.
- Keep an integer output an integer variable: `z = m.add_var(var_type=mip.INTEGER)` with `z == sum(w_i * b_i)` (unit or integer coefficients). The integer variable then comes back as a whole number.
- Coefficients up to 1e9 with integer outputs up to 2.5e10 gave exact integer values in tests (60 binaries). Larger magnitudes were not tested.

## Solving

`m.optimize(max_seconds=...)` returns an `mip.OptimizationStatus`. Read the status before any value.

| Status | Meaning |
|---|---|
| `OPTIMAL` | a solution, proven optimal when `max_mip_gap` is 0 |
| `INFEASIBLE` | proven: no solution (CBC also reports this when the relaxation is feasible but no integer point exists) |
| `UNBOUNDED` | the objective has no bound |
| `FEASIBLE` | a solution, optimality not proven (time limit reached) |
| `NO_SOLUTION_FOUND` | time limit reached with no solution: nothing is known |
| `OTHER` | the model has no variables, so nothing was solved |

Reference: [`OptimizationStatus`](https://python-mip.readthedocs.io/en/latest/classes.html). Without a solution, `v.x` is `None`.

A satisfaction model (no objective) may leave `m.objective` unset, or set it to 0. Then `m.optimize()` returns `OPTIMAL` when a feasible point exists (`m.objective_value` is 0.0) and `INFEASIBLE` when none does. Checked with CBC 2.935.

Settings that matter (defaults from the package source, `mip/model.py`):

| Setting | Default | Note |
|---|---|---|
| `m.max_mip_gap` | `1e-4` | relative gap at which CBC stops. Set `0.0`. In a test at the default, CBC returned `OPTIMAL` with value 195,360,778 and gap 4.5e-5; the same model with gap 0 found 195,369,517 |
| `m.max_mip_gap_abs` | `1e-10` | absolute gap at which CBC stops. Set `0.0` with the line above |
| `m.verbose` | `1` | CBC's log goes to stdout. Set `0` |
| `m.threads` | `0` | solver default. `1` for reproducible runs |
| `m.integer_tol`, `m.infeas_tol`, `m.opt_tol` | `1e-6` each | tolerances; leave them unless a model needs otherwise |
| `m.seed` | `0` | random seed for CBC's tie-breaks |
| `optimize(max_seconds=...)` | no limit | time limit in seconds for that solve |

With the default `verbose = 1` the package prints a solver banner and CBC's log to stdout. A program that prints its own answer sets `m.verbose = 0` before `optimize`.

Errors in building the model are Python exceptions at build time. A solver failure shows as status `ERROR`, which none of the tests with CBC produced. A model with no variables returns `OTHER` and logs `Model has no variables`.

## All solutions

No solution pool to rely on: `m.num_solutions` and `v.xi(k)` exist, but on a tie of four binaries the pool held one solution. Enumerate with no-good cuts instead ([n-queens-all](assets/n-queens-all/README.md)):

```python
# Count every 0/1 assignment of decision binaries that satisfies the model.
# After each solution, a no-good cut over the decision binaries forbids it.
placements = []
while m.optimize(max_seconds=60) == mip.OptimizationStatus.OPTIMAL:
    values = [round(b.x) for b in decisions]
    placements.append(values)
    m += mip.xsum((1 - b) if v == 1 else b for b, v in zip(decisions, values)) >= 1
```

The loop itself prints nothing. With zero solutions the first `optimize` returns `INFEASIBLE`, the loop body never runs and `placements` is empty, so a count of 0 is printed. With exactly one solution the count is 1. Check `placements` before indexing it. Any printing format works ([n-queens-all](assets/n-queens-all/README.md) prints a plain list).

- Cut only over the variables that define the answer. An auxiliary variable in the cut gives duplicate answers.
- Integer decisions need binaries before a cut (one-hot per value), or two binaries per variable (below and above the current value) with finite bounds.
- All **optimal** solutions: solve, require `OPTIMAL`, store `best = m.objective_value`, add `m += m.objective >= best - 1e-6` and `m += m.objective <= best + 1e-6`, then run the loop above ([all-optimal-committee](assets/all-optimal-committee/README.md)).

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `OPTIMAL`, but a better solution exists | default `max_mip_gap` 1e-4 | set `max_mip_gap` and `max_mip_gap_abs` to 0 |
| Log lines in the output, parser fails | `verbose` defaults to 1 | `m.verbose = 0` |
| `TypeError: Can not multiply with type Var` | `x * y` | encode the product (table above) |
| `TypeError: bad operand type for abs()` | `abs(var)` | `d >= a - b`, `d >= b - a` with minimisation |
| A branch never runs, or a constraint has no effect | `if x == 3:` is always true | use `m += x == 3`, or compare `x.x` after the solve |
| `ValueError: Invalid bounds for binary variable` | `var_type=mip.BINARY` with `lb` or `ub` other than 0 and 1 | omit the bounds of a binary |
| `TypeError: type ... bool not supported` | `m += 2 <= 3` | write the constraint with variables |
| `TypeError: type ... Var not supported` on `m += x` | a bare expression is not a constraint | `m.objective = x` |
| `5.0` where `5` is expected | solution values are floats | `round()`; keep integer outputs integer variables |
| `None` in output, or `TypeError` on `None` | no solution | check the status before reading values |
| `OTHER`, `Model has no variables` | no `add_var` before `optimize` | create the variables first |
| Enumeration repeats answers or never ends | cut over auxiliary variables, or unbounded integers | cut only decision binaries; bound every integer |
| Wrong answer after a disjunction or `!=` | `M` too small | compute `M` from the bounds |
| Solver is Gurobi, not CBC | `gurobipy` installed | `mip.Model(solver_name="CBC")` |
| `FEASIBLE` or `NO_SOLUTION_FOUND` on a hard model | time limit reached | the answer is not proven; say so or raise `max_seconds` |

## Further reading

- Documentation: [Python-MIP site](https://www.python-mip.com), [user guide and API](https://python-mip.readthedocs.io/en/latest/)
- API reference: [classes, status values and parameters](https://python-mip.readthedocs.io/en/latest/classes.html)
- Source and issues: [coin-or/python-mip](https://github.com/coin-or/python-mip)
