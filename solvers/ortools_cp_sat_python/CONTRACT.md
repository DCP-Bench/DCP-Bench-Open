# ortools_cp_sat_python: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how OR-Tools
CP-SAT (Python) expresses it. Runner: [run.py](run.py), which calls `main("cp_sat")` in
[runner/runtime.py](../../runner/runtime.py).

## Submission file

One Python file, `model.py`. It may import `ortools`, `numpy` and the standard library
(the image installs the shared `runner/requirements.txt` stack); no other file of yours
is staged.

## Entrypoint

```python
def build(instance) -> tuple[cp_model.CpModel, dict]:
```

The runner imports the file and calls `build(instance)` once. It must return a 2-tuple
`(model, outputs)` with `model` a `cp_model.CpModel`. Anything the module prints goes to
stderr, not to the result.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based. Convert to NumPy yourself where that helps.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a CP-SAT `IntVar`,
`BoolVar` (or its `.Not()`), integer linear expression, Python/NumPy integer or Boolean,
or a nested list/tuple/NumPy array of these with the declared shape. The runner reads each
leaf with `int(solver.value(leaf))`, so every value, Booleans included, is reported as an
integer (`0`/`1` for a Boolean).

## Objective

Set it on the model: `model.minimize(expr)` or `model.maximize(expr)`, with an integer
linear expression. No objective for a satisfaction problem.

## Compilation

None.

## Environment

Image `dcp-eval/ortools_cp_sat_python:v1`: Python 3.12.11, OR-Tools 9.15.6755, NumPy
2.5.3 (pinned in `runner/requirements.txt`). The runner solves with one search worker and
`keep_all_feasible_solutions_in_presolve`; the submission cannot set solver parameters.

## Traps

- A floating-point objective (any float coefficient in `minimize`/`maximize`) is refused
  before solving with `unsupported_capability` ("Use an integer objective").
- An output leaf `solver.value` cannot evaluate is an `execution_error`: a constraint
  such as `x >= 1`, a float or a float-coefficient expression, a string. Reify into a
  `BoolVar` and output that instead.
- A model CP-SAT validates as `MODEL_INVALID` is reported as `execution_error`
  ("Invalid CP-SAT model").
- Every variable created with `new_int_var`/`new_bool_var` is in the model, so an output
  that appears in no constraint is enumerated over its whole domain: give every output a
  domain that matches the problem.

## Example

The pilot fixture [tests/fixtures/model_cp_sat.py](../../tests/fixtures/model_cp_sat.py)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```python
from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]
    model = cp_model.CpModel()
    x, y = model.new_int_var(0, n, "x"), model.new_int_var(0, n, "y")
    model.add(x + y >= n if instance["optimize"] else x + y == n)
    if instance["optimize"]:
        model.minimize(x + y)
    return model, {"x": x, "y": y}
```
