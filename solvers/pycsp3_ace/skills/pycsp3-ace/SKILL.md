---
name: pycsp3-ace
description: Write constraint models in PyCSP3 (Python) and solve them with the ACE solver bundled in pycsp3 2.6.1. Covers PyCSP3 modelling in general (variables, globals, objectives, errors) and the DCP-Bench pycsp3_ace submission (one model.py, instance fields through data, declared outputs as module-level names, evaluation with evaluation.check). Use when a problem must be modelled with PyCSP3 or submitted to the pycsp3_ace integration.
---

# PyCSP3 with ACE

PyCSP3 2.6.1 compiles a Python constraint model to XCSP3. ACE 2.6 ships inside the
wheel and solves it. Details: [references/language.md](references/language.md) (syntax,
globals, limits, errors), [references/examples.md](references/examples.md) (models run in
the image), [references/dcp-contract.md](references/dcp-contract.md) (the DCP-Bench contract
and verdicts), [sources.md](sources.md).

## Model shape

Outputs: `x`.

```python
from pycsp3 import *

x = VarArray(size=4, dom=range(4))
satisfy(AllDifferent(x))
minimize(Sum(x))   # optional: one minimize or maximize
```

- `satisfy(...)` posts constraints. A list or generator inside it is flattened.
- One declaration per line. `a, b = Var(...), Var(...)` fails.
- Domains: `range(lo, hi)` (upper bound excluded), a set `{0, 1}` for Booleans, or a list.
- Integers only. A float in an expression fails with `bad form of predicate`.

## Variables and domains

- Declare with `VarArray` at module level. A `Var` made in a loop, comprehension, helper
  function or dict needs an explicit `id=`, or pycsp3 fails. Messages in the table below.
- Reserved identifiers: `E` and 57 XCSP words such as `min`, `max`, `dist`, `in`, `set`,
  `sin`, `card`. ACE stops with `The id E is a keyword`. The full list is in language.md.
- Values must stay below about 2.1e9. The total number of domain values, summed over all
  variables, must stay under about 3e7. A 4 x 1e7 domain solved; 5e7 ran out of heap.
- Avoid `Product` of four or more variables. ACE 2.6 accepts invalid tuples there. The
  runner rejects them, but the search gets slower. Split into binary products with an
  auxiliary `VarArray`.

## Constraints

- Relations and arithmetic: `x[0] + 2 * x[1] < x[2]`, `x[0] != x[1]`, `Sum(w[i] * x[i] for i in range(n))`.
- Globals are functions: `AllDifferent`, `Increasing(x, strict=True)`, `Count`, `NValues`,
  `Exist`, `Cardinality`, `Minimum`, `Maximum`, `Table`, `Circuit`, `Channel`, `Cumulative`,
  `NoOverlap`, `LexIncreasing`, `Regular`, `BinPacking`, `Knapsack`, `Hamming`.
  Each one is run in [references/language.md](references/language.md).
- `v == t[idx]` with a variable index is an element constraint when `t` is a `VarArray`.
  A Python list indexed by a variable fails: use `Table` or a `VarArray`.
- Conditions: `imply(a, b)`, `If(c, Then=..., Else=...)`, `(b == 1) == (Sum(x) > 4)`,
  `Or`, `Xor`, `And`, `Iff`. `Not(c)` fails in 2.6.1: write the negated relation instead.
- Matrices: `VarArray(size=[r, c], dom=...)` gives nested lists; `grid[i][j]`, `grid[:, j]`.
- `from pycsp3 import *` replaces the builtin `min`: `min(..., key=...)` fails. Use
  `builtins.min(..., key=...)` after `import builtins`.

## Comments

Each conceptual block of constraints starts with a `#` line taken from the problem
statement, in its words: `# all rows must have different values`. Do not name the global.

## Every output must be constrained

ACE reports only variables that a constraint mentions. A whole output with no constraint
fails with `declared output 'z' has a variable that no constraint mentions`. One element of
an array fails with `a declared output has no determined value`. Constrain every element.

## Objectives and search

- At most one `minimize(term)` or `maximize(term)`.
- For an optimisation the runner first runs ACE's full search and reports a solution only
  when ACE proved the optimum. An unproven optimum is a `timeout`, not an incumbent.
- Enumeration runs more solve rounds, each excluding the assignments already found. Each
  round is one compile. A round that returns fewer solutions than asked, without saying the
  search is exhausted, ends as `timeout`.
- Symmetry: `LexIncreasing([x, y])` orders two vectors. For a grid, order the flat
  row-major list against the flat transposed list ([examples.md](references/examples.md)).

## Common errors

Messages are verified. The runner passes them through as `execution_error` detail.

| message | cause |
|---|---|
| `The identifier z is used twice. This is not possible` | `Var` without `id=` inside a loop |
| `The variable identifier None is not valid` | `Var` without `id=` made in a helper function |
| `The variable identifier [ is not valid` | `Var` without `id=` in a list comprehension |
| `The variable identifier d[0] is not valid` | `Var` stored in a dict |
| `The id E is a keyword, and so cannot be used.` | reserved identifier, see the list |
| `Too big integer value 2147483640` | value at or above about 2.1e9 |
| `java.lang.OutOfMemoryError: Java heap space` | total domain values too large |
| `TypeError: list indices must be integers or slices, not VariableInteger` | Python list indexed by a variable |
| `TypeError: min() got an unexpected keyword argument 'key'` | builtin `min` replaced by pycsp3 |
| `Bad arity for node MUL. It is 1 but it should be between 2 and inf` | `Product` of one value |
| `the model must not call solve()` | remove `solve()` |
| `declared output 'z' has a variable that no constraint mentions` | output not in any constraint |
| `unary ~: 'list'` | `Not(...)` of a constraint |

## DCP-Bench submissions (pycsp3_ace)

Read [references/dcp-contract.md](references/dcp-contract.md) before writing a submission.

- One file, `model.py`. Instance fields come from `data`: `data.n` or `data["n"]`.
- Each declared output is a module-level name equal to the output name, bound to a `Var`,
  `VarArray` or nested list. Booleans are 0/1. Shapes: `python -m generation.brief PROBLEM`.
- Values follow the problem description (queens: columns 1 to n).
- Satisfaction: no objective. Optimisation: one objective in the direction `brief` gives.
- Check: `python -m evaluation.check model.py --problem PROBLEM --solver pycsp3_ace --instance-count N --solution-limit 2`.
  Read `reason` and `detail` per instance, in `instances[]`.

## Known limits

- Each round starts a Python and a Java process. A small run took about 2 s wall in total.
- The Java heap is 1200 MiB inside the 2048 MiB container limit. Memory failures are
  `memory_limit`, which the checker treats as inconclusive. A Java `OutOfMemoryError` that
  ACE reports is `execution_error` with that message.
- `The search stopped before it was exhausted` (`timeout`): ACE stopped with fewer
  solutions than asked and did not prove that none are left.
