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
- Declare variables at module level, as one `VarArray` where possible. A `Var` without `id=`
  made in a loop, a comprehension, a helper function or a dict fails in pycsp3 (verified):
  `The identifier z is used twice`, `The variable identifier None is not valid` (helper),
  `The variable identifier [ is not valid` (comprehension), `The variable identifier d[0] is
  not valid` (dict). With `id=` each form works: a loop (`id=f"z{i}"`), a comprehension
  (`[Var(range(3), id=f"z{i}") for i in range(2)]`), a dict entry (`id="d0"`) and a helper
  (`id=name`).
- Identifiers (the `id`, or the Python name when no `id` is given) must not be an XCSP or
  ACE keyword. ACE stops with `Fatal Error: The id E is a keyword, and so cannot be used.`.
  Probed in the image, these 58 are reserved: `E` and the 57 words
  `abs`, `acos`, `add`, `and`, `asin`, `atan`, `card`, `convex`, `cos`, `cosh`, `diff`, `dist`, `div`, `djoint`, `eq`, `exp`, `fdiv`, `fmod`, `ge`, `gt`, `hull`, `if`, `iff`, `imp`, `in`, `inter`, `le`, `ln`, `log`, `lt`, `max`, `min`, `mod`, `mul`, `ne`, `neg`, `not`, `nroot`, `or`, `others`, `PI`, `pow`, `sdiff`, `set`, `sin`, `sinh`, `sqr`, `sqrt`, `sub`, `subseq`, `subset`, `supseq`, `supset`, `tan`, `tanh`, `union`, `xor`.
  Probed and accepted: `A`..`Z` except `E`, `a`..`z`, `instance`, `variables`, `var`, `array`, `domain`, `args`, `objective`, `minimize`,
  `maximize`, `static`, `decision`, `ALL`, `STAR`, `TIMES`, `cst`, `ok`, `x_1`.
- Values must stay in the 32-bit range that ACE reads. Values at or above about 2.1e9 fail
  with `Fatal Error: Too big integer value 2147483640`. Accepted: `2147000000`. The same
  holds for negative values (`-2147483640` fails).
- Every domain value is built in memory. The total of all domain sizes, over all variables,
  must stay under about 3e7: four variables with `range(0, 10**7)` solved, five and six ran out
  of heap (`java.lang.OutOfMemoryError: Java heap space`). One `range(0, 10**9)` also ran out of
  heap. A domain such as `range(0, 10**7)` is fine on its own.
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
- `Element`: `v == t[idx]` where `t` is a VarArray and `idx` is a variable (verified). A Python
  list indexed by a variable fails: `TypeError: list indices must be integers or slices, not
  VariableInteger`. Use a `Table` over `(idx, value)` pairs, or a `VarArray` for `t`.
- `Table` linked to a `Channel` (verified): `Channel(x, y)` with
  `Table(scope=(y[i], y[(i + 1) % n]), conflicts=[...])` per consecutive pair.
- `AllDifferent([x[0], x[1] + 1])` (mixed variable and expression) and `AllDifferent(x + y)`
  (list concatenation) both post (verified).
- `Cumulative(origins=s, lengths=d, heights=h) <= 2`, and
  `Cumulative(tasks=[(origin, length, height), ...]) <= 1`.
- `NoOverlap(origins=s, lengths=d)`.
- `Circuit(x)`: successors form one Hamiltonian cycle (0-based). `Channel(x, y)`: y is the inverse
  of x.
- `LexIncreasing([x, y])`: vectors in lexicographic order. Use it to break symmetry on rows.
- `Regular(scope=x, automaton=Automaton(start=..., transitions=[...], final=...))` (verified: a
  single block of two ones in five binary variables, with `Sum(x) == 2`). For a line of cells
  with block runs (nonograms), one automaton per line: the transitions read the cell values
  and the final states close each run.
- `Product(list) == K` (verified for three variables). Four or more variables: see the
  `Product` note in SKILL.md.
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
| `Var` without `id=` in a loop, comprehension, helper or dict | `The identifier z is used twice`, `The variable identifier None / [ / d[0] is not valid` |
| `Var` declared on a line with a comma | `AssertionError: Every simple declaration must be on its own line` |
| Python list indexed by a variable | `TypeError: list indices must be integers or slices, not VariableInteger` |
| `min(..., key=...)` after `from pycsp3 import *` | `TypeError: min() got an unexpected keyword argument 'key'`. Use `builtins.min` |
| `Product(x[0]) == 2` (one value) | `AssertionError: Problem: Bad arity for node MUL. It is 1 but it should be between 2 and inf` |
| An XCSP keyword as an identifier, e.g. `E` | `Fatal Error: The id E is a keyword` (ACE, reported by the runner as `error`) |

## Not run

Not verified, not used in examples: `Mdd`, `Flow`, `Slide`, `Adhoc`, `Precedence`, `Clause`,
`Increasing(..., lengths=...)`, `LexIncreasing(..., matrix=True)`, per-cell domains with a
lambda, `Decreasing`, `Automaton` beyond the example above. If one is needed, run it first.

## Other things measured

- `data._SHIP` and `data["_SHIP"]` both read a field whose name starts with an underscore.
- Ragged input lists (`data.rows[i]` of different lengths) are plain Python lists.
- `import builtins` then `builtins.min([3, 1, 2], key=lambda v: -v)` works in a model that
  also does `from pycsp3 import *`.
- ACE output is checked by the runner, not trusted. Some tuples ACE reports for `Product`
  over four variables are invalid (`[100, 50, 1, 1]` for `Product == 5040`). Avoid such
  products rather than relying on the check.
