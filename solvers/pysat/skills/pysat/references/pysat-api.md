# PySAT API reference

Signatures taken from python-sat 1.9.dev15 (Python 3.12). Full docs:
[formula](https://pysathq.github.io/docs/html/api/formula.html),
[card](https://pysathq.github.io/docs/html/api/card.html),
[pb](https://pysathq.github.io/docs/html/api/pb.html),
[integer](https://pysathq.github.io/docs/html/api/integer.html),
[solvers](https://pysathq.github.io/docs/html/api/solvers.html),
[RC2](https://pysathq.github.io/docs/html/api/examples/rc2.html).

## Identifiers and clauses

```python
from pysat.formula import CNF, IDPool, WCNF

pool = IDPool()
lit = pool.id(key)            # a fresh positive literal per distinct key

cnf = CNF()
cnf.append([a, -b])           # one clause
cnf.extend(other.clauses)     # merge an encoder's output
cnf.nv                        # highest variable id

wcnf = WCNF()
wcnf.append([a, b])           # hard clause (no weight)
wcnf.append([-a], weight=3)   # soft clause, positive integer weight
```

Use one `IDPool` per model and pass `vpool=pool` to every encoder, so auxiliary
variables never collide.

## Cardinality and pseudo-Boolean

```python
from pysat.card import CardEnc, EncType
from pysat.pb import PBEnc

CardEnc.atmost(lits, bound, vpool=pool, encoding=EncType.seqcounter)
CardEnc.atleast(lits, bound, vpool=pool, encoding=...)
CardEnc.equals(lits, bound, vpool=pool, encoding=...)

PBEnc.leq(lits, weights, bound, vpool=pool)
PBEnc.geq(lits, weights, bound, vpool=pool)
PBEnc.equals(lits, weights, bound, vpool=pool)
```

Each returns a formula; take `.clauses`. `EncType` covers `pairwise`, `seqcounter`,
`sortnetwrk`, `cardnetwrk`, `bitwise`, `ladder`, `totalizer`, `mtotalizer`,
`kmtotalizer`. `seqcounter` is a sound default.

`PBEnc` accepts negative weights: `PBEnc.leq` over `[2, -1, 1]` with bound 0 gives
clauses that force the terms to sum to at most zero. No shifting is needed.

## Finite-domain integers

```python
from pysat.integer import Integer, IntegerEngine

Integer(name, lb, ub, encoding='direct', card_enc=1, vpool=None, numeric='float')
    .decode(model) -> int          # value under a dense model (see Solving)
    .equals(value) -> int          # literal for "x == value"; direct or coupled only
    .ge(value) -> int              # literal for "x >= value"; order or coupled only
    .atmost(v) / .atleast(v) / .le(v) / .ge(v)

IntegerEngine(vars=None, constraints=None, adaptive=True, vpool=None)
    .add_var(var)
    .add_linear(constraint, reified=False)      # comparison; returns a selector if reified
    .add_alldifferent(vars, reified=False)      # Integer objects only
    .add_equal(left, right, reified=False)      # Integer objects only
    .add_not_equal(left, right, reified=False)  # Integer objects only
    .clausify(cardenc=1, pbenc=0) -> CNF
    .decode(lits, vars=None)
```

| Written | Produces |
|---|---|
| `a + b <= 5` | linear constraint |
| `3 * a + 2 * b >= 4` | linear constraint |
| `a - b != 3` | not-equal constraint over a linear expression |
| `a != b` | not-equal between two Integers |

| Encoding | Literals | `equals(v)` | `ge(v)` | `add_not_equal` on left side |
|---|---|---|---|---|
| `direct` | one per value, exactly one true | yes | no (`Order encoding is disabled`) | yes |
| `order` | one per threshold, monotone | no (`Direct encoding is disabled`) | yes | no (`requires direct or coupled encoding on left`) |
| `coupled` | both, channelled | yes | yes | yes |

Cost grows with the domain size, so bound each variable by what the instance can reach.

Literal methods, measured on `Integer("x", 1, 4)`:

| Call | `order` | `coupled` | `direct` |
|---|---|---|---|
| `x.ge(v)`, `x.atleast(v)` | literal for `x >= v`, valid for `lb+1 <= v <= ub` | same | `Order encoding is disabled` |
| `x.le(v)`, `x.atmost(v)` | `-x.ge(v+1)`, i.e. `x <= v`, valid for `lb <= v <= ub-1` | same | `Order encoding is disabled` |
| `x.equals(v)` | `Direct encoding is disabled` | literal for `x = v` | literal for `x = v` |
| `engine.add_linear(x >= 3)` | constraint | constraint | constraint |
| `engine.add_linear(x >= 3, reified=True)` | selector literal | selector literal | selector literal |

Out-of-range values raise `AssertionError: Value is outside the order domain` (or `... domain` for `equals`).

`add_linear(c, reified=True)` returns `None` when the bounds already make `c` true, and a literal otherwise (also when `c` is impossible: the literal is then forced false). A `None` must not reach a clause, so skip any clause that contains it, since that clause is already satisfied.

Passing a `LinearExpr` to `add_alldifferent`, `add_equal` or `add_not_equal` fails
(`TypeError` or `AttributeError`). Put expressions through `add_linear`.

A variable created after its engine needs `engine.add_var(v)`. Call `clausify()`
once, after all constraints are added, and extend the returned CNF for anything
outside the engine:

```python
cnf = engine.clausify()
cnf.extend(CardEnc.atmost(lits=flags, bound=k, vpool=pool).clauses)
```

Wide values: `Integer(name, 0, 10**10)` registers one variable per value and can run
out of memory. Declare the value as a sum over small Integers instead, for example
`sum(2**k * bit_k)` over 35 Integers with domain 0..1 (a `pysat.integer.LinearExpr`;
`terms` maps Integer to coefficient, `const` holds the constant).

## Solving

```python
from pysat.solvers import Solver

with Solver(name="glucose42", bootstrap_with=cnf.clauses) as s:
    ok = s.solve()                       # True, False
    model = s.get_model()                # signed literals, positive = true
```

| Solver name | `solve()` | `solve_limited()` and `interrupt()` from another thread |
|---|---|---|
| `glucose42` (Glucose 4.2) | yes | honoured: a 14-into-13 pigeonhole returned `None` 0.15 s after a 1 s timer |
| `minisat22`, `mergesat3`, `maplechrono` | yes | `solve_limited` accepted; interrupt not tested |
| `cadical195` | yes | `solve_limited` accepted, but `interrupt()` was not honoured: the same pigeonhole ran past a 100 s timeout; `clear_interrupt()` raises `NotImplementedError: Limited solve is currently unsupported by CaDiCaL.` |
| `lingeling` | yes | `solve_limited` raises `NotImplementedError: Limited solve is currently unsupported by Lingeling.` |

Use `glucose42` when a time limit has to stop the search.

## Core-guided MaxSAT (RC2)

```python
from pysat.examples.rc2 import RC2Stratified

rc2 = RC2Stratified(wcnf, solver="glucose42")
model = rc2.compute()        # list of signed literals, or None
cost = rc2.cost              # total weight of falsified soft clauses
rc2.add_clause([...])        # hard clause; the next compute() respects it
rc2.delete()
```

- `RC2Stratified` works through soft clauses heaviest first. On a 15-item knapsack
  with one soft clause per item weighted by its value, plain `RC2` did not prove the
  optimum in 178 s, and `RC2Stratified` proved it in 0.13 s.
- An interrupted search returns `None` and leaves `rc2.interrupted` set. A returned
  model is optimal.
- `CNF.weighted()` turns every clause into a soft clause of weight 1; use
  `WCNF().extend(cnf.clauses)` for hard clauses.
- After `add_clause`, `compute()` returns the best model that respects the new clause.
- `compute()` returns only the variables that occur in the formula.
- An unsatisfiable hard part gives `None`.

## Measured costs

Pigeonhole with `Integer` plus `add_alldifferent`, refuted by Glucose 4.2:

| Pigeons into holes | Clauses | Time |
|---|---|---|
| 12 into 11 | 712 | 4.5 s |
| 13 into 12 | 849 | 11.0 s |
| 14 into 13 | 998 | 24.6 s |
| 15 into 14 | 1159 | 70.9 s |

Eight-queens clausifies to 8264 clauses over 4538 variables in 0.02 s.

Job shop ft06 (6 x 6), `clausify()` only, head/tail start bounds, `order` starts:

| Horizon | Makespan encoding | Hard clauses | Time |
|---|---|---|---|
| 197 (sum of durations), `order` | `order` | 13.6M | 21 s |
| 197, `direct` starts | `direct` | 11.9M | 19 s |
| 197, `order` starts, no head/tail bounds | `order` | 18.2M | 30 s |
| 80 | `coupled` | 1.16M | 1.4 s |
| 68 (greedy schedule) | `coupled` | 0.64M | 0.7 s |
| 55 (optimum) | `direct` starts and makespan | 0.23M | 0.3 s |

Full solve with the greedy horizon and unit-weight threshold softs: optimum 55 in about 3 s (assets/jobshop). With horizon 197 and the same softs, RC2 took about 108 s in total.
