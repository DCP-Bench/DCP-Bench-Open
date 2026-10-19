---
name: pycsp3-ace
description: PyCSP3 is a Python library (pip package and import pycsp3) that compiles constraint models to XCSP3; the ACE solver ships inside the wheel as a Java jar and solves them. Use when writing, debugging or explaining PyCSP3 models, or when the user has chosen PyCSP3 or ACE for a constraint satisfaction or optimisation problem.
license: Apache-2.0
compatibility: Requires Python 3.10+, pycsp3 (tested 2.6.1, MIT, pulls in lxml) and a Java runtime on PATH for the bundled ACE-2.6.jar (tested with OpenJDK 17). No licence key.
metadata:
  domain: constraint-programming
  solver: ace
  paradigm: cp
---

# PyCSP3 with ACE

PyCSP3 is a modelling library: Python statements declare variables and post constraints,
`solve()` compiles the model to an XCSP3 file (`<script>.xml`) and runs ACE, a Java CP
solver bundled in the wheel, as a subprocess. Keep in mind that **the variable names come
from the Python source line** that declares them, and that a **solver-side error is not an
exception**: `solve()` returns `UNKNOWN` and the cause is in ACE's log file.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Reading data](#reading-data)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Modelling lessons](#modelling-lessons)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Examples: [satisfy](assets/satisfy-queens/README.md), [all solutions](assets/all-solutions-latin/README.md),
  [all optimal](assets/all-optimal-permutation/README.md), [maximise](assets/maximise-knapsack/README.md),
  [minimise](assets/minimise-coins/README.md), [infeasible](assets/infeasible-pigeonhole/README.md),
  [scheduling](assets/scheduling-jobshop/README.md), [fewest colours](assets/colouring-min-colours/README.md),
  [JSON input](assets/json-input-shifts/README.md)
- References: [language.md](references/language.md) (every construct, limits, reserved
  words, failing forms), [examples.md](references/examples.md) (tested models per global)

## Install

```bash
pip install pycsp3                 # also installs lxml; ACE-2.6.jar is inside the wheel
java -version                      # any recent JRE; ACE's classes are Java 8/11
python -c "from importlib.metadata import version; print(version('pycsp3'))"
```

