# choco_python: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how Choco
(pychoco) expresses it. Runner: [run.py](run.py), which imports `emit`, `finish`,
`flatten` and `mapped` from [runner/runtime.py](../../runner/runtime.py) but has its own
`build`, solve and enumeration loop.

## Submission file

One Python file, `model.py`. It may import `pychoco` and the standard library; nothing
else is installed (no NumPy), and no other file of yours is staged.

## Entrypoint

```python
def build(instance) -> tuple[Model, dict] | tuple[Model, dict, tuple[str, IntVar]]:
```

It must return a 2-tuple `(model, outputs)` for a satisfaction problem, or a 3-tuple
`(model, outputs, (direction, objective))` for an optimisation problem, with `model` a
`pychoco.model.Model`. Anything the module prints goes to stderr. For an optimisation
problem the runner calls `build(instance)` three times (a Choco search cannot be
rewound), so it must build a fresh, identical model on each call.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a Choco `IntVar` or
`BoolVar`, a Python integer or Boolean, or a nested list/tuple of these with the declared
shape. The runner reads `.get_value()` from each variable leaf: an `IntVar` gives an
`int`, a `BoolVar` a `bool`. Any leaf without `get_value` (a constraint, a string) is
rejected.

## Objective

The third element of the return value: `("minimize", var)` or `("maximize", var)`, with
`var` a Choco variable of that model. The runner proves the optimum with
`find_optimal_solution`, rebuilds the model and posts `arithm(var, "=", best)` before
enumerating.

## Compilation

None.

## Environment

Image `dcp-eval/choco_python:v1`: Python 3.12.11, pychoco 0.2.1 (bundles the Choco native
library; no JVM), nothing else (the shared `runner/requirements.txt` stack is not
installed).

## Traps

- The objective must be a variable (anything with `get_value`), not an expression: post
  an equality onto an `IntVar` and pass that, or the run is an `execution_error`.
- `import numpy` fails in this image (`execution_error`).
- `build` must be deterministic and side-effect free: the optimum is proven on one call's
  model and pinned on another's.
- pychoco 0.2.1 cannot say whether a search was exhausted, so the runner calls it
  exhausted only if it stopped at least 0.5 s before the budget; a search that ends later
  is reported as `timeout`.
- Choco enumerates assignments of every variable; the runner skips repeats of the declared
  outputs, which costs search time. Auxiliary variables left free can starve enumeration.
- An output leaf that is not a variable, integer or Boolean raises in the runner and
  surfaces as `execution_error`, not `invalid_output` as the old skill said.

## Example

The pilot fixture [tests/fixtures/model_choco.py](../../tests/fixtures/model_choco.py)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```python
from pychoco.model import Model


def build(instance):
    n = instance["n"]
    model = Model()
    x = model.intvar(0, n, name="x")
    y = model.intvar(0, n, name="y")
    if not instance["optimize"]:
        model.arithm(x, "+", y, "=", n).post()
        return model, {"x": x, "y": y}
    model.arithm(x, "+", y, ">=", n).post()
    total = model.intvar(0, 2 * n, name="total")
    model.sum([x, y], "=", total).post()
    return model, {"x": x, "y": y}, ("minimize", total)
```
