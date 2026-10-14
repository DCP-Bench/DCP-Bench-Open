---
name: pysat
description: Write a DCP-Bench submission for the pysat integration - one Python file defining build(instance) that returns a pysat.formula.CNF, or a pysat.formula.WCNF whose soft clauses state the objective, built with PySAT's own IDPool, CardEnc, PBEnc and pysat.integer. Use when generating or repairing a model for solver ID pysat.
---

# PySAT submissions

A submission is one Python file defining `build(instance)`, written against
PySAT itself:

```python
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def build(instance):
    ...
    return formula, outputs
```

`formula` is a `pysat.formula.CNF` for a problem without an objective, or a
`pysat.formula.WCNF` for one with an objective (next section). `outputs` maps
each name the brief declares to a literal (a positive `int` from the pool), a
`pysat.integer.Integer`, or nested lists of those.

## Objectives are soft clauses

PySAT optimises through MaxSAT. The runner hands a `WCNF` with soft clauses to
RC2 in its stratified form (`pysat.examples.rc2.RC2Stratified`), which finds
an assignment that satisfies every hard clause and **minimises the total
weight of the soft clauses it falsifies**.
The constraints are the hard clauses; the objective is the soft clauses, and
nothing else. Returning an objective as a third value is refused.

```python
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]
    pool = IDPool()
    x = Integer("x", 0, n, vpool=pool)
    y = Integer("y", 0, n, vpool=pool)
    engine = IntegerEngine(vars=[x, y], vpool=pool)
    engine.add_linear(x + y >= n)                     # a constraint

    formula = WCNF()
    formula.extend(engine.clausify().clauses)         # hard: every constraint
    # Minimise x + y: an assignment pays v whenever x or y takes the value v.
    for v in range(1, n + 1):
        for var in (x, y):
            formula.append([-var.equals(v)], weight=v)
    return formula, {"x": x, "y": y}
```

- **`formula.extend(cnf.clauses)` adds hard clauses. `cnf.weighted()` does
  not:** it turns every clause into a *soft* clause of weight 1, so the
  constraints silently become optional and the answer is wrong.
- `formula.append(clause, weight=w)` adds a soft clause; `w` must be a
  positive integer. Leave out a clause whose weight would be zero.
- **Minimising** a quantity: pay its value, as above. A single literal `l`
  counted with weight `w` is the soft clause `[-l]` with weight `w`.
- **Maximising** a quantity `q` with a known upper bound `U`: minimise the
  shortfall `U - q`. For a sum of literals, the soft clause `[l]` with weight
  `w` pays `w` exactly when `l` is false. For an `Integer`, pay `U - v` for
  each value `v`, as in the example with `v` replaced by `n - v`.
- With `encoding="order"` or `"coupled"`, `x` itself is the soft clauses
  `[-x.ge(v)]` with weight 1 for each threshold `v` in `lb + 1 .. ub`, plus the
  constant `lb`. On the default `"direct"` encoding `x.ge(v)` raises
  `AssertionError: Order encoding is disabled`; use `x.equals(v)` there.
- A `WCNF` with no soft clauses is solved as a satisfaction problem.

RC2 reports a model only once it has proved the optimum, so an instance that
runs out of time ends as a timeout, never as a merely good answer.

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
whether it is true.

An `Integer` creates one variable per value (direct) or per threshold
(order), so an output with millions of possible values does not fit in
memory. Declare such an output as a `LinearExpr` over small Integers instead,
and the runner reads its value off the assignment:

```python
bits = [Integer(f"b{k}", 0, 1, vpool=pool) for k in range(35)]
number = sum(2 ** k * bit for k, bit in enumerate(bits))   # up to 2**35 - 1
engine.add_linear(number == ...)                            # constrain it
return engine.clausify(), {"number": number}
```

Digits work the same way: `sum(10 ** (9 - i) * digit[i] for i in range(10))`
over 0..9 Integers. The runner blocks the summed Integers when enumerating, so
a second combination with the same total is skipped rather than reported
twice. Coefficients must be integers. Do not put values you computed in Python into `outputs` —
every declared output has to come from the solver.

## What the runner does

1. Imports the submission and calls `build(instance)`.
2. Solves a `CNF` with Glucose 4.2, and a `WCNF` with soft clauses with
   stratified RC2 over the same Glucose, under the remaining budget. CaDiCaL and Lingeling are
   not options: PySAT raises `NotImplementedError` for limited solve on both,
   so neither can be stopped mid-search.
3. Emits the solution, then blocks the **declared outputs** and solves again,
   so enumeration counts answers the problem can tell apart. When optimising,
   it stops as soon as the next answer costs more than the optimum.
4. Ends with `complete` when the formula goes unsatisfiable or the next answer
   is worse, `limit` at the solution limit, or `timeout`.

## Reasoning to record

Say where each variable's domain bound comes from in the instance. For an
`Integer`, say which encoding you chose and why, since a direct encoding over a
wide domain is the expensive shape here. For an objective, say in a comment
what each group of soft clauses pays and, when maximising, which upper bound
the shortfall is measured from.
