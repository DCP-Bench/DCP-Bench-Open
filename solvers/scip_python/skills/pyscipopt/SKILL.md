---
name: pyscipopt
description: PySCIPOpt, the Python interface to the SCIP mixed-integer and nonlinear solver (pip package and import `pyscipopt`), with SCIP's general constraints (and/or/xor, indicator, cardinality, SOS, cumulative, nonlinear). Use when writing, debugging or explaining SCIP models in Python, or when the user has chosen SCIP for an optimisation or feasibility problem.
license: Apache-2.0
compatibility: Requires Python 3.8+ and pip install pyscipopt (tested with PySCIPOpt 6.3.0, whose wheel bundles SCIP 10.0.2, on Python 3.12). SCIP is Apache-2.0 and PySCIPOpt MIT; no licence key or size limit.
metadata:
  domain: constraint-programming
  solver: scip
  paradigm: mip
---

# SCIP (Python, `pyscipopt`)

SCIP is a branch-and-cut MIP solver that also handles general constraints natively:
logical and/or/xor, indicators, cardinality, SOS, cumulative and nonlinear expressions.
Use them where they state the problem directly; do not hand-linearise what SCIP already
supports. The objective must be linear, and the result is a **status string** to check
before any value is read.

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- [Modelling](#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Common issues](#common-issues)
- [Further reading](#further-reading)
- Encodings (`!=`, `abs`, min/max, `//`, `%`, logic, products, symmetry): [references/encodings.md](references/encodings.md)
- Examples: [n-queens](assets/n-queens/README.md) (satisfy), [n-queens-all](assets/n-queens-all/README.md) (all solutions), [all-optimal](assets/all-optimal/README.md), [knapsack](assets/knapsack/README.md) (maximise), [assignment](assets/assignment/README.md) (minimise), [infeasible](assets/infeasible/README.md), [scheduling](assets/scheduling/README.md), [json-input](assets/json-input/README.md) (data from a JSON file)

## Install

```bash
pip install pyscipopt
python -c "import pyscipopt; print(pyscipopt.__version__, pyscipopt.Model().version())"   # 6.3.0 10.0 when tested
```

The binary wheel bundles SCIP and needs NumPy (installed with it); no compiler, licence
or network at run time. Details: [installation guide](https://pyscipopt.readthedocs.io/en/latest/install.html).

## Quick start

```python
from pyscipopt import Model, quicksum

m = Model("quick")
m.hideOutput()                                   # silence the solver log
x = m.addVar(name="x", vtype="I", lb=0, ub=10)
y = m.addVar(name="y", vtype="I", lb=0, ub=10)
m.addCons(x + y >= 7)
m.addCons(x - y <= 2)
m.setObjective(3 * x + 2 * y, "minimize")
m.optimize()

if m.getStatus() == "optimal":                   # proven: the default gap is 0
    print("Objective:", round(m.getObjVal()))
    print("x =", round(m.getVal(x)), "y =", round(m.getVal(y)))
else:
    print("Status:", m.getStatus())
```

Expected output: `Objective: 14`, then `x = 0 y = 7`.

## Modelling

Reference: [Model API](https://pyscipopt.readthedocs.io/en/latest/api/model.html) ·
[constraint types](https://pyscipopt.readthedocs.io/en/latest/tutorials/constypes.html) ·
[expressions](https://pyscipopt.readthedocs.io/en/latest/tutorials/expressions.html)

| Need | API |
|---|---|
| variable | [`m.addVar(name=, vtype="B"\|"I"\|"C", lb=, ub=)`](https://pyscipopt.readthedocs.io/en/latest/api/model.html); `lb` defaults to **0**, `ub=None` is infinity. Give every integer tight finite bounds from the data |
| linear constraint | `m.addCons(expr <= rhs)`, `>=`, `==`; sums with `quicksum(c * x[i] for i in I)` |
| ranged `lo <= e <= hi` | `m.addCons((lo <= e) <= hi)` with the parentheses, or two constraints; without them `TypeError: Can't evaluate constraints as booleans` |
| discrete choice, all-different, element | one-hot binaries: [encodings](references/encodings.md#discrete-choices-and-all-different) |
| `x != y` | not supported (`NotImplementedError`); [encoding](references/encodings.md#not-equal) |
| conditional constraint | [`m.addConsIndicator(ineq, binvar=b, activeone=True)`](https://pyscipopt.readthedocs.io/en/latest/tutorials/constypes.html): `<=`/`>=` only, **always pass `binvar`** |
| and / or / xor | `addConsAnd(bs, r)`, `addConsOr(bs, r)`, `addConsXor(bs, True)` (rhs a Python bool) |
| at most k nonzero, SOS | `addConsCardinality(xs, k)`, `addConsSOS1(xs)`, `addConsSOS2(xs)` |
| scheduling | `addConsCumulative(starts, durations, demands, capacity)`: integer starts, constant durations and demands ([example](assets/scheduling/README.md)) |
| no-overlap (one machine, disjunctive) | `addConsCumulative(starts, durations, [1] * k, 1)` per machine; no big-M pairwise disjunctions needed |
| nonlinear | `x * y`, `x ** 2`, `abs(e)`, `sqrt`, `exp`, `log`, `e / y` in constraints ([when to avoid](references/encodings.md#products)) |
| read data from a file | standard `json` module: `data = json.load(open(sys.argv[1]))`; take sizes from the data, ignore extra keys ([example](assets/json-input/README.md)) |
| minimise / maximise | `m.setObjective(expr, "minimize" \| "maximize")`; linear only. No objective = satisfaction |

Not available on variables: Python `min`/`max` and `!=` (`NotImplementedError: can only
support with '<=', '>=', or '=='`), `//` and `%` (`TypeError`). Encodings for all of
them: [references/encodings.md](references/encodings.md).

Lessons that turned timeouts into solves:

- **One-hot binaries for discrete choices**: all-different as "each value at most once"
  is far stronger than pairwise `!=`.
- **Indicators instead of big-M**: indicator models solved where big-M versions timed out.
- **`abs` is slow in constraints**: `d == abs(x - y)` timed out from about 13 variables;
  a sign binary with indicators was fast ([encoding](references/encodings.md#absolute-value)).
- **Symmetry breaking and implied constraints** derived from the data
  ([details](references/encodings.md#search-help-symmetry-and-implied-constraints)).
- **Large coefficients in one linear equality are fine**: a cryptarithm's
  `SEND + MORE == MONEY` with `10**k` weights solved in milliseconds; no need to split it
  into column-wise carries.
- **Hold the objective in a bounded integer variable** (`z == expr`, bounds from the data,
  `setObjective(z)`): it can then be pinned to enumerate optima. With a bare expression as
  objective, one model proved its optimum in 2 s and then timed out finding a second
  optimal solution.

## Solving

Statuses: [`getStatus`](https://pyscipopt.readthedocs.io/en/latest/api/model.html) ·
Parameters: [SCIP parameter list](https://www.scipopt.org/doc/html/PARAMETERS.php)

| `m.getStatus()` | Meaning |
|---|---|
| `"optimal"` | proven optimal (default gap 0); with no objective: a solution was found |
| `"infeasible"` | proven to have no solution |
| `"unbounded"` | objective unbounded |
| `"inforunbd"` | infeasible or unbounded: re-solve with presolve off to decide (below) |
| `"timelimit"` | stopped at `limits/time`; a solution exists only if `m.getNSols() > 0` |
| `"nodelimit"`, `"sollimit"`, `"gaplimit"`, `"memlimit"`, `"userinterrupt"` | stopped by that limit; not proven |

- **No solution** means `"infeasible"`, also with an objective. `"inforunbd"` is not yet
  an answer: presolve could not tell infeasible from unbounded. To decide it, run
  `m.freeTransform()`, `m.setPresolve(SCIP_PARAMSETTING.OFF)` (import
  `SCIP_PARAMSETTING` from `pyscipopt`), `m.optimize()`, and read the new status
  (`"infeasible"` or `"unbounded"`). Example: maximise a continuous `x >= 0` with no upper
  bound, with an unbounded integer `y` and `m.addCons(2 * y == 1)`; the first solve gives
  `inforunbd`, and presolve off gives `infeasible`. With `m.addCons(2 * z == 2 * x + 1)`
  for an integer `z` instead, presolve off gives `unbounded`.
- Read values with `m.getVal(var)` and `m.getObjVal()`; round integers (`round(...)`).
  `m.getBestSol()[expr]` evaluates any expression in the best solution.
- **Check the status first.** With no solution `getVal` raises `Warning: No solution
  available` and `getBestSol()` returns `None` (6.3.0); after `freeTransform()` it still
  returns the old solution's value, and older setups were seen to return a silent 0.
- Parameters with `m.setParam(name, value)`: `limits/time` (seconds), `limits/gap`
  (0 by default), `randomization/randomseedshift`, `parallel/maxnthreads`.
  `m.hideOutput()` silences the log.
- Errors: Python exceptions (`TypeError`, `NotImplementedError`, `ValueError`) at model
  building, with a traceback on stderr. SCIP's own errors print `[file.c:line] ERROR:` to
  stderr and raise `Exception: SCIP: method cannot be called at this time`. Some misuse
  (an indicator without `binvar`) **crashes the process** with a segmentation fault (exit
  code 139) and no traceback.

## All solutions

No reliable built-in enumeration: `m.count()` is wrong with indicators (it returned 0
where solutions existed, and 5 of 12 on a two-variable `!=` model). Enumerate with
no-goods in a loop ([example](assets/n-queens-all/README.md)):

1. `m.optimize()`; stop at `"infeasible"` (none left). Any other status (`"timelimit"`, ...)
   means the list is incomplete: report that, do not present it as all solutions.
2. Record the values, then `m.freeTransform()`: **required** before changing a solved
   model (`addVar` on a solved model gives `cannot call method <SCIPcreateVarBasic> in
   problem solved stage`).
3. Add a no-good over the variables you care about. Binaries: `quicksum(1 - v for v in
   ones) + quicksum(zeros) >= 1`. General integers: per variable, binaries `lo`/`hi` with
   `addConsIndicator(x <= v - 1, binvar=lo)` and `addConsIndicator(x >= v + 1, binvar=hi)`
   (only on a side the bounds allow), then `quicksum(moves) >= 1`.

Block only the variables that define a distinct solution, so auxiliary variables never
produce repeats. **All optimal solutions**: solve, read the optimum, `freeTransform()`,
pin the objective variable to it (form below), `m.setObjective(0, "minimize")`, then
the loop ([example](assets/all-optimal/README.md)). With an integer objective take
`best = round(m.getObjVal())` and keep `z` integer. With a fractional objective `z` is
continuous and the pin is one-sided: `best = m.getObjVal()`, `z <= best + 1e-6` when
minimising, `z >= best - 1e-6` when maximising. An exact `z == best` also worked in tests,
within SCIP's feasibility tolerance (`numerics/feastol`, 1e-6), but the one-sided form does
not rely on it.

**Cost**: each solution is a full re-solve after `freeTransform()`, so time grows with the
number of solutions (92 n-queens solutions at n = 8: about 9 to 12 s, against about 1 s for
one). Cap the list when a few are enough: stop the loop once `len(solutions)` reaches the
cap. When only the **number** of solutions is needed and the model is pure
linear over binaries (no indicators), `m.count()` then `m.getNCountedSols()` is much faster
(92 in under 1 s), but it does not return the solutions.

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| Segmentation fault (exit 139) at `optimize()` | `addConsIndicator` without `binvar=` | always pass `binvar=b` |
| `ValueError: expected inequality that has either only a left or right hand side` | equality in `addConsIndicator` | two indicators (`<=`, `>=`) on the same binary |
| `NotImplementedError: can only support with '<=', '>=', or '=='` | `!=`, or `max`/`min` over variables | [encodings](references/encodings.md) |
| `TypeError: Can't evaluate constraints as booleans` | ranged `lo <= e <= hi` | `(lo <= e) <= hi`, or two constraints |
| `TypeError: unsupported operand type(s) for //` or `%` | integer division on a variable | `x == d * q + r`, `0 <= r <= d - 1` |
| `ValueError: SCIP does not support nonlinear objective functions` | nonlinear objective | minimise `z` with `z >= f(x)` ([encodings](references/encodings.md#nonlinear-objective)) |
| `AssertionError: Provide BOOLEAN value as rhsvar` | `addConsXor` with a variable rhs | parity `quicksum(bs) == 2 * k + r` |
| `ERROR: cannot call method ... in problem solved stage` | model changed after `optimize()` | `m.freeTransform()` first |
| later solve crashes after a caught exception | an `addCons` was rejected and the program carried on | fix the constraint; never catch a rejected `addCons` and continue |
| `Warning: No solution available`, or values all 0 | values read without a solution | check `getStatus()` / `getNSols()` first |
| `m.count()` gives too few solutions | counting with indicators | no-good loop ([All solutions](#all-solutions)) |
| enumeration slow with many solutions | one full re-solve per no-good | expected; use `m.count()` for a count on pure binary linear models |
| `inforunbd` taken as "no solution" | presolve could not tell infeasible from unbounded | re-solve with presolve off ([Solving](#solving)) |
| enumeration lists fewer solutions than exist, after a `timelimit` | the loop treats any non-optimal status as the end | stop only at `"infeasible"`; any other status is an incomplete list ([All solutions](#all-solutions)) |
| fractional objective: all-optimal list misses optima or repeats | objective variable declared integer, or pinned with `==` on a float | `z` continuous, pin `z <= best + 1e-6` (or `>=`) ([All solutions](#all-solutions)) |
| more values used than the objective counts | a `used[c]` binary linked to `x[v, c]` only through some constraints (edges), so an unconstrained `x[v, c]` escapes it | link every assignment: `x[v, c] <= used[c]` for all `v` ([example](assets/json-input/README.md)) |
| machines overlap, or slow big-M disjunctions | no-overlap written by hand | `addConsCumulative(starts, durs, [1] * k, 1)` per machine |
| `timelimit`, slow proof | weak formulation | one-hot binaries, indicators, no `abs`, symmetry breaking, implied constraints, tight bounds |
| `SyntaxError: encoding problem: one-hot` | a comment with `coding:` / `coding=` in a file's first two lines (`# Encoding: one-hot ...`) is read by Python as its encoding declaration | reword the comment or move it below line 2 |

## Further reading

- Documentation and tutorials: https://pyscipopt.readthedocs.io/en/latest/
- Model API reference: https://pyscipopt.readthedocs.io/en/latest/api/model.html
- SCIP parameters: https://www.scipopt.org/doc/html/PARAMETERS.php
- Examples: https://github.com/scipopt/PySCIPOpt/tree/master/examples/finished (`logical.py` for and/or/xor, `gcp.py` graph colouring, `sudoku.py`, `diet.py`, `piecewise.py`)
