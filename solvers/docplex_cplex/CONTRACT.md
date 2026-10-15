# docplex_cplex: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how DOcplex
(Python, CPLEX) expresses it. Runner: [run.py](run.py), which takes only `emit` and
`finish` from [runner/runtime.py](../../runner/runtime.py) and does its own solving.

## Submission file

One Python file, `model.py`. It may import `docplex` and the standard library; nothing
else is installed (no NumPy), and no other file of yours is staged.

## Entrypoint

```python
def build(instance) -> tuple[docplex.mp.model.Model, dict]:
```

The runner imports the file and calls `build(instance)` once. It must return a 2-tuple
(not a list) `(model, outputs)` with `model` a `docplex.mp.model.Model`. Anything the
module prints goes to stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a docplex variable,
a linear expression, a Python integer or Boolean, or a nested `list`/`tuple` of these.
Integer and binary variables are rounded to the nearest integer and linear expressions
are evaluated over the rounded values. A `binary_var` is reported as `0`/`1`, not as a
Boolean. A value that is not within 1e-6 of an integer is rejected (`execution_error`).

## Objective

`model.minimize(expr)` or `model.maximize(expr)`; the runner reads
`model.has_objective()`. No call (or `minimize(0)`) is a satisfaction problem. The runner
sets `threads = 1`, `mip.tolerances.mipgap = 0` and the time limit over yours; other
parameters you set are kept.

## Compilation

None.

## Environment

Image `dcp-eval/docplex_cplex:v1`: Python 3.12.11, docplex 2.32.264 on the cplex
22.2.0.1 wheel (CPLEX Community Edition, no licence file, no network). One thread.

## Traps

- The Community Edition refuses a model above 1000 variables or 1000 constraints
  (indicator constraints count). That raises `DOcplexLimitsExceeded`, reported as
  `unsupported`, which the evaluator records as `unsupported_capability`; size the
  model for the largest instance. Enumeration adds rows of its own: one range pinning
  the objective, one no-good per extra solution, and per general-integer output
  variable up to two binaries and two indicators.
- With `solution_limit > 1`, any continuous variable under an output is `unsupported`.
  That includes the hidden continuous variable of `model.abs`, `model.max` and
  `model.min`: tie such a value to an `integer_var` and declare that instead.
- `*_var_matrix` and `*_var_dict` return dicts. Keyed by tuples they crash serialisation
  (`execution_error`); keyed by ints they become a JSON object (`invalid_output`).
  Return lists: `[[x[i, j] for j in cols] for i in rows]`.
- The no-good is over the variables an output is built from, not its value: an output
  expression over many variables makes the runner re-solve through every assignment
  with the same value. Declare such an output as its own integer variable.
- The old skill says a constant objective means satisfaction; only a zero one does.

## Example

The pilot fixture [tests/fixtures/model_docplex.py](../../tests/fixtures/model_docplex.py)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```python
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]
    model = Model()
    x = model.integer_var(0, n, name="x")
    y = model.integer_var(0, n, name="y")
    if instance["optimize"]:
        model.add_constraint(x + y >= n)
        model.minimize(x + y)
    else:
        model.add_constraint(x + y == n)
    return model, {"x": x, "y": y}
```
