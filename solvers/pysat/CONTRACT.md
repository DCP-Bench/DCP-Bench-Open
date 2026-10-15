# pysat: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how PySAT
(Python, SAT and MaxSAT) expresses it. Runner: [run.py](run.py), which takes only `emit`
and `finish` from [runner/runtime.py](../../runner/runtime.py) and does its own solving.

## Submission file

One Python file, `model.py`. It may import `pysat` (python-sat, with pblib for `PBEnc`)
and the standard library; nothing else is installed, and no other file of yours is staged.

## Entrypoint

```python
def build(instance) -> tuple[pysat.formula.CNF | pysat.formula.WCNF, dict]:
```

The runner imports the file and calls `build(instance)` once. It must return a 2-tuple
`(formula, outputs)`; a third value (an objective) is refused with an error. Anything the
module prints goes to stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a leaf or a nested
`list`/`tuple` of leaves. A leaf is one of:

- a Python `int`: a **literal**, reported as `true`/`false` by whether that variable is
  true in the model;
- a Python `bool`: a constant, reported as is;
- a `pysat.integer.Integer`: reported as `decode(model)`;
- a `pysat.integer.LinearExpr` whose terms are all `Integer`s and whose coefficients
  are integers: reported as its value. This is how an output too wide for one `Integer`
  is declared, e.g. `sum(2**k * bit[k])` over 0..1 Integers.

Anything else is an `execution_error`.

## Objective

The **soft clauses of a `WCNF`**: `formula.append(clause, weight=w)`. The runner hands a
`WCNF` with soft clauses to stratified RC2 (`RC2Stratified`), which minimises the total
weight of the soft clauses an assignment **falsifies**; maximising pays the shortfall.
Hard clauses are the constraints. A `CNF`, or a `WCNF` without soft clauses (only its
hard clauses are kept), is a satisfaction problem solved with Glucose 4.2.

## Compilation

None.

## Environment

Image `dcp-eval/pysat:v1`: Python 3.12.11, python-sat[pblib] 1.9.dev15. SAT solver
`glucose42`, also the oracle under RC2. The budget covers `build` as well as the search.

## Traps

- Every `int` in `outputs` is read as a literal, never as a number: a constant `3` is
  reported as "variable 3 is true". A negative literal `-v` is always reported `false`;
  declare the positive pool id.
- A literal is reported as a Boolean. For an output the brief declares as a 0/1 integer,
  use `Integer(name, 0, 1, vpool=pool)`.
- `cnf.weighted()` turns every clause into a weight-1 soft clause, which the runner then
  reads as objective, not constraint. Add hard clauses with `formula.extend(cnf.clauses)`.
- Enumeration blocks the declared outputs: for a `LinearExpr` it blocks the combination
  of its Integers, so another combination with the same total is re-solved and skipped.
  For an optimisation, enumeration stops at the first answer costlier than the optimum.

## Example

The pilot fixture [tests/fixtures/model_pysat.py](../../tests/fixtures/model_pysat.py)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```python
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]
    pool = IDPool()
    x = Integer("x", 0, n, vpool=pool)
    y = Integer("y", 0, n, vpool=pool)
    engine = IntegerEngine(vars=[x, y], vpool=pool)
    if not instance["optimize"]:
        engine.add_linear(x + y == n)
        return engine.clausify(), {"x": x, "y": y}
    engine.add_linear(x + y >= n)
    # The objective as soft clauses: an assignment pays `cost` whenever x or y
    # takes the value v, so the total paid is x + y.
    formula = WCNF()
    formula.extend(engine.clausify().clauses)
    for v, cost in ((v, v) for v in range(n + 1)):
        if cost > 0:
            formula.append([-x.equals(v)], weight=cost)
            formula.append([-y.equals(v)], weight=cost)
    return formula, {"x": x, "y": y}
```
