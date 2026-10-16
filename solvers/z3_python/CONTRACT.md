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

## Solving

- The only parameter set is Z3's `timeout`, in milliseconds, on each `check()`: what is
  left of `execution_timeout`, measured from the start of the run (including `build`).
- Optimisation: `check()` on the runner's `z3.Optimize`. `unsat` gives `unsat`; `unknown`,
  or `sat` with lower and upper bound apart, gives `timeout`.
- Enumeration: a plain `z3.Solver` over the constraints (plus `objective == best`).
  `sat` reports a solution; `unsat` gives `unsat` on the first check and `complete`
  after; `unknown` gives `timeout`.
- Next solution: `Or(leaf != value)` over every declared output leaf that is not a Python
  constant, with values read under `model_completion=True`. With only constant leaves
  the next check is refused outright, so the search is `complete` after one solution.
- Time: a `SIGALRM` at `execution_timeout + 5` s is a backstop that becomes `timeout`;
  Z3's own `timeout` is what stops a search.

## Compilation

None.

## Environment

Image `dcp-eval/z3_python:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11 at
`/usr/local/bin/python`, the `z3-solver` 5.1.0.0 wheel (Z3 core 5.1.0, as
`z3.get_version_string()` reports) and nothing else besides pip (the shared
`runner/requirements.txt` stack is not installed). JSON is the standard library's `json`.
No edition or size limits.

Inside the container: no network, a read-only filesystem except `/tmp` (512 MB tmpfs, the
working directory, and `HOME`), user 65534, the submission and `request.json` under
`/input`. The image's entrypoint is the runner (`python /opt/runner/run.py`); for an ad
hoc run override it, e.g. `docker run --rm --network none --entrypoint sh
dcp-eval/z3_python:v1 -c '...'`.

## Traps

- `import numpy` fails in this image (`execution_error`); build nested structure with
  lists.
- An objective set on a returned `z3.Optimize` (`opt.minimize(...)`) is ignored: only the
  third tuple element declares the objective.
- An objective with no finite bound, or a `Real`-sorted one, is reported as
  `execution_error` ("Objective is not a finite integer..."). `z3.Int` is unbounded, so
  add the bounds the problem implies.
- An output of a non-integer, non-Boolean sort raises in the runner and is reported as
  `execution_error`.
- An output in no constraint is accepted (model completion gives it `0` or `false`) and
  is then enumerated over its whole domain, which for a `z3.Int` is unbounded: constrain
  every output to the domain the problem implies.

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
