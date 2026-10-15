# pulp_cbc: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how PuLP with
CBC expresses it. Runner: [run.py](run.py), which imports `emit` and `finish` from
[runner/runtime.py](../../runner/runtime.py) but has its own `build`, solve and
enumeration loop.

## Submission file

One Python file, `model.py`. It may import `pulp` and the standard library; nothing else
is installed (no NumPy), and no other file of yours is staged.

## Entrypoint

```python
def build(instance) -> tuple[pulp.LpProblem, dict]:
```

The runner imports the file and calls `build(instance)` once. It must return exactly a
2-tuple `(problem, outputs)` with `problem` a `pulp.LpProblem`; a third element is
rejected. Anything the module prints goes to stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to an `LpVariable`, an
`LpAffineExpression`, a Python integer or Boolean, or a nested list/tuple of these with
the declared shape. The runner reads `pulp.value(leaf)`, rounds it, and rejects a value
more than 1e-6 from an integer; values come back as integers (`0`/`1` for a `Binary`).

## Objective

On the problem itself: the direction is the `sense` given to `LpProblem(name,
pulp.LpMinimize | pulp.LpMaximize)`, the objective is a bare expression added with
`problem += expr`. A problem whose `objective` stays `None` is a satisfaction problem,
whatever its sense. The runner accepts a solve only when CBC's `sol_status` is
`LpSolutionOptimal`, then pins the objective to within 1e-6 of that value before
enumerating.

## Compilation

None.

## Environment

Image `dcp-eval/pulp_cbc:v1`: Python 3.12.11, PuLP 3.3.2 with the CBC binary its wheel
ships, nothing else (the shared `runner/requirements.txt` stack is not installed). The
runner solves with one thread and a whole-second time limit.

## Traps

- Enumeration (more than one solution requested) needs every variable inside a declared
  output, including those inside an output expression, to be `Integer`/`Binary` and to
  have finite lower and upper bounds; otherwise the run is `unsupported_capability`.
- An output variable in no constraint is added through its bound; with no bound at all
  the run is an `execution_error`.
- An unbounded objective is an `execution_error` ("The objective is unbounded").
- A fractional output value raises in the runner and surfaces as `execution_error`, not
  `invalid_output` as the old skill said.
- The runner's no-good cuts add binaries named `_below_<i>_<j>` and `_above_<i>_<j>`; do
  not use those names.
- `import numpy` fails in this image (`execution_error`).

## Example

The pilot fixture [tests/fixtures/model_pulp.py](../../tests/fixtures/model_pulp.py)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```python
import pulp


def build(instance):
    n = instance["n"]
    problem = pulp.LpProblem("smoke", pulp.LpMinimize)
    x = pulp.LpVariable("x", 0, n, cat="Integer")
    y = pulp.LpVariable("y", 0, n, cat="Integer")
    if instance["optimize"]:
        problem += x + y >= n
        problem += x + y
    else:
        problem += x + y == n
    return problem, {"x": x, "y": y}
```
