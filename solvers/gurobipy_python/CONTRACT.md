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
objective (`NumObj > 1`) is `unsupported`. The runner sets `OutputFlag = 0`,
`Threads = 1`, `MIPGap = 0` and `TimeLimit` over yours; other parameters are kept.

## Compilation

None.

## Environment

Image `dcp-eval/gurobipy_python:v1`: Python 3.12.11, gurobipy 13.0.3 with its bundled
size-limited licence (no licence file, no network; expires 2027-11-29), NumPy 2.4.6,
SciPy 1.18.1. One thread.

## Traps

- The bundled licence refuses a model above 2000 variables or 2000 linear constraints.
  That `GurobiError` (`SIZE_LIMIT_EXCEEDED`) is reported as `unsupported`, which the
  evaluator records as `unsupported_capability`; size the model for the largest
  instance. Enumeration adds rows of its own: two constraints pinning the objective,
  one no-good per extra solution, and per general-integer output variable up to two
  binaries and two indicator constraints.
- With `solution_limit > 1`, any continuous variable under an output is `unsupported`.
- A `tupledict` from `addVars` is a dict. Keyed by tuples it crashes serialisation
  (`execution_error`); keyed by ints it becomes a JSON object (`invalid_output`).
  Return lists: `[[x[i, j] for j in range(m)] for i in range(n)]`.
- An `MLinExpr` or a general expression (`gp.abs_`, `gp.max_`, ...) is not an accepted
  leaf (`execution_error`): give a list of `LinExpr`, or the variable the general
  constraint defines.
- The no-good is over the variables an output is built from, not its value: an output
  expression over many variables makes the runner re-solve through every assignment
  with the same value. Declare such an output as its own integer variable.
- The old skill says a returned `tupledict` gives `invalid_output`; with tuple keys it
  is an `execution_error`.

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
