---
name: cpmpy-python
description: CPMpy is a Python constraint modelling library for constraint programming and optimisation, solved by OR-Tools CP-SAT by default. Use when writing, debugging or explaining CPMpy models, or when the user has chosen CPMpy for scheduling, assignment, packing, sequencing or other combinatorial problems.
license: Apache-2.0
compatibility: Requires Python 3.10+ and cpmpy 1.0.0 (tested; installs OR-Tools as a dependency). Other solvers need their own packages through extras.
metadata:
  domain: constraint-programming
  solver: cpmpy
  paradigm: cp
---

# CPMpy (Python)

CPMpy is a modelling layer: you write NumPy-like expressions and constraints, and a
backend solver (OR-Tools CP-SAT by default) searches. Expressions are lazy: nothing is
computed until `solve()`, so the built-in Python operators on them build constraints, and
the Python built-ins that test truth values (`max`, `min`, `any`, `all`, `if`) do not work.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [Scheduling and objectives](#scheduling-and-objectives)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- [Examples](#examples)

## Install

```bash
pip install cpmpy
python3 -c "import cpmpy; print(cpmpy.__version__)"
```

Python 3.10 or newer. OR-Tools is installed with CPMpy and is the default solver; no
licence or account is needed. Other backends come as extras, e.g. `pip install "cpmpy[z3]"`.
Details: [CPMpy documentation](https://cpmpy.readthedocs.io/en/latest/) and the
[installation notes in the README](https://github.com/CPMpy/cpmpy/blob/master/README.md).

## Quick start

```python
import cpmpy as cp

x, y = cp.intvar(0, 5, shape=2, name=["x", "y"])
model = cp.Model(x + y >= 5)
model.minimize(2 * x + 3 * y)
if model.solve():
    print("x =", x.value(), "y =", y.value(), "cost =", model.objective_value())
    print("status:", model.status().exitstatus.name)   # OPTIMAL
```

Output: `x = 5 y = 0 cost = 10`, then `status: OPTIMAL`.

## Modelling

Full list: [API catalogue](references/api.md) and the
[model and variable reference](https://cpmpy.readthedocs.io/en/latest/api/model.html).

| Need | API |
|---|---|
| integer variables | [`cp.intvar(lb, ub, shape=None, name=None)`](https://cpmpy.readthedocs.io/en/latest/api/expressions/variables.html) |
| Boolean variables | [`cp.boolvar(shape=None, name=None)`](https://cpmpy.readthedocs.io/en/latest/api/expressions/variables.html) |
| a model | [`cp.Model(*constraints)`](https://cpmpy.readthedocs.io/en/latest/api/model.html); `model += c` adds more |
| all different | [`cp.AllDifferent(*args)`](https://cpmpy.readthedocs.io/en/latest/api/expressions/globalconstraints.html) |
| element / table / cumulative / no-overlap | [`arr[idx]`](#modelling), [`cp.Table`](https://cpmpy.readthedocs.io/en/latest/api/expressions/globalconstraints.html), [`cp.Cumulative`](https://cpmpy.readthedocs.io/en/latest/api/expressions/globalconstraints.html), [`cp.NoOverlap`](https://cpmpy.readthedocs.io/en/latest/api/expressions/globalconstraints.html) |
| reification / implication | [`a.implies(b)`](https://cpmpy.readthedocs.io/en/latest/api/expressions/variables.html); `(x >= 3).implies(b)` |
| index a Python list or NumPy array by a variable | [`cp.cpm_array(arr)[idx]`](https://cpmpy.readthedocs.io/en/latest/api/expressions/variables.html) |
| index a CPMpy variable array by a variable | `arr[idx]`, no wrapping |
| sum / absolute value / max / min | `cp.sum`, `cp.abs`, `cp.max`, `cp.min` ([functions](https://cpmpy.readthedocs.io/en/latest/api/expressions/globalfunctions.html)) |
| number of distinct values | `cp.NValue(arr)` ([functions](https://cpmpy.readthedocs.io/en/latest/api/expressions/globalfunctions.html)) |
| minimise / maximise | [`model.minimize(expr)` / `model.maximize(expr)`](https://cpmpy.readthedocs.io/en/latest/api/model.html) |

Operators on expressions: comparisons `== != < <= > >=`; arithmetic `+ - * // % **` and unary
`-`; logic `& | ~ ^`, `a.implies(b)`. Integer only: a float anywhere fails (see
[Common issues](#common-issues)).

**Naming.** `cp.max` and `cp.min` are the expression-aware forms of `cp.Maximum` and
`cp.Minimum`: `cp.max(x)` and `cp.Maximum(x)` build the same expression, printed as
`max(x[0],x[1],...)`. Both `cp.max` and `cp.Maximum` take a list of expressions; `cp.max` also
accepts several arguments (`cp.max(a, b, 3)`). On plain numbers, `cp.max` falls back to Python's
built-in. `cp.sum` is the same as the built-in `sum` on expressions; prefer `cp.sum` for clarity.

```python
import cpmpy as cp

values = cp.intvar(0, 9, shape=3)
pick = cp.boolvar(shape=3)
table = [10, 20, 30]
model = cp.Model(
    cp.AllDifferent(values),
    (values[0] >= 5).implies(pick[0]),          # reified implication
    cp.cpm_array(table)[values[1] // 4] == 20,  # list indexed by a variable
)
```

## Solving

Status values: [solver interface](https://cpmpy.readthedocs.io/en/latest/api/solvers/solver_interface.html).
`solve()` returns `True` when a solution was found, `False` when none was found.
Read the reason from `model.status().exitstatus`, a `cpmpy.solvers.solver_interface.ExitStatus`.

| Status | Meaning |
|---|---|
| `OPTIMAL` | optimisation: objective proven optimal |
| `FEASIBLE` | solution found, optimality not proven (time limit), or a satisfaction problem solved |
| `UNSATISFIABLE` | proven: no solution |
| `UNKNOWN` | limit reached with no solution found |

Satisfaction problems report `FEASIBLE`, not `OPTIMAL`; use the return value of `solve()`.
`ERROR` and `NOT_RUN` also exist.

Read values with `var.value()` (a NumPy integer or Boolean), and the objective with
`model.objective_value()`. Both are `None` or invalid until a solution exists; read them only
after `solve()` returned `True`.

Parameters go to the solver, and naming it is required when passing keyword arguments:

```python
model.solve(solver="ortools", time_limit=10, num_workers=1, random_seed=7)
```

[Solve parameters](https://cpmpy.readthedocs.io/en/latest/api/model.html). A model can
also be extended after solving: `model += constraint` and solve again.

## Scheduling and objectives

**Renewable resource (Cumulative).** `cp.Cumulative(start, duration, end=end, demand=demand,
capacity=capacity)` keeps the total demand of the tasks running at any time within capacity.
Worked example: [scheduling-cumulative](assets/scheduling-cumulative/README.md).

**One task at a time on a machine (disjunctive).** Use one `NoOverlap` per machine, not one for
all tasks (a single one would force every task to be disjoint from every other). Group the
tasks by machine, then unpack each group into three lists with `zip(*tasks)`:

```python
tasks_on = {}                                   # machine -> [(start, duration, end), ...]
for j, job in enumerate(jobs):                  # job = [(machine, duration), ...]
    for k, (machine, duration) in enumerate(job):
        tasks_on.setdefault(machine, []).append((start[j][k], duration, end[j][k]))
for tasks in tasks_on.values():
    s, d, e = (list(column) for column in zip(*tasks))
    model += cp.NoOverlap(s, d, e)
```

**Job order.** A job's operations run in sequence: `end[j][k] <= start[j][k + 1]`.
**Makespan.** `makespan >= end[j][k]` for every operation, then `model.minimize(makespan)`.
Worked example: [scheduling-jobshop](assets/scheduling-jobshop/README.md).

**Number of distinct values (for example, colours).** `model.minimize(cp.NValue(colour))` gives
the number of distinct values directly. The alternative `model.minimize(cp.max(colour))` gives
the largest label, which is one less than the count (labels 0..n-1), so report
`max + 1`. Both were verified as optima; prefer `cp.NValue` for readability.

## All solutions

`model.solveAll(display=callback, solution_limit=None)` calls `callback()` on every
solution (read the values inside it) and returns the count.

- **OR-Tools rejects a model with an objective**: `solveAll` raises `NotSupportedError`.
  Build the enumeration model without `minimize`/`maximize`.
- **Solutions are counted over all variables of the model.** A variable the outputs do not
  determine (a free auxiliary `intvar` or `boolvar`) multiplies the count: two outputs with
  a free Boolean gave 12 solutions instead of 6. An auxiliary variable fixed by the outputs
  (`a == cp.max(x)`) does not duplicate. Expressions over decision variables (`q[i] + i`,
  `cp.max(x)`, `cp.abs(...)`) create no counted variables, so `AllDifferent` over diagonal
  expressions enumerates each solution once. Either enumerate a model whose variables are all
  outputs, or loop with blocking clauses:

```python
solutions = []
while model.solve():
    values = tuple(int(v.value()) for v in outputs)
    solutions.append(values)
    model += cp.any([v != x for v, x in zip(outputs, values)])
```

- **All optimal solutions**: solve with the objective to get `best`, then build
  `cp.Model(constraints + [objective == best])` without an objective and enumerate with
  `solveAll`. Ready-made in [assets/all-optimal](assets/all-optimal/README.md).

[Solution enumeration](https://cpmpy.readthedocs.io/en/latest/api/model.html).

## Examples

Each folder under `assets/` is a standalone program with a README:

| Example | Pattern |
|---|---|
| [satisfy-seating](assets/satisfy-seating/README.md) | satisfy; `AllDifferent`, `abs`, checking the result |
| [all-solutions](assets/all-solutions/README.md) | enumerate every solution with `solveAll` |
| [all-optimal](assets/all-optimal/README.md) | every optimal solution |
| [maximise-production](assets/maximise-production/README.md) | maximise; integer vector; proven-optimal check |
| [minimise-assignment](assets/minimise-assignment/README.md) | minimise; permutation; list indexed by a variable |
| [infeasible-pigeonhole](assets/infeasible-pigeonhole/README.md) | infeasible; reading the status |
| [scheduling-cumulative](assets/scheduling-cumulative/README.md) | scheduling; `Cumulative` with `end` variables; data from a JSON file |
| [scheduling-jobshop](assets/scheduling-jobshop/README.md) | scheduling; one `NoOverlap` per machine; job order; makespan |

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `ValueError: __bool__ should not be called on a CPMPy expression` | Python `max`, `min`, `any`, `all` or an `if` on an expression | use `cp.max`, `cp.min`, `cp.any`, `cp.all`; the built-in `sum` works but prefer `cp.sum` |
| Job-shop or machine schedule with no valid solution, or every task disjoint | one `NoOverlap` over all tasks | one `NoOverlap` per machine, see [Scheduling and objectives](#scheduling-and-objectives) |
| Colour count is one less than expected | `minimize(cp.max(colour))` gives the largest label | minimise `cp.NValue(colour)` or report `max + 1` |
| `TypeError: Multiplication does not support float constants` | a float coefficient, also inside a NumPy float array | scale to integers |
| `TypeError: list indices must be integers or slices, not _IntVarImpl` | Python list indexed by a variable | `cp.cpm_array(list)[var]` |
| `IndexError: only integers, slices ...` | NumPy array indexed by a variable | `cp.cpm_array(np_array)[var]` |
| `ValueError: operands could not be broadcast together` | mismatched shapes in `*` | match the shapes; NumPy broadcasting rules apply |
| `NotSupportedError: OR-tools does not support finding all optimal solutions` | `solveAll` on a model with an objective | move the objective to a constraint, see [All solutions](#all-solutions) |
| `solveAll` returns more solutions than expected | a free auxiliary variable the outputs do not determine | enumerate over outputs only, or use blocking clauses; see [All solutions](#all-solutions) |
| `NotSupportedError: Specify the solver when using kwargs` | `solve(time_limit=...)` without `solver=` | `solve(solver="ortools", time_limit=...)` |
| `solve()` is `False` but the cause is unclear | expected | read `model.status().exitstatus`: `UNSATISFIABLE` is proof, `UNKNOWN` is a limit |
| status `FEASIBLE` on a minimisation | time limit reached | the solution is valid but not proven optimal; raise the limit |
| `AttributeError` from `DirectConstraint` | name is not a native method of the solver | use the native name, e.g. `"AddAllDifferent"` for OR-Tools |

## Further reading

- Documentation: [cpmpy.readthedocs.io](https://cpmpy.readthedocs.io/en/latest/)
- API reference: [model](https://cpmpy.readthedocs.io/en/latest/api/model.html), [global constraints](https://cpmpy.readthedocs.io/en/latest/api/expressions/globalconstraints.html), [OR-Tools backend](https://cpmpy.readthedocs.io/en/latest/api/solvers/ortools.html)
- Examples: [CPMpy examples folder](https://github.com/CPMpy/cpmpy/tree/master/examples)
