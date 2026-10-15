# exact: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how Exact
(Python bindings) expresses it. Runner: [run.py](run.py), which imports `emit`, `finish`,
`flatten` and `mapped` from [runner/runtime.py](../../runner/runtime.py) but has its own
`build`, solve and enumeration loop.

## Submission file

One Python file, `model.py`. It may import `exact` and the standard library; nothing else
is installed (no NumPy), and no other file of yours is staged.

## Entrypoint

```python
def build(instance) -> tuple[Exact, dict] | tuple[Exact, dict, tuple[str, list[tuple[int, str]]]]:
```

The runner imports the file and calls `build(instance)` once. It must return a 2-tuple
`(solver, outputs)` for a satisfaction problem, or a 3-tuple
`(solver, outputs, (direction, terms))` for an optimisation problem, with `solver` an
`exact.Exact`. Anything the module prints goes to stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a **variable name**
(the `str` given to `addVariable`), or a nested list/tuple of names with the declared
shape. The runner reads them all with `getLastSolutionFor(names)`; every value comes back
as an integer, so a Boolean output is a variable over 0..1 reported as `0`/`1`.

## Objective

The third element of the return value: `("minimize", terms)` or `("maximize", terms)`,
with `terms` a list of `(integer coefficient, variable name)` pairs. The runner calls
`setObjective(terms, minimize=...)` and `toOptimum`, accepts only the state `"SAT"` as a
proven optimum, then pins `terms` at that value with `addConstraint` before enumerating.

## Solving

- The runner sets no solver option; it passes the seconds left of `execution_timeout`
  (measured from the start of the run, `build` included) as the timeout of each
  `toOptimum` and `runFull` call.
- Optimisation: `toOptimum` returning `"SAT"` is the proven optimum, `"UNSAT"` gives
  `unsat`, and `"TIMEOUT"` or any other state gives `timeout` (the incumbent Exact still
  holds is never reported). Exact minimises internally, so for `"maximize"` the runner
  negates the returned value before pinning `terms` to it.
- Enumeration: `runFull(False, left)`. `"SAT"` reports a solution, `"UNSAT"` gives `unsat`
  on the first call and `complete` after, anything else `timeout`.
- Next solution: `invalidateLastSol(names)`, Exact's own blocking clause projected onto
  the declared output variables, so solutions differing only in auxiliary variables are
  not found twice.
- Time: there is no `SIGALRM`; only Exact's timeouts bound the search. Import and `build`
  are not bounded by the runner: the evaluator kills the container at
  `execution_timeout + 10` s, reported as `execution_timeout`.

## Compilation

None.

## Environment

Image `dcp-eval/exact:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11 at
`/usr/local/bin/python`, `exact` 2.2.1 (pip lists it as `Exact`; one compiled module,
`site-packages/exact.cpython-312-x86_64-linux-gnu.so`) and nothing else besides pip (the
shared `runner/requirements.txt` stack is not installed). JSON is the standard library's
`json`. No edition or size limits (a variable over 0..10^20 is accepted); the package is
AGPL-3.0.

Inside the container: no network, a read-only filesystem except `/tmp` (512 MB tmpfs, the
working directory, and `HOME`), user 65534, the submission and `request.json` under
`/input`. The image's entrypoint is the runner (`python /opt/runner/run.py`); for an ad
hoc run override it, e.g. `docker run --rm --network none --entrypoint sh
dcp-eval/exact:v1 -c '...'`.

## Traps

- An output leaf must be a `str` naming a declared variable. A Python integer, Boolean or
  any other object is rejected (`execution_error`); for a constant output declare a fixed
  variable, `addVariable(name, c, c)`. An undeclared name raises
  `ValueError: No variable ... found` (`execution_error`).
- The objective is a term list, not an expression, and has no constant offset. Do not call
  `setObjective` in `build`: the runner sets the objective from the third element only.
- `import numpy` fails in this image (`execution_error`).

## Example

The pilot fixture [tests/fixtures/model_exact.py](../../tests/fixtures/model_exact.py)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```python
from exact import Exact


def build(instance):
    n = instance["n"]
    solver = Exact()
    solver.addVariable("x", 0, n)
    solver.addVariable("y", 0, n)
    if not instance["optimize"]:
        solver.addConstraint([(1, "x"), (1, "y")], True, n, True, n)
        return solver, {"x": "x", "y": "y"}
    solver.addConstraint([(1, "x"), (1, "y")], True, n)
    return solver, {"x": "x", "y": "y"}, ("minimize", [(1, "x"), (1, "y")])
```
