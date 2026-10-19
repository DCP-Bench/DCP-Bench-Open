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

## Solving

- Each solve is `PULP_CBC_CMD(msg=0, threads=1, timeLimit=max(1, int(seconds left)))`:
  one thread, a whole-second limit of at least 1 s; no gap or presolve option is set.
- Status: `Infeasible` gives `unsat` on the first solve and `complete` after;
  `Unbounded` on the first solve gives `error` (see Traps). Otherwise a solve counts only
  when `sol_status` is `LpSolutionOptimal`: CBC reports `Optimal` even when it stopped on
  its time limit, and `sol_status` then reads `LpSolutionIntegerFeasible`, which gives
  `timeout` ("Candidate optimum was not proven" when there is an objective).
- Enumeration (solution limit above 1): every variable under a declared output, those
  inside an output expression included, must be `Integer`/`Binary` with finite bounds,
  else `unsupported`. The objective is held within 1e-6 of the optimum.
- Next solution: a big-M no-good cut over those variables, with binaries
  `_below_<k>_<i>` and `_above_<k>_<i>`, then a fresh CBC solve. A solution whose declared
  values repeat an earlier one (the cut moved only a variable inside an expression) is
  skipped. Exhausted when the cut problem is `Infeasible`, or every such variable is
  already fixed by its bounds.
- Time: the budget runs from the start of the run (`build` included). A `SIGALRM` at
  `execution_timeout + 5` s becomes `timeout`.

## Compilation

None.

## Environment

Image `dcp-eval/pulp_cbc:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11 at
`/usr/local/bin/python`, PuLP 3.3.2 and nothing else besides pip (the shared
`runner/requirements.txt` stack is not installed). CBC 2.10.3 is the binary the wheel
ships, at `/usr/local/lib/python3.12/site-packages/pulp/solverdir/cbc/linux/i64/cbc`;
`PULP_CBC_CMD` is the only solver PuLP finds. The pin must stay below PuLP 4, which
removes both the bundled CBC and `PULP_CBC_CMD` that the runner calls. JSON is the
standard library's `json`. No edition or size limits.

Inside the container: no network, a read-only filesystem except `/tmp` (512 MB tmpfs, the
working directory, and `HOME`), user 65534, the submission and `request.json` under
`/input`. The image's entrypoint is the runner (`python /opt/runner/run.py`); for an ad
hoc run override it, e.g. `docker run --rm --network none --entrypoint sh
dcp-eval/pulp_cbc:v1 -c '...'`.

## Traps

- Enumeration (more than one solution requested) needs every variable inside a declared
  output, including those inside an output expression, to be `Integer`/`Binary` and to
  have finite lower and upper bounds; otherwise the run is `unsupported_capability`.
- An output variable in no constraint is added through its bound; with no bound at all
  the run is an `execution_error`.
- An unbounded objective is an `execution_error` ("The objective is unbounded").
- A fractional output value (more than 1e-6 from an integer) raises in the runner and is
  reported as `execution_error`.
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
