# gurobipy_python: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how gurobipy
(Python, Gurobi) expresses it. Runner: [run.py](run.py), which takes only `emit` and
`finish` from [runner/runtime.py](../../runner/runtime.py) and does its own solving.

## Submission file

One Python file, `model.py`. It may import `gurobipy`, `numpy`, `scipy` and the standard
library; nothing else is installed, and no other file of yours is staged.

## Entrypoint

```python
def build(instance) -> tuple[gurobipy.Model, dict]:
```

The runner imports the file and calls `build(instance)` once. It must return a 2-tuple
(not a list) `(model, outputs)` with `model` a `gurobipy.Model`. Anything the module
prints goes to stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a `gp.Var`,
`LinExpr` or `QuadExpr`, a Python/NumPy integer or Boolean, or a nested `list`/`tuple`
of these. Anything with `.tolist()` (an `MVar`, a NumPy array) is expanded element by
element. Integer and binary variables are rounded to the nearest integer and expressions
are evaluated over the rounded values. A `GRB.BINARY` variable is reported as `0`/`1`.
A value that is not within 1e-6 of an integer is rejected (`execution_error`).

## Objective

`model.setObjective(expr, GRB.MINIMIZE)` or `GRB.MAXIMIZE`. An objective with no
variable terms (never set, or a constant) is a satisfaction problem; more than one
objective (`NumObj > 1`) is `unsupported`.

## Solving

- Forced over the submission's own parameters: `OutputFlag = 0` (no solver log),
  `Threads = 1`, `MIPGap = 0` (Gurobi's default 1e-4 relative gap reports `OPTIMAL` short
  of the optimum) and `TimeLimit` = the budget left. Other parameters you set are kept.
- Status: `OPTIMAL` with a solution is proven; `INFEASIBLE` is `unsat`; `UNBOUNDED` is
  `error` (objective unbounded); `TIME_LIMIT` is `timeout`; any other status is `error`.
  On `INF_OR_UNBD` the runner re-solves once with `DualReductions = 0` and maps the new
  status. `SIZE_LIMIT_EXCEEDED` is `unsupported`, any other `GurobiError` `error`.
- Enumeration is not pool-based: after the first proven solve the objective is pinned by
  two constraints (±0.5 around the optimum for an integral objective) and replaced by 0;
  each next solve adds a no-good over the integer variables under the declared outputs
  (a linear term per binary, two indicator constraints per general integer; fixed
  variables skipped). A repeated output value is re-solved, not emitted. Infeasible after
  a no-good, or no unfixed variable left to move, is `complete`.
- Time: the deadline is set before `build` runs, so building spends the budget. Each solve
  gets the time left; a SIGALRM at budget + 5 s, armed over `build` and the whole loop,
  turns a hang in Python into `timeout`.

## Compilation

None.

## Environment

Image `dcp-eval/gurobipy_python:v1`: Python 3.12.11 (`/usr/local/bin/python`), gurobipy
13.0.3 (Gurobi Optimizer 13.0.3), NumPy 2.4.6, SciPy 1.18.1; the standard library (`json`
included) and nothing else. The wheel's bundled licence needs no licence file and no
network (the container has none) and expires 2027-11-29. It refuses a model above 2000
variables or 2000 linear constraints with `GurobiError` 10010 (`SIZE_LIMIT_EXCEEDED`):
`Model too large for size-limited license; visit https://gurobi.com/unrestricted for more
information`. Its banner (`Restricted license - for non-production use only - expires
2027-11-29`) is printed from C to file descriptor 1; the runner keeps the protocol on its
own copy of that descriptor and sends fd 1, and everything the submission prints, to
stderr. For an ad hoc run, `--entrypoint sh` bypasses `/opt/runner/run.py`.

## Traps

- The licence size limit (see Environment) is reported as `unsupported`, which the
  evaluator records as `unsupported_capability`; size the model for the largest
  instance. Enumeration adds rows of its own: two constraints pinning the objective,
  one no-good per extra solution, and per general-integer output variable up to two
  binaries and two indicator constraints.
- With `solution_limit > 1`, any continuous variable under an output is `unsupported`.
- A `tupledict` from `addVars` is a dict, which the runner walks as one. Keyed by tuples
  it crashes serialisation (`execution_error`, not `invalid_output`); keyed by ints it
  becomes a JSON object (`invalid_output`). Return lists:
  `[[x[i, j] for j in range(m)] for i in range(n)]`.
- An `MLinExpr` or a general expression (`gp.abs_`, `gp.max_`, ...) is not an accepted
  leaf (`execution_error`): give a list of `LinExpr`, or the variable the general
  constraint defines.
- The no-good is over the variables an output is built from, not its value: an output
  expression over many variables makes the runner re-solve through every assignment
  with the same value. Declare such an output as its own integer variable.

## Example

The pilot fixture [tests/fixtures/model_gurobipy.py](../../tests/fixtures/model_gurobipy.py)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```python
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    model = gp.Model()
    x = model.addVar(lb=0, ub=n, vtype=GRB.INTEGER, name="x")
    y = model.addVar(lb=0, ub=n, vtype=GRB.INTEGER, name="y")
    if instance["optimize"]:
        model.addConstr(x + y >= n)
        model.setObjective(x + y, GRB.MINIMIZE)
    else:
        model.addConstr(x + y == n)
    return model, {"x": x, "y": y}
```
