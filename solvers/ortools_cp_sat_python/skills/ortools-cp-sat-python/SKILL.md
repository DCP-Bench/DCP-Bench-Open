---
name: ortools-cp-sat-python
description: OR-Tools CP-SAT, Google's constraint programming and integer optimisation solver, used from Python (ortools.sat.python.cp_model). Use when writing, debugging or explaining integer or Boolean models in Python with CP-SAT, including scheduling, assignment, packing, enumerating all or all optimal solutions, or interpreting CP-SAT statuses.
license: Apache-2.0
compatibility: Requires Python 3.10+ and the ortools package (tested with 9.15, Python 3.12); free and open source, no licence key
metadata:
  domain: constraint-programming
  solver: ortools-cp-sat
  paradigm: cp
---

# OR-Tools CP-SAT (Python)

CP-SAT is a constraint solver over **integer and Boolean variables**. Every constraint is
built from integer linear expressions or a global constraint, and the objective must be
an integer linear expression. Anything else (products of variables, division, floats) has
to be modelled with a helper constraint such as `add_multiplication_equality`.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [All optimal solutions](#all-optimal-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Runnable examples: `assets/`, one folder per pattern, each with a README

## Install

```bash
pip install ortools
python3 -c "from ortools.sat.python import cp_model; print(cp_model.__name__)"
```

The package is free and needs no licence. Details: [install guide](https://developers.google.com/optimization/install/python).

## Quick start

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()
x = model.new_int_var(0, 10, "x")
y = model.new_int_var(0, 10, "y")
model.add(x + 2 * y == 14)
model.maximize(x + y)

solver = cp_model.CpSolver()
status = solver.solve(model)
if status == cp_model.OPTIMAL:
    print(solver.status_name(status), solver.value(x), solver.value(y), solver.objective_value)
```

## Modelling

Full API: [CpModel reference](https://or-tools.github.io/docs/pdoc/ortools/sat/python/cp_model.html).
Each row names its method on `CpModel` unless stated otherwise.

| Need | API |
|---|---|
| integer variable (name is **required**) | `new_int_var(lb, ub, name)` |
| variable with a non-interval domain | `new_int_var_from_domain(cp_model.Domain.from_values([2, 4, 8]), name)` |
| Boolean variable | `new_bool_var(name)`; negation `b.Not()` |
| constant | `new_constant(5)` or plain Python `5` |
| linear constraint | `add(expr <= k)`; `==`, `!=`, `>=` work the same |
| sum / weighted sum | `cp_model.LinearExpr.sum(xs)`, `cp_model.LinearExpr.weighted_sum(xs, ws)`; Python `sum()` also works |
| reification (enforce a constraint when a literal holds) | `add(...).only_enforce_if(b)` |
| at least one / at most one / exactly one | `add_bool_or`, `add_at_most_one`, `add_exactly_one` |
| implication / xor | `add_implication(a, b)`, `add_bool_xor` |
| all different (items may be linear expressions) | `add_all_different(xs)`, e.g. `add_all_different([col[i] + i for i in range(n)])` for the diagonals of n-queens |
| element (`arr[i]` with variable `i`) | `add_element(index, values, target)` |
| allowed / forbidden tuples | `add_allowed_assignments(vars, tuples)`, `add_forbidden_assignments` |
| min / max / abs of expressions | `add_min_equality`, `add_max_equality`, `add_abs_equality` |
| product / division / modulo of variables | `add_multiplication_equality`, `add_division_equality`, `add_modulo_equality` |
| circuit (Hamiltonian cycle) | `add_circuit(arcs)`, `add_multiple_circuit` |
| interval for scheduling | `new_interval_var(start, size, end, name)`, `new_fixed_size_interval_var(start, size, name)`, `new_optional_interval_var` |
| no two intervals overlap (one list per machine or resource) | `add_no_overlap(intervals)`; worked example: `assets/jobshop-no-overlap/` |
| shared resource limit | `add_cumulative(intervals, demands, capacity)`; worked example: `assets/tasks-scheduling/` |
| minimise / maximise | `minimize(expr)`, `maximize(expr)`; `clear_objective()` removes it |
| check the model before solving | `validate()` returns `''` when valid, else a message |

Reading and writing expressions:

| Writing | Result |
|---|---|
| `if x:`, `bool(x == 1)` | `NotImplementedError`: an expression has no truth value; use `add` or `only_enforce_if` |
| `x // 2`, `x / 2`, `x * y` in a constraint | `TypeError`: use `add_division_equality` / `add_multiplication_equality` with an auxiliary variable |
| `x * 0.5` in a constraint | `TypeError`: scale to integers |
| `x in list`, `list.index(x)` | compares by identity; `==` between expressions builds a constraint, it is not a Boolean |

Reading instance data: CP-SAT does not read files. Read them in plain Python and build the
model from the values: `with open(path) as f: data = json.load(f)`, where `path` comes from
the caller (for example `sys.argv[1]`). Size the variables from the data, not from the example
you were shown. Worked example: `assets/coins-minimise/`.

Minimising the number of distinct values (for example colours): minimise the largest index
with `add_max_equality`. At an optimum the values are `0..k-1`, so the largest index is
`k - 1` and the count is exact. Worked example: `assets/colouring-min-colours/`.

Modelling notes: [CP-SAT primer](https://developers.google.com/optimization/cp/cp_solver)
explains the overall approach; the constraint list in the reference above is the complete set.

## Solving

Status values and parameters: [CpSolver reference](https://or-tools.github.io/docs/pdoc/ortools/sat/python/cp_model.html),
definitions in [cp_model.proto](https://github.com/google/or-tools/blob/stable/ortools/sat/cp_model.proto).

| `status` (`cp_model.X`) | `solver.status_name(status)` | Meaning |
|---|---|---|
| `OPTIMAL` | `OPTIMAL` | Solution found and, with an objective, proven optimal. For a satisfaction model, a solution was found |
| `FEASIBLE` | `FEASIBLE` | Solution found, optimality not proven (typically a time limit) |
| `INFEASIBLE` | `INFEASIBLE` | Proven that no solution exists |
| `UNKNOWN` | `UNKNOWN` | Limit reached before anything was found |
| `MODEL_INVALID` | `MODEL_INVALID` | The model is malformed, e.g. `new_int_var(5, 1, "x")` (lower bound above upper bound) |

| Need | Call |
|---|---|
| time limit (seconds) | `solver.parameters.max_time_in_seconds = 10` |
| workers | `solver.parameters.num_workers = 8` (default `0` = automatic) |
| seed | `solver.parameters.random_seed = 7` |
| objective value / proven bound | `solver.objective_value`, `solver.best_objective_bound` |
| value of a variable or expression | `solver.value(x)`, `solver.value(x + y)`; Booleans give `0`/`1`, `solver.boolean_value(b)` gives `bool` |
| many values at once | `solver.values(list_of_vars)` |
| run time | `solver.wall_time` |
| summary string | `solver.solution_info()` |

- `solver.value` before `solve` raises `RuntimeError: solve() has not been called`.
- Only read values when `status` is `OPTIMAL` or `FEASIBLE`.
- **Optimisation problems:** the answer is the optimum, so accept only `OPTIMAL`. A `FEASIBLE`
  result is a solution with no proof of optimality; do not report it as the optimum. Either
  raise `max_time_in_seconds` and solve again, or report the status and the gap
  (`objective_value` against `best_objective_bound`) as the outcome. Example:
  `if status != cp_model.OPTIMAL: raise SystemExit(solver.status_name(status))`
  (as in `assets/ties-all-optimal/`).
- **Satisfaction problems:** `OPTIMAL` and `FEASIBLE` both mean a solution is available.
  `INFEASIBLE` is a proof that none exists, not an error.

## All solutions

Enumeration needs a callback; the solver calls it once per solution. Full details:
[enumerate all solutions](https://developers.google.com/optimization/cp/cp_solver#finding_all_solutions).

```python
class Collect(cp_model.CpSolverSolutionCallback):
    def __init__(self, outputs):
        super().__init__()
        self.outputs = outputs
        self.solutions = []

    def on_solution_callback(self):
        self.solutions.append(tuple(self.value(v) for v in self.outputs))

solver = cp_model.CpSolver()
solver.parameters.enumerate_all_solutions = True
collector = Collect([x, y])
status = solver.solve(model, collector)
print(len(collector.solutions))
```

- Solutions are counted **per assignment of all variables**. An auxiliary variable that takes
  several values for the same declared outputs makes duplicates: record only the outputs
  (as above) and dedupe with `set(...)`, or make auxiliary variables fully determined by
  the outputs.
- **Zero solutions:** the callback is never called and the status is `INFEASIBLE`
  (for example three Booleans with `sum == 5`). Decide "no solutions" from the status, not from
  an empty list. If the status is `UNKNOWN` or `MODEL_INVALID`, the list is not a complete
  answer: report the status instead of the count.
- A finished enumeration of a satisfiable model returns status `OPTIMAL` (checked: 20 solutions of
  `sum == 3` over six Booleans). Do not report a count that a time limit cut short.

## All optimal solutions

Enumeration with an objective still set returns **one** optimal solution, not all of them.
Solve for the optimum, post the objective as a constraint, clear the objective, then enumerate:

```python
solver = cp_model.CpSolver()
solver.solve(model)
best = int(solver.objective_value)

model.add(total == best)
model.clear_objective()

enumerator = cp_model.CpSolver()
enumerator.parameters.enumerate_all_solutions = True
collector = Collect(outputs)
enumerator.solve(model, collector)
```

Check the first solve is `OPTIMAL` before using `objective_value`. Worked example:
`assets/ties-all-optimal/`. Several objective terms can tie; `total` must be the same linear
expression as the objective.

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `TypeError: new_int_var() missing ... 'name'` | the name argument is required in this version | pass a name string |
| `NotImplementedError` on `if x` or `bool(...)` | using an expression as a Boolean | use `add`, `only_enforce_if` or `.Not()` |
| `TypeError` on `x * y`, `x // k`, `x / k` | nonlinear arithmetic in a linear expression | introduce a variable with `add_multiplication_equality` or `add_division_equality` |
| float objective: the runner refuses it, though `maximize(z * 0.5)` solves locally | the local solver accepts float coefficients, but the objective must be integer, so a local run does not show the model is valid | make every objective coefficient an integer: multiply the objective by a common factor (`maximize(z * 0.5)` becomes `maximize(z)`: the same `z` is optimal, and the true value is half the reported one) |
| `MODEL_INVALID` | e.g. a variable with lower bound above upper bound | `model.validate()` gives the message; fix the bound |
| `RuntimeError: solve() has not been called` | reading values before solving | call `solver.solve(model)` first |
| `FEASIBLE` instead of `OPTIMAL` on an optimisation problem | time limit reached before the proof | raise `max_time_in_seconds` and solve again, or report the status and gap; do not report the value as the optimum |
| enumeration reports nothing | the instance is infeasible: the callback is never called | read the status: `INFEASIBLE` means zero solutions; other statuses mean the list is incomplete |
| too many solutions in enumeration | auxiliary variables multiply solutions | record and dedupe on declared outputs only |
| only one optimal solution enumerated | objective still set during enumeration | post `objective == best`, then `clear_objective()` |
| enumeration hangs | unbounded variable domain | give every variable finite bounds |
| data read from a file beside the script, not the path given | the file location is the caller's choice | open the path argument: `json.load(open(sys.argv[1]))`; see `assets/coins-minimise/` |
| one `add_no_overlap` over all operations | operations on different machines block each other | build one interval list per machine and one `add_no_overlap` per list; see `assets/jobshop-no-overlap/` |
| minimising "number of colours" with no counter | a count of distinct values is not a linear expression | minimise the largest index with `add_max_equality`; see `assets/colouring-min-colours/` |

## Further reading

- Documentation: [OR-Tools CP-SAT guide](https://developers.google.com/optimization/cp/cp_solver)
- Install: [install guide](https://developers.google.com/optimization/install/python)
- API reference: [cp_model (pdoc)](https://or-tools.github.io/docs/pdoc/ortools/sat/python/cp_model.html)
- Scheduling example with intervals: [job shop](https://developers.google.com/optimization/scheduling/job_shop)
- Examples in this skill: `assets/`, one folder per pattern, each with a README
