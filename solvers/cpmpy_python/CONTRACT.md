# cpmpy_python: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how CPMpy
(Python) expresses it. Runner: [run.py](run.py), which calls `main("cpmpy")` in
[runner/runtime.py](../../runner/runtime.py).

## Submission file

One Python file, `model.py`. It may import `cpmpy`, `numpy` and the standard library;
no other file of yours is staged.

## Entrypoint

```python
def build(instance) -> tuple[cp.Model, dict]:
```

The runner imports the file and calls `build(instance)` once. It must return a 2-tuple
`(model, outputs)`. Anything the module prints goes to stderr, not to the result.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based. Convert to NumPy yourself where that helps (`np.array(...)`).

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a CPMpy variable,
expression, Python/NumPy integer or Boolean, or a nested list/NumPy array of these with the
declared shape. The runner reads `.value()` from each leaf; a leaf whose value is not an
integer or Boolean makes the runner raise, which the evaluator reports as
`execution_error`.

## Objective

Set it on the model: `model.minimize(expr)` or `model.maximize(expr)`, with an integer
expression. No objective for a satisfaction problem.

## Solving

- Every solve is `model.solve(solver="ortools", time_limit=<seconds left>,
  num_search_workers=1, keep_all_feasible_solutions_in_presolve=True)`; the submission
  cannot change these.
- Status: a solution is reported only when CPMpy's exit status is `OPTIMAL` (optimisation)
  or a solution was found (satisfaction). `UNSATISFIABLE` gives `unsat` on the first solve
  and `complete` after; anything else (a time limit, `FEASIBLE` with an objective) gives
  `timeout`.
- Next solution: the objective is pinned (`objective == best`, objective dropped), then
  `any(leaf != value)` over every declared output leaf is added and the model is solved
  again from scratch. The search is exhausted when that solve is `UNSATISFIABLE`.
- Time: each solve gets the seconds left of `execution_timeout`, measured from the start
  of the run (including `build`); a `SIGALRM` at exactly `execution_timeout` covers
  import and `build` too, and turns into `timeout`.

## Compilation

None.

## Environment

Image `dcp-eval/cpmpy_python:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11 at
`/usr/local/bin/python`, CPMpy 1.0.0 with OR-Tools CP-SAT 9.15.6755 as its solver,
NumPy 2.5.3, all pinned in `runner/requirements.txt`, which also installs pandas 3.0.5,
protobuf, absl-py, immutabledict, packaging, python-dateutil, six and typing_extensions.
JSON is the standard library's `json`. No edition or size limits.

Inside the container: no network, a read-only filesystem except `/tmp` (512 MB tmpfs, the
working directory, and `HOME`), user 65534, the submission and `request.json` under
`/input`. The image's entrypoint is the runner (`python /opt/runner/run.py`); for an ad
hoc run override it, e.g. `docker run --rm --network none --entrypoint sh
dcp-eval/cpmpy_python:v1 -c '...'`.

## Traps

- Output variables that appear in no constraint are still registered by the runner, so an
  unconstrained output is enumerated over its whole domain: give every output a domain that
  matches the problem.
- A float anywhere in an expression raises at build time (`TypeError: Multiplication does
  not support float constants`), which surfaces as `execution_error`. Scale to integers.

## Example

The pilot fixture [tests/fixtures/model_cpmpy.py](../../tests/fixtures/model_cpmpy.py)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```python
import cpmpy as cp


def build(instance):
    n = instance["n"]
    x, y = cp.intvar(0, n, shape=2)
    model = cp.Model(x + y >= n if instance["optimize"] else x + y == n)
    if instance["optimize"]:
        model.minimize(x + y)
    return model, {"x": x, "y": y}
```
