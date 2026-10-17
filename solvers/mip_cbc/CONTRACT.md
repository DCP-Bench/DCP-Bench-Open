# mip_cbc: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how Python-MIP with its default solver CBC expresses it. Runner: [run.py](run.py), which imports `emit` and `finish` from [runner/runtime.py](../../runner/runtime.py) and has its own build, solve and enumeration loop. The modelling reference is the standalone skill [mip-python](skills/mip-python/SKILL.md).

## Submission file

One Python file, `model.py`. It may import `mip` (Python-MIP 2.0.0) and the standard library. Nothing else is installed: no NumPy, no gurobipy, no highspy. No other file of yours is staged.

## Entrypoint

```python
def build(instance) -> tuple[mip.Model, dict]:
```

The runner imports the file and calls `build(instance)` once. It must return exactly a 2-tuple `(model, outputs)`, where `model` is a `mip.Model`; the runner checks the type. Anything the module prints goes to stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a `mip.Var`, a `mip.LinExpr` (a linear expression over variables), an integer or Boolean, or a nested `list`/`tuple`/`dict` of these with the declared shape. The runner reads `v.x` or `expr.x` after a solve that found a solution, rounds it, and rejects a value more than 1e-6 from an integer (`execution_error`). A `None` value (no solution) is also `execution_error`. Integers are emitted as JSON integers. A Python `bool` leaf stays a JSON boolean. A `mip.Var` declared as `BINARY` gives 0 or 1.

## Objective

Set on the model with `model.objective = expr` (a variable, a linear expression, or a number). The direction is the model's `sense`: `mip.Model(sense=mip.MAXIMIZE)` or `mip.MINIMIZE`, which is the default. A model is an optimisation when its objective has at least one term or a nonzero constant. Otherwise it is a satisfaction problem, whatever its `sense`. A bare `m += expr` is not an objective: a bare variable raises `TypeError`, and a bare expression is accepted and adds nothing. Use `m.objective`.

## Solving

- Forced after `build`, overriding anything the model set: `verbose = 0`, `threads = 1`, `max_mip_gap = 0`, `max_mip_gap_abs = 0`. With the gap at zero, CBC's `OPTIMAL` means proven (the default gap of 1e-4 lets it stop early with a suboptimal value). Every solve gets `max_seconds` equal to the time left in the budget.
- Status mapping (`OptimizationStatus` of the solve):
  - `OPTIMAL`: solved. For an optimisation this is the proven optimum; for a satisfaction problem it is a feasible point.
  - `INFEASIBLE`, `INT_INFEASIBLE`: `unsat` on the first solve, `complete` after a no-good.
  - `UNBOUNDED`: `error` "The objective is unbounded".
  - `FEASIBLE` on an optimisation: `timeout` ("Optimum not proven within the time limit"), with no solution emitted for that solve. On a satisfaction problem: `solved`, since any feasible point answers the question.
  - `NO_SOLUTION_FOUND`: `timeout`.
  - Any other status (`ERROR`, `OTHER`, `LOADED`, `CUTOFF`, `TRUNCATED`, `INF_OR_UNBD`): `error` with the message `RuntimeError: Python-MIP returned status ...`. `OTHER` is what a model with no variables returns.
- Enumeration (`solution_limit > 1`): every variable under a declared output, including those inside an output expression, must be `INTEGER` or `BINARY` with finite bounds, else `unsupported` with the reason. An optimisation first pins the objective within 1e-6 of the proven optimum (`>= best` and `<= best`, with the tolerance).
- Next solution: for each cut variable with current value `v` in `lb..ub`, a binary `_below_<k>_<i>` (`x <= v - 1 + (ub - v + 1) * b`) when `v > lb`, and a binary `_above_<k>_<i>` (`x >= v + 1 - (v + 1 - lb) * (1 - b)`) when `v < ub`. The sum of these binaries is at least 1. Then a fresh solve. A solution whose declared values repeat an earlier one is skipped, not emitted. Exhausted when the solve is infeasible, or when no cut variable can differ.
- Time: the budget runs from the start of the run (`build` included). A `SIGALRM` at `execution_timeout + 5` seconds becomes `timeout`. CBC's own limit is `max_seconds`, set from the time left.

## Compilation

None.

## Environment

Image `dcp-eval/mip_cbc:v1`, built on `python:3.12.11-slim-bookworm` pinned by digest: Python 3.12.11 at `/usr/local/bin/python`. Packages: `mip==2.0.0`, `cbcbox==2.935`, `cffi==2.1.1`, `pycparser==3.11`, and nothing else besides pip. `cbcbox` provides the CBC library (`CBC devel (git:146ce89)`, from the `cbc_dist` build; the image sets `CBCBOX_BUILD=generic`, so the non-AVX2 binary is used on every host). mip 2.0.0 ships no solver binary itself.

Selecting another solver fails inside the image: `solver_name="GRB"` raises `FileNotFoundError` (Gurobi not found), `solver_name="HiGHS"` raises `FileNotFoundError` (highspy not installed). `Model()` without a name uses CBC here. JSON is the standard library's `json`. No edition or size limits.

Inside the container: no network, a read-only filesystem except `/tmp` (512 MB tmpfs, the working directory and `HOME`), user 65534, and `/input` with the submission and `request.json` only. The entrypoint is the runner (`python /opt/runner/run.py`). For an ad hoc run, override it with `--entrypoint python`.

## Traps

- Declared outputs and objective terms must be linear. `x * y`, `abs(x)` and `x / y` raise an error at build time (`TypeError`); the runner reports it as `error` with the message.
- `x == 3` used as a Python condition is always true (it builds an expression). Use it inside `m += ...`.
- `m += 2 <= 3` (a constraint with no variables) is a `TypeError`.
- A binary variable with bounds other than 0 and 1 is a `ValueError` at build time.
- The runner overrides `threads`, `verbose`, `max_mip_gap` and `max_mip_gap_abs` after `build`. A submission cannot restore the default gap.
- A model with an unbounded objective is `error`, not `unsat`.
- A model with an infeasible relaxation and no integer point is `unsat` (CBC reports `INFEASIBLE`).
- Enumeration with a continuous or unbounded declared output is `unsupported`. A single solution works with a continuous output, if its value is integral within 1e-6.
- Variable names `_below_<k>_<i>` and `_above_<k>_<i>` are used by the runner's no-good cuts; do not use them.
- Declared outputs are read after the last solve. If a later solve in the enumeration times out, the solutions already emitted stand, and the status is `timeout`.

## Example

The pilot fixture [tests/fixtures/model_mip.py](../../tests/fixtures/model_mip.py) (instance fields `n`, `optimize`; outputs `x`, `y`):

```python
import mip


def build(instance):
    n = instance["n"]
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    x = model.add_var("x", lb=0, ub=n, var_type=mip.INTEGER)
    y = model.add_var("y", lb=0, ub=n, var_type=mip.INTEGER)
    if instance["optimize"]:
        model += x + y >= n
        model.objective = x + y
    else:
        model += x + y == n
    return model, {"x": x, "y": y}
```
