# hermax: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how hermax
(Python, MaxSAT) expresses it. Runner: [run.py](run.py), which takes `emit`, `finish` and
`mapped` from [runner/runtime.py](../../runner/runtime.py) and does its own solving.

## Submission file

One Python file, `model.py`. It may import `hermax` (which brings `pysat`) and the
standard library; nothing else is installed, and no other file of yours is staged.

## Entrypoint

```python
def build(instance) -> tuple[hermax.model.Model, dict]:
```

The runner imports the file and calls `build(instance)` once. It must return a 2-tuple
`(model, outputs)` with `model` a `hermax.model.Model`; the objective is never returned.
Anything the module prints goes to stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to variables of the
model, or nested `list`s/`tuple`s of them:

- a `Literal` (from `m.bool`) is reported as `true`/`false`, an `IntVar` as an `int`;
- a vector or matrix (`m.bool_vector`, `m.int_matrix`, ...) may be given whole and is
  decoded by hermax into nested lists;
- a linear expression (`PBExpr`, or a single weighted literal `Term`) with integer
  coefficients is summed by the runner. This is how an output too wide for one `IntVar`
  is declared, e.g. `sum(10**(9-i) * digit[i])` over 0..9 IntVars.

Plain Python values (`int`, `bool`) are not accepted (`execution_error`).

## Objective

Soft clauses on `model.obj`: `m.obj[w] += literal` pays `w` when the literal is
**false**, so minimising a literal's count pays on `~lit` and maximising pays on `lit`.
`m.obj += expr` is also accepted; the cost then includes the expression's lower bounds
(`m.obj += x` with `x` in 3..7 costs 3 at best). The runner always minimises that cost and
reads only whether one exists: `result.cost` is None when there are no soft clauses, which
makes the model a satisfaction problem.

## Solving

- The runner calls `model.solve(time_limit=left)` with hermax's defaults and forces no
  other setting: a model with soft clauses goes to hermax's RC2, a hard-only model to
  PySAT's Glucose 4 (`g4`).
- Status: `optimum`, or `sat` without soft clauses, is an answer; `unsat` is `unsat`
  (`complete` once something was emitted); `interrupted`, `interrupted_sat` and `unknown`
  are `timeout` (an unproven incumbent is never reported); `error` and any other status
  are `error`.
- Enumeration adds one blocking clause per answer over every `Literal` and `IntVar` under
  the declared outputs, including those a `PBExpr`/`Term` output sums (`x != v` per
  `IntVar`, the flipped literal per `Literal`), and re-solves. A repeated output value is
  re-solved, not emitted. It stops with `complete` on `unsat`, when nothing is left to
  block, or, for an optimisation, at the first answer whose cost exceeds the first one.
- Time: one deadline from the runner's start; each solve gets the time left, and an
  expired deadline before a solve is `timeout`. There is no SIGALRM, so `build` itself is
  unbounded until the evaluator stops the container.

## Compilation

None.

## Environment

Image `dcp-eval/hermax:v1`: Python 3.12.11 (`/usr/local/bin/python`), hermax 1.2.5 with
python-sat 1.9.dev16 (and `six`); the standard library (`json` included) and nothing else.
`Model.solve` defaults to RC2 for soft clauses and Glucose 4 otherwise, although
`metadata.yaml` names EvalMaxSAT. No licence, no environment variables of note, no
network in the container. For an ad hoc run, `--entrypoint sh` bypasses
`/opt/runner/run.py`.

## Traps

- `build` has no time limit of its own (see Solving): a slow build ends as
  `execution_timeout`. Tying the objective to an auxiliary `IntVar`
  (`sum(...) == total`) is the usual way to spend the budget inside `build`: keep the
  objective as soft clauses.
- With `solution_limit > 1`, an output expression must sum only literals and `IntVar`s:
  a derived integer such as `x // 3` inside it cannot be blocked (`execution_error`).
  Tie it to an `IntVar` first.
- Because enumeration blocks the literals and variables an expression output sums, every
  other combination with the same total costs a re-solve.
- A `Literal` output is reported as a Boolean. For an output the brief declares as a
  0/1 integer, use `m.int(name, 0, 1)`.

## Example

The pilot fixture [tests/fixtures/model_hermax.py](../../tests/fixtures/model_hermax.py)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```python
from hermax.model import Model


def build(instance):
    n = instance["n"]
    m = Model()
    x = m.int("x", 0, n)
    y = m.int("y", 0, n)
    if not instance["optimize"]:
        m &= (x + y == n)
        return m, {"x": x, "y": y}
    m &= (x + y >= n)
    m.obj += (x + y)
    return m, {"x": x, "y": y}
```
