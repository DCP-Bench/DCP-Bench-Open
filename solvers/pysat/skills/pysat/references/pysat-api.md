# The PySAT surface a submission uses, exactly

Signatures taken from python-sat 1.9.dev15 as installed in the integration
image. The image installs nothing of this repository's own beside `run.py`, so
this is the whole vocabulary available to a submission.

## Identifiers

```python
from pysat.formula import CNF, IDPool

pool = IDPool()
lit = pool.id(key)        # a fresh positive literal per distinct key
```

One pool per submission. Every encoder call takes `vpool=pool` so its auxiliary
variables come from the same counter.

## Clauses

```python
cnf = CNF()
cnf.append([a, -b])            # one clause
cnf.extend(other.clauses)      # merge an encoder's output
cnf.nv                         # highest variable id
```

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

Each returns a formula; take `.clauses`.

`EncType` covers `pairwise`, `seqcounter`, `sortnetwrk`, `cardnetwrk`,
`bitwise`, `ladder`, `totalizer`, `mtotalizer`, `kmtotalizer`.

**`PBEnc` accepts negative weights.** Verified: `PBEnc.equals` over
`[3, -1, -2, 5, -5, 4]` with bound 0 solved to `[3, -1, -2]`. Shifting terms to
make weights non-negative is unnecessary.

## Finite-domain integers

```python
from pysat.integer import Integer, IntegerEngine

Integer(name, lb, ub, encoding='direct', card_enc=1, vpool=None, numeric='float')
    .decode(model) -> int          # the value in a solver model
    .equals(value) -> int          # the literal for "x == value"
    .atmost(v) / .atleast(v) / .le(v) / .ge(v)
    .abs()  .as_expr()  .linearize()  .domain_clauses()  .encode()

IntegerEngine(vars=None, constraints=None, adaptive=True, vpool=None)
    .add_var(var)
    .add_linear(constraint, reified=False)      # takes a comparison
    .add_alldifferent(vars, reified=False)      # takes Integer objects
    .add_equal(left, right, reified=False)      # takes Integer objects
    .add_not_equal(left, right, reified=False)  # takes Integer objects
    .clausify(cardenc=1, pbenc=0) -> CNF
    .decode(lits, vars=None)
```

Comparisons build the constraint objects `add_linear` wants:

| Written | Produces |
| --- | --- |
| `a + b <= 5` | `('linear', ...)` |
| `3 * a + 2 * b >= 4` | `('linear', ...)` |
| `a - b != 3` | `('ne_linear', ...)` |
| `a != b` | `('ne', Integer, Integer)` |

`add_alldifferent`, `add_equal` and `add_not_equal` reach for `.vpool` on their
arguments, so they raise `AttributeError` on a `LinearExpr`. Route expressions
through `add_linear`.

The three domain encodings are **direct** (a literal per value, exactly one
true), **order** (a literal per threshold, with monotonicity) and **coupled**
(both, channelled). Cost grows with the size of the domain, so bound variables
by what the instance can reach.

## Solving

```python
from pysat.solvers import Solver

with Solver(name="glucose42", bootstrap_with=cnf) as s:
    ok = s.solve_limited(expect_interrupt=True)
    model = s.get_model()
```

The runner owns this part. **CaDiCaL and Lingeling raise
`NotImplementedError: Limited solve is currently unsupported`**, so neither can
be interrupted mid-search; Glucose, Minisat, Maplesat and MergeSat all stop
within a tenth of a second.

## Measured costs

Pigeonhole with `Integer` plus `add_alldifferent`, refuted by Glucose 4.2:

| Pigeons into holes | Clauses | Time |
| --- | --- | --- |
| 12 into 11 | 712 | 4.5 s |
| 13 into 12 | 849 | 11.0 s |
| 14 into 13 | 998 | 24.6 s |
| 15 into 14 | 1159 | 70.9 s |

Eight-queens clausifies to 8264 clauses over 4538 variables in 0.02 s.
