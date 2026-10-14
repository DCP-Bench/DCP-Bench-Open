---
name: pycsp3-ace
description: Write constraint models in PyCSP3 (Python) and solve them with the ACE solver bundled in pycsp3 2.6.1. Covers PyCSP3 modelling in general (variables, globals, objectives, errors) and the DCP-Bench pycsp3_ace submission (one model.py, instance fields through data, declared outputs as module-level names, evaluation with evaluation.check). Use when a problem must be modelled with PyCSP3 or submitted to the pycsp3_ace integration.
---

# PyCSP3 with ACE

PyCSP3 2.6.1 compiles a Python constraint model to XCSP3. ACE 2.6 ships inside the
wheel and solves it. Details: [references/language.md](references/language.md) (syntax,
globals, what fails), [references/examples.md](references/examples.md) (models run in the
image), [references/dcp-contract.md](references/dcp-contract.md) (the DCP-Bench contract
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

## Constraints

- Relations and arithmetic: `x[0] + 2 * x[1] < x[2]`, `x[0] != x[1]`, `Sum(w[i] * x[i] for i in range(n))`.
- Globals are functions: `AllDifferent`, `Increasing(x, strict=True)`, `Count`, `NValues`,
  `Exist`, `Cardinality`, `Minimum`, `Maximum`, `Table`, `Circuit`, `Channel`, `Cumulative`,
  `NoOverlap`, `LexIncreasing`, `Regular`, `BinPacking`, `Knapsack`, `Hamming`.
  Each one is run in [references/language.md](references/language.md).
- `v == t[idx]` with a variable index is an element constraint.
- Conditions: `imply(a, b)`, `If(c, Then=..., Else=...)`, `(b == 1) == (Sum(x) > 4)`,
  `Or`, `Xor`, `And`, `Iff`. `Not(c)` fails in 2.6.1 (`unary ~: 'list'`): write the negated
  relation instead.
- Matrices: `VarArray(size=[r, c], dom=...)` gives nested lists; `grid[i][j]`, `grid[:, j]`.

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
- Enumeration after the first round runs more solve rounds, each with nogoods that exclude
  the assignments already found. Each round is one compile. A round that returns fewer
  solutions than asked, without saying the search is exhausted, ends as `timeout`.
- Symmetry: `LexIncreasing([x, y])` orders two vectors (verified). Keep domains tight.

## Common errors

| message (verified) | cause |
|---|---|
| `Every simple declaration must be on its own line` | two Vars on one line |
| `the model must not call solve()` | remove `solve()` |
| `declared output 'z' has a variable that no constraint mentions` | output not in any constraint |
| `unary ~: 'list'` | `Not(...)` of a constraint |
| `SyntaxError` on `notin` | `(x, y) notin {...}` is not valid; use `Table(conflicts=...)` |
| `bad form of predicate 0.5` | float coefficient |
| `Wrong type for first` | `MaximumArg(..., rank='first')`; use `rank=TypeRank.FIRST` |

## DCP-Bench submissions (pycsp3_ace)

Read [references/dcp-contract.md](references/dcp-contract.md) before writing a submission.

- One file, `model.py`. Instance fields come from `data`: `data.n` or `data["n"]`.
- Each declared output is a module-level name equal to the output name, bound to a `Var`,
  `VarArray` or nested list. Booleans are 0/1. Shapes: `python -m generation.brief PROBLEM`.
- Values follow the problem description (queens: columns 1 to n).
- Satisfaction: no objective. Optimisation: one objective in the direction `brief` gives.
- Check: `python -m evaluation.check model.py --problem PROBLEM --solver pycsp3_ace --instance-count N`.
  Read `reason` and `detail` per instance, in `instances[]`.

## Known limits

- Each round starts a Python and a Java process. A small run took about 2 s wall in total.
- The Java heap is 1200 MiB inside the 2048 MiB container limit. Memory failures are
  `memory_limit`, which the checker treats as inconclusive.
