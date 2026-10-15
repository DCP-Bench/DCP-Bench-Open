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

## Solving

- The runner sets one parameter, Choco's time limit, as `limit_time("<seconds>s")` with
  the time left (at least 1 ms). It is written in seconds because pychoco 0.2.1 ignores
  a limit written in milliseconds.
- Optimisation: `find_optimal_solution` on a first build. A result returned at least
  0.5 s before the budget left is the optimum; no result that early gives `unsat`; any
  later return gives `timeout`.
- Enumeration: repeated `solver.solve()` on a fresh build with `arithm(objective, "=",
  best)` posted. No no-good is added: Choco moves on to its next assignment of all
  variables, and the runner skips any whose declared outputs it has already reported.
  `solve()` returning false at least 0.5 s before the budget is exhaustion (`complete`,
  or `unsat` with nothing found); later is `timeout`.
- Time: the budget runs from the start of the run (including the first `build`). A
  search stops at Choco's own limit; a search stopped that late is reported as
  `timeout`. A `SIGALRM` at `execution_timeout + 5` s is a backstop that only fires once
  control is back in Python.

## Compilation

None.

## Environment

Image `dcp-eval/choco_python:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11 at
`/usr/local/bin/python`, pychoco 0.2.1 and nothing else besides pip (the shared
`runner/requirements.txt` stack is not installed). pychoco carries Choco as a native
library (`site-packages/pychoco/libchoco_capi.so`): there is no JVM and nothing is fetched
at run time. JSON is the standard library's `json`. No edition or size limits.

Inside the container: no network, a read-only filesystem except `/tmp` (512 MB tmpfs, the
working directory, and `HOME`), user 65534, the submission and `request.json` under
`/input`. The image's entrypoint is the runner (`python /opt/runner/run.py`); for an ad
hoc run override it, e.g. `docker run --rm --network none --entrypoint sh
dcp-eval/choco_python:v1 -c '...'`.

## Traps

- The objective must be a variable (anything with `get_value`), not an expression: post
  an equality onto an `IntVar` and pass that, or the run is an `execution_error`.
- `import numpy` fails in this image (`execution_error`).
- `build` must be deterministic and side-effect free: the optimum is proven on one call's
  model and pinned on another's.
- Choco enumerates assignments of every variable; the runner skips repeats of the declared
  outputs, which costs search time. Auxiliary variables left free can starve enumeration.
- An output leaf that is not a variable, integer or Boolean raises in the runner and is
  reported as `execution_error`.

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
