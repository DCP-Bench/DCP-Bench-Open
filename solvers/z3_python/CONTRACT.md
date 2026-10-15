# z3_python: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how Z3 (Python)
expresses it. Runner: [run.py](run.py), which imports `emit`, `finish`, `flatten` and
`mapped` from [runner/runtime.py](../../runner/runtime.py) but has its own `build`, solve
and enumeration loop.

## Submission file

One Python file, `model.py`. It may import `z3` and the standard library; nothing else is
installed (no NumPy), and no other file of yours is staged.

## Entrypoint

```python
def build(instance) -> tuple[constraints, dict] | tuple[constraints, dict, tuple[str, z3.ArithRef]]:
```

The runner imports the file and calls `build(instance)` once. It must return a 2-tuple
`(constraints, outputs)` for a satisfaction problem, or a 3-tuple
`(constraints, outputs, (direction, objective))` for an optimisation problem. `constraints`
is a `z3.Solver`, a `z3.Optimize` (only its assertions are taken), a list/tuple of Boolean
expressions, or a single one. Anything the module prints goes to stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a Z3 `Int`- or
`Bool`-sorted expression, a Python integer or Boolean, or a nested list/tuple of these with
the declared shape. The runner evaluates each expression with
`model.eval(e, model_completion=True)`: a Boolean comes back as `true`/`false`, an integer
as its `as_long()`; any other sort (a `Real`, a bit-vector) is rejected.

## Objective

The third element of the return value: `("minimize", expr)` or `("maximize", expr)`, with
`expr` an `Int`-sorted Z3 expression. A third element of `None` also means satisfaction.
The runner builds its own `z3.Optimize`, requires the proven lower and upper bound to be
the same finite integer, then adds `expr == best` before enumerating.

## Compilation

None.

## Environment

Image `dcp-eval/z3_python:v1`: Python 3.12.11, `z3-solver` 5.1.0.0 and nothing else (the
shared `runner/requirements.txt` stack is not installed).

## Traps

- `import numpy` fails in this image (`execution_error`); build nested structure with
  lists.
- An objective set on a returned `z3.Optimize` (`opt.minimize(...)`) is ignored: only the
  third tuple element declares the objective.
- An objective with no finite bound, or a `Real`-sorted one, is reported as
  `execution_error` ("Objective is not a finite integer..."). `z3.Int` is unbounded, so
  add the bounds the problem implies.
- An output of a non-integer, non-Boolean sort raises in the runner and surfaces as
  `execution_error`, not `invalid_output` as the old skill said.

## Example

The pilot fixture [tests/fixtures/model_z3.py](../../tests/fixtures/model_z3.py)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```python
import z3


def build(instance):
    n = instance["n"]
    x, y = z3.Ints("x y")
    # z3.Int has no domain, so the bounds the reference declares must be added.
    bounds = [x >= 0, x <= n, y >= 0, y <= n]
    if instance["optimize"]:
        return bounds + [x + y >= n], {"x": x, "y": y}, ("minimize", x + y)
    return bounds + [x + y == n], {"x": x, "y": y}
```