`pycsp3` has no `__version__`. Importing pycsp3 in a script that declares no variables prints
`Warning: no variables in this model` at exit; harmless. Java heap: set it with
`JAVA_TOOL_OPTIONS=-Xmx2g` (Java then prints `Picked up JAVA_TOOL_OPTIONS` on stderr).
Details: [installation](http://pycsp.org/documentation/installation).

## Quick start

```python
from pycsp3 import *

x = VarArray(size=4, dom=range(4))
satisfy(AllDifferent(x), x[0] < x[1])
minimize(Sum(x[i] * (i + 1) for i in range(4)))

status = solve()                     # OPTIMUM, SAT, UNSAT or UNKNOWN
if status is OPTIMUM:
    print(values(x), bound())        # [2, 3, 1, 0] 11
```

`python model.py` writes `model.xml` and a `solver_*.log` file to the working directory.
A small model takes about 2 s wall in total (Python start, compilation, a Java start).

## Modelling

Every construct below was run; the full catalogue with failing forms is in
[language.md](references/language.md), and per-global models in
[examples.md](references/examples.md). API docs: [pycsp.org](https://pycsp.org/).

| Need | API |
|---|---|
| integer variable | `Var(dom=range(lo, hi))` (upper bound excluded), a list or a set; Boolean `dom={0, 1}` |
| array, matrix | `VarArray(size=n, dom=...)`, `VarArray(size=[r, c], dom=...)`; `grid[i][j]`, column `grid[:, j]` |
| post constraints | `satisfy(c1, c2, ...)`; lists and generators inside are flattened |
| arithmetic | `+ - * // % abs`, `==`, `!=`, `<`; `Sum(w[i] * x[i] for i in range(n))`; integers only |
| all different | `AllDifferent(x)`, also over expressions `AllDifferent(q[i] + i for i in range(n))` |
| counting | `Count(x, value=v)`, `NValues(x)`, `Exist(x, value=v)`, `Cardinality(x, occurrences={...})` |
| element | `v == t[idx]` with `t` a `VarArray` and `idx` a variable |
| table | `(x, y) in {(0, 1), (1, 2)}`, `x in {1, 3}`, `Table(scope=x, supports=[...])`, `conflicts=[...]`; `ANY`/`'*'` wildcard |
| min / max | `Minimum(x) == lo`, `Maximum(x) == hi`, `MaximumArg(x, rank=TypeRank.FIRST) == i` |
| scheduling | `NoOverlap(origins=s, lengths=d)`, `Cumulative(origins=s, lengths=d, heights=h) <= cap` |
| graphs, permutations | `Circuit(x)` (0-based successors), `Channel(x, y)` (inverse) |
| sequences | `Increasing(x, strict=True)`, `LexIncreasing([x, y])`, `Regular(scope=x, automaton=Automaton(...))` |
| packing | `BinPacking(b, sizes=w, limits=caps)`, `Knapsack(x, weights=w, wlimit=c, profits=p) >= k` |
| distance | `Hamming(x, y) == k` (positions where two arrays differ) |
| logic | `imply(a, b)`, `If(c, Then=..., Else=...)`, `Or`, `And`, `Xor`, `Iff`; reify `(b == 1) == (Sum(x) > 4)` |
| objective | at most one `minimize(term)` or `maximize(term)` |

Rules pycsp3 enforces (messages in [Common issues](#common-issues)):

- **One declaration per line.** `a, b = Var(...), Var(...)` fails.
- **Declare variables at module level, preferably as one `VarArray`.** A `Var` without `id=`
  made in a loop, comprehension, helper function or dict fails. `VarArray` inside a function
  works; with `id="x"` it is safe everywhere.
- **Reserved identifiers**: `E` and 57 XCSP words (`min`, `max`, `dist`, `in`, `set`, `sin`,
  `card`, ...; full list in [language.md](references/language.md#variables-and-domains)).
  ACE stops with `The id E is a keyword`.
- **Value limits**: values at or above about 2.1e9 (either sign) fail; the total number of
  domain values over all variables must stay under about 3e7 (four `range(10**7)` domains
  solved, five ran out of a 1200 MiB heap; one `range(10**9)` too).
- **A Python list indexed by a variable fails**: make it a `VarArray`, or use a `Table` of
  `(index, value)` pairs ([JSON example](assets/json-input-shifts/README.md)).
- `from pycsp3 import *` replaces the builtin `min`/`max` and defines `values`, `value`,
  `Sum`, `ANY`, ...: `min(..., key=...)` fails (use `builtins.min` after `import builtins`),
  and a data list called `values` hides the function.
- `Not(c)` fails in 2.6.1: write the negated relation (`!=`, `>=`).

## Reading data

Read a JSON file with the standard library's `json` and take every size from it; extra keys
are simply never read ([example](assets/json-input-shifts/README.md)):

```python
import json, sys
from pycsp3 import *
with open(sys.argv[1] if len(sys.argv) > 1 else "data.json") as f:
    d = json.load(f)
x = VarArray(size=d["n"], dom=range(d["n"]))
satisfy(AllDifferent(x))
```

PyCSP3's own `python model.py -data=file.json` (then `data.n`) breaks on keys starting
with `_` and on one-key files ([details](references/language.md#reading-data)); plain `json`
avoids both.

## Solving

`solve(solver=ACE, options="", verbose=-1, sols=None)` compiles, runs ACE and returns a
`TypeStatus`; compare with `is`. Solver options: `java -jar <path>/ACE-2.6.jar` lists them,
or the [options PDF](https://github.com/xcsp3team/pycsp3/blob/master/docs/optionsSolvers.pdf).

| Status | Meaning |
|---|---|
| `OPTIMUM` | optimisation, optimum proven |
| `SAT` | a solution; for an optimisation, **not proven optimal** (time limit) |
| `UNSAT` | proven infeasible; `n_solutions()` is `None`, no values stored |
| `UNKNOWN` | nothing found: time limit, or a solver error (prints `Actually, the instance was not solved`) |

- Values: `value(v)`, `values(x)` (nested like `x`), `values(x, sol=k)` for solution k;
  objective value `bound()`. An array element no constraint mentions reads as `*` (`ANY`);
  a lone `Var` no constraint mentions makes `value(z)` raise `AssertionError`. ACE only
  sees constrained variables, so constrain everything you print.
- Time limit `options="-t=10s"` (**a bare number is milliseconds**), seed `-seed=1`.
- `verbose=1` prints the compilation and the ACE command and log; `solver().last_log` is the
  log file path. `clear()` drops the whole model so a script can build and solve another.
- Files: `solve()` writes `<script>.xml` (`model.xml` for `model.py`) and `solver_*.log` to the
  **current working directory**, not beside the script. If that directory is read-only,
  `solve()` raises `OSError: [Errno 30] Read-only file system` while compiling. Run the script
  from a writable directory.
- **Errors**: a Python modelling error raises (or pycsp3 prints `ERROR: ...` and exits). An
  ACE error gives `UNKNOWN`, with `Fatal Error: ...` in the log, or only `! ERROR (use -ev
  for more details)` for a Java exception; `options="-ev"` does not bring it into the log,
  so rerun ACE on the XML: `java -jar <path>/ACE-2.6.jar model.xml -ev` prints the
  exception (e.g. `java.lang.OutOfMemoryError: Java heap space`). The jar path:
  `os.path.join(os.path.dirname(pycsp3.__file__), "solvers", "ace", "ACE-2.6.jar")`.
- **Checking a solution**: ACE 2.6 can report wrong solutions for `Product` over four or
  more variables (see [lessons](#modelling-lessons)). The XCSP3 checker in the same jar
  verifies one: write `str(solution())` to `sol.xml`, then
  `java -cp <jar> org.xcsp.parser.callbacks.SolutionChecker model.xml sol.xml` prints `OK`
  or `INVALID Solution!` with the violated constraint.

## All solutions

`solve(sols=ALL)` (or `sols=k`) enumerates; read solution k with `values(x, sol=k)`
([example](assets/all-solutions-latin/README.md)). Two traps:

- `n_solutions()` misparses ACE's thousands separator (`1,500` gives 500). Count the stored
  solutions instead: `len(x[0].values)` for any variable `x[0]` of the model.
- The status is `SAT` whether or not the search finished. Only the log tells: it contains
  `d COMPLETE EXPLORATION` or `d INCOMPLETE EXPLORATION` (`solver().last_log`).
- An infeasible model enumerates to `UNSAT`, not `SAT` with zero solutions: `n_solutions()` is
  `None` and `x[0].values` is empty. Take the count as `len(x[0].values) if status is SAT else 0`;
  it is 0 with no error.

ACE enumerates assignments of all constrained variables, so an auxiliary variable that is
not fixed by the ones you print repeats them; deduplicate on the printed values or fix it.

**All optimal solutions** ([example](assets/all-optimal-permutation/README.md)): solve with the
objective, require `OPTIMUM`, keep `best = bound()`; then `clear()`, rebuild the model (a
function returning the arrays, with `id=`), post `satisfy(term == best)` with no objective,
and `solve(sols=ALL)`.

## Modelling lessons

Learned across hundreds of PyCSP3 models; the timing claims were measured on small instances.

- **Boolean indicators instead of `NValues`** in a feasibility model: one 0/1 variable per
  (item, value), linked by `(ind[i][c] == 1) == (x[i] == c)`, with plain `Sum` counts, beat
  `NValues` over integer colours on Schur-type colouring models ([examples.md](references/examples.md#boolean-indicators-instead-of-nvalues)).
- **`NValues` as the objective** works: `minimize(NValues(colour))` proved the fewest colours
  on a 6-cycle (2), K4 (4), Petersen (3) and a wheel ([fewest colours](assets/colouring-min-colours/README.md)).
  A `Maximum`-index objective (`Maximum(colour) == top`, `minimize(top)`) also worked on three
  graphs; use `NValues` unless you need the index.
- **`Product` over four or more variables**: ACE 2.6 accepts wrong tuples (`[100, 50, 1, 1]`
  for `Product == 5040`). Split into binary products with an auxiliary `VarArray`
  ([examples.md](references/examples.md#product-of-four-variables-split-into-binary-products)).
- **Symmetry breaking**: `LexIncreasing([row_a, row_b])` orders vectors; for the transpose
  symmetry of a square grid, order the flat row-major list against the flat column-major list
  ([examples.md](references/examples.md#grid-symmetry-with-lexincreasing-transpose)). Add it
  only when equivalent solutions are truly interchangeable for the question asked.
- **Nonogram-style lines**: one `Regular` automaton per line, reading cell values, with final
  states that close each run.
- Keep domains tight (they are materialised value by value) and constrain every variable you
  read back.

## Common issues

| Message or symptom | Cause | Fix |
|---|---|---|
| `AssertionError: Every simple declaration must be on its own line` | two declarations on one line | one per line |
| `The identifier z is used twice. This is not possible` | `Var` without `id=` in a loop | `VarArray`, or `id=f"z{i}"` |
| `The variable identifier None is not valid` | `Var` without `id=` in a helper function | `id=name` |
| `The variable identifier [ is not valid` | `Var` without `id=` in a list comprehension | `VarArray`, or `id=` |
| `The variable identifier d[0] is not valid` | `Var` stored in a dict | `id="d0"` |
| `UNKNOWN`; log: `Fatal Error: The id E is a keyword, and so cannot be used.` | reserved identifier | rename ([list](references/language.md#variables-and-domains)) |
| `UNKNOWN`; log: `Fatal Error: Too big integer value 2147483640` | value >= about 2.1e9 | rescale |
| `UNKNOWN`; log: `! ERROR (use -ev ...)`; ACE `-ev`: `java.lang.OutOfMemoryError` | too many domain values | tighter domains, or more heap |
| `TypeError: list indices must be integers or slices, not VariableInteger` | Python list indexed by a variable | `VarArray` or `Table` |
| `TypeError: min() got an unexpected keyword argument 'key'` | builtin `min` replaced | `builtins.min` |
| `TypeError: bad operand type for unary ~: 'list'` | `Not(...)` | negated relation |
| `ValueError: Problem: bad form of predicate 0.5` | float in an expression | scale to integers |
| `Bad arity for node MUL. It is 1 but it should be between 2 and inf` | `Product` of one value | use the value |
| `TypeError: Wrong type for first` | `rank='first'` | `rank=TypeRank.FIRST` |
| `*` in `values(x)`; `AssertionError` from `value(z)` | variable in no constraint | constrain it |
| `n_solutions()` too small | thousands separator | [count stored values](#all-solutions) |
| `n_solutions()` is `None` after enumeration | the model is infeasible: `solve(sols=ALL)` returned `UNSAT` | count is 0; [status check](#all-solutions) |
| `OSError: [Errno 30] Read-only file system` from `solve()` | the working directory is read-only; pycsp3 writes the XML and the log there | run from a writable directory ([Solving](#solving)) |
| `SAT` for an optimisation | time limit before the proof | longer `-t`, stronger model |
| `ValueError: Field names cannot start with an underscore` | `-data=` with a `_key` | [plain `json`](#reading-data) |

## Further reading

- Documentation: <https://pycsp.org/> (models and data: <http://pycsp.org/models/>)
- Source and solver options: <https://github.com/xcsp3team/pycsp3>
- ACE: <https://github.com/xcsp3team/ace>
