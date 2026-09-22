---
name: pysat
description: Write a DCP-Bench submission for the pysat integration - one Python file defining build(instance) that returns a pysat.formula.CNF built with PySAT's own IDPool, CardEnc, PBEnc and pysat.integer. Use when generating or repairing a model for solver ID pysat.
---

# PySAT submissions

A submission is one Python file defining `build(instance)`, written against
PySAT itself:

```python
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def build(instance):
    ...
    return cnf, outputs
```

`cnf` is a `pysat.formula.CNF`. `outputs` maps each name the brief declares to
a literal (a positive `int` from the pool), a `pysat.integer.Integer`, or
nested lists of those.

## This integration cannot optimise

PySAT is a SAT solver: it answers satisfiable or not. The metadata declares
`optimization: false`, and the runner **refuses** a submission that returns an
objective rather than solving it as though the objective were absent. So only
take problems whose reference has no objective. A problem with one is a pair to
leave alone, not a model to write.

## Boolean models

Allocate literals from one `IDPool` and hand every encoder the same pool, so
the auxiliary variables they introduce never collide.

```python
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.pb import PBEnc


def build(instance):
    weights = instance["weights"]
    capacity = instance["capacity"]
    n = len(weights)

    pool = IDPool()
    x = [pool.id(("x", j)) for j in range(n)]
    cnf = CNF()
    cnf.extend(CardEnc.atmost(lits=x, bound=3, vpool=pool,
                              encoding=EncType.seqcounter).clauses)
    cnf.extend(PBEnc.leq(lits=x, weights=weights, bound=capacity,
                         vpool=pool).clauses)
    cnf.append([x[0], -x[1]])          # an ordinary clause
    return cnf, {"x": x}
```

- `CardEnc.atmost / atleast / equals(lits, bound, vpool, encoding)` for
  unweighted counting. `EncType.seqcounter` is a sound default.
- `PBEnc.leq / geq / equals(lits, weights, bound, vpool)` for weighted sums.
  **Negative weights are accepted directly** — there is no need to shift terms
  or flip literals by hand.
- A negated literal is `-lit`. A clause is a list of literals.

## Integer models

`pysat.integer` gives finite-domain variables that clausify into the CNF.

```python
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]

    pool = IDPool()
    queens = [Integer(f"q{i}", 1, n, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=queens, vpool=pool)
    engine.add_alldifferent(queens)
    for i in range(n):
        for j in range(i + 1, n):
            engine.add_linear(queens[i] - queens[j] != i - j)
            engine.add_linear(queens[i] - queens[j] != j - i)
    return engine.clausify(), {"queens": queens}
```

- `Integer(name, lb, ub, encoding="direct", vpool=pool)`. The encodings are
  `"direct"` (one literal per value), `"order"` (one per threshold) and
  `"coupled"` (both, channelled).
- Comparisons on `Integer` and on sums of them produce constraints:
  `engine.add_linear(x + y == n)`, `engine.add_linear(3 * a - b <= 7)`,
  `engine.add_linear(a - b != 4)`.
- `engine.add_alldifferent(vars)`, `engine.add_not_equal(a, b)` and
  `engine.add_equal(a, b)` take `Integer` objects, **not** expressions. Pass an
  expression through `add_linear` instead.
- `engine.clausify()` returns the `CNF` to hand back. Call it once, at the end.
- A variable created after the engine needs `engine.add_var(v)`.

To mix the two, build the integer part first and extend it:

```python
cnf = engine.clausify()
cnf.extend(CardEnc.atmost(lits=flags, bound=k, vpool=pool).clauses)
```

## Outputs

Booleans render as `true`/`false` from their literal. If the brief declares 0/1
integers, use `Integer(name, 0, 1, vpool=pool)` so the value comes out as a
number.

An `Integer` in `outputs` is decoded by the runner; a literal is reported by
whether it is true. Do not put values you computed in Python into `outputs` —
every declared output has to come from the solver.

## What the runner does

1. Imports the submission and calls `build(instance)`.
2. Solves the CNF with Glucose 4.2, under the remaining budget. CaDiCaL and
   Lingeling are not options: PySAT raises `NotImplementedError` for limited
   solve on both, so neither can be stopped mid-search.
3. Emits the solution, then blocks the **declared outputs** and solves again,
   so enumeration counts answers the problem can tell apart.
4. Ends with `complete` when the formula goes unsatisfiable, `limit` at the
   solution limit, or `timeout`.

## Reasoning to record

Say where each variable's domain bound comes from in the instance. For an
`Integer`, say which encoding you chose and why, since a direct encoding over a
wide domain is the expensive shape here.
