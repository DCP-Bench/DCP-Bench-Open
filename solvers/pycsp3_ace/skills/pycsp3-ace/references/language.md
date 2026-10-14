# PyCSP3 2.6.1 reference (tested)

Every construct here was run through the `pycsp3_ace` image (pycsp3 2.6.1, ACE 2.6) with a
harness that runs one solve round, or through `evaluation.check` on a benchmark problem.
Items under "Dropped" failed; do not use them. Examples with code are in
[examples.md](examples.md).

## Model file

Outputs: `x`.

```python
from pycsp3 import *

x = VarArray(size=4, dom=range(4))
satisfy(AllDifferent(x))
```

- `from pycsp3 import *` at the top. Module-level code runs once per solve round.
- One declaration per line. `a, b = Var(dom=range(3)), Var(dom=range(3))` fails with
  `AssertionError: Every simple declaration must be on its own line`.
- The variable name comes from the Python name on the declaration line.
- `solve()` is not allowed in a model. The runner calls it and raises if the model does.

## Variables and domains

- `Var(dom=range(lo, hi))` (exclusive upper bound, as Python `range`). A list `[10, 20, 30]`
  or a set `{0, 1}` also works. Booleans: `dom={0, 1}`, reported as 0/1.
- `VarArray(size=n, dom=...)` gives a list of n variables.
- `VarArray(size=[r, c], dom=...)` gives a nested list: `grid[i][j]`. `grid[:, j]` is column j.
- A variable that no constraint mentions is not reported by ACE, and the runner refuses the
  output. A whole output with no constraint raises `ValueError: declared output 'z' has a
  variable that no constraint mentions`. A single element of an array raises `ValueError: a
  declared output has no determined value in the solution`. Constrain every element.

## Relations and arithmetic

- Operators build constraints and expressions: `x[0] + 2 * x[1] < x[2]`, `x[0] != x[1]`,
  `abs`, `//`, `%`.
- Integers only. `Sum(x[0] * 0.5, x[1])` fails with `ValueError: Problem: bad form of predicate 0.5`.
- `Sum(x[0] * 3, x[1] * 2, x[2] * 5) <= 7` (several terms as separate arguments) and
  `Sum(w[i] * x[i] for i in range(n))` (generator) both work.
- `Sum(b)` over Boolean variables counts the true ones.

## Globals (tested)

- `AllDifferent(list)`, `Increasing(list, strict=True)`.
- `Count(x, value=1) == 2`, `NValues(x) >= 2`, `Exist(x, value=2)`.
- `Cardinality(x, occurrences={0: range(1, 4), 1: 2, 2: range(1, 4)}, closed=True)`.
  `closed=True` forces every variable to take one of the keys.
- `Minimum(x) == lo`, `Maximum(x) == hi`.
- `MaximumArg(x, rank=TypeRank.FIRST) == i` (the index of the maximum). A plain string
  `rank='first'` fails with `TypeError: Wrong type for first`.
- `Table(scope=x, supports=[(0, 1, 2), ...])`, `Table(scope=x, supports=[(0, 1, '*')])`, and
  `Table(scope=x, conflicts=[(0, 0)])`.
- `(x[0], x[1]) in {(0, 1), (1, 2)}` (positive table). `ANY` or `*` matches any value:
  `(x[0], x[1], x[2]) in {(0, 1, ANY), (2, ANY, 1)}`.
- `Element`: `v == t[idx]` where `t` is a VarArray (verified) and `idx` is a variable. Constant lists were not run.
- `Cumulative(origins=s, lengths=d, heights=h) <= 2`, and
  `Cumulative(tasks=[(origin, length, height), ...]) <= 1`.
- `NoOverlap(origins=s, lengths=d)`.
- `Circuit(x)`: successors form one Hamiltonian cycle (0-based). `Channel(x, y)`: y is the inverse
  of x.
- `LexIncreasing([x, y])`: vectors in lexicographic order. Use it to break symmetry on rows.
- `Regular(scope=x, automaton=Automaton(start=..., transitions=[...], final=...))`.
- `BinPacking(b, sizes=w, limits=[4, 3])`: bin i has capacity `limits[i]`.
- `Knapsack(x, weights=w, wlimit=c, profits=p) >= 6`.
- `Hamming(x, y) == 2`: positions where x and y differ.

## Conditionals and connectives (tested)

- `imply(x[0] == 3, x[1] == 0)`.
- `If(x[2] == 1, Then=x[0] == 3, Else=x[0] == 0)`. `Then=[c1, c2]` takes a list.
- `(b == 1) == (Sum(x) > 4)`: reification through a Boolean variable.
- `Or(c1, c2)`, `And(c1, c2)`, `Xor(c1, c2)`, `Iff(c1, c2)` take constraints as arguments.

## Constraint posting

- `satisfy(c1, c2, ...)`. A list or a generator is flattened:
  `satisfy(x[i] != x[i + 1] for i in range(n - 1))`.
- `satisfy(Cumulative(...) <= 2)`: a relation on a global is a constraint.

## Objectives (tested)

- `minimize(term)` or `maximize(term)`, at most one. The term is a variable or an expression:
  `minimize(Sum(x[i] * (i + 1) for i in range(3)))`, `maximize(Sum(x))`.
- A generator with a filter inside `Sum` works: `Sum(w[i] * x[i] for i in range(n) if w[i] > 0)`.

## Dropped (failed in 2.6.1)

| Construct | Error |
|---|---|
| `Not(c)`, also `Not(AllDifferent(x))`, `Not(x[0] == 0)` | `TypeError: bad operand type for unary ~: 'list'`. Write the negated relation (`!=`, `>=`) instead |
| `(x[0], x[1]) notin {(0, 0)}` | `SyntaxError: invalid syntax` |
| `solve()` in the model | `RuntimeError: the model must not call solve(); the runner solves it` |
| `a, b = Var(...), Var(...)` on one line | `AssertionError: Every simple declaration must be on its own line` |
| Float in an expression | `ValueError: Problem: bad form of predicate 0.5` |

## Not run

Not verified, not used in examples: `Mdd`, `Flow`, `Slide`, `Adhoc`, `Precedence`, `Clause`,
`Increasing(..., lengths=...)`, `LexIncreasing(..., matrix=True)`, per-cell domains with a
lambda, `Decreasing`, `Automaton` beyond the example above. If one is needed, run it first.

## Other things measured

- `data._SHIP` and `data["_SHIP"]` both read a field whose name starts with an underscore.
- Ragged input lists (`data.rows[i]` of different lengths) are plain Python lists.
