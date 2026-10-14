---
name: pyscipopt
description: Write PySCIPOpt (SCIP) models, including SCIP's general constraints (and/or/xor, indicator, cardinality, SOS, nonlinear), and instance-agnostic models for the DCP-Bench scip_python integration with its build(instance) contract.
---

# PySCIPOpt (SCIP) models

PySCIPOpt 6.3.0 with SCIP 10.0.2. SCIP is a MIP solver that also handles general
constraints natively: logical and/or/xor, indicators, cardinality, SOS, and nonlinear
expressions. Use them where they state the problem directly; do not hand-linearise what
SCIP already supports.

## Modelling

- Variables: `m.addVar(name=, vtype="B"|"I"|"C", lb=, ub=)`; `ub=None` is infinity. Give
  every integer a tight finite `lb`/`ub` from the data.
- Linear constraints: `m.addCons(expr <= rhs)`, `>=`, `==`; sums with
  `quicksum(c * x[i] for i in I)`. Ranged `lo <= e <= hi` raises `TypeError`: write two
  constraints. `!=` is not supported (see below).
- Objective: `m.setObjective(expr, "minimize" | "maximize")`. It must be linear: for a
  nonlinear objective, minimise a variable `z` constrained by `z >= f(x)`.
- **Discrete choices: prefer one-hot binaries.** A variable that takes one of k values is
  best modelled as binaries `b[i, v]` with `quicksum(b[i, v] for v) == 1` and
  `x[i] == quicksum(v * b[i, v] for v)`. All-different is then `quicksum(b[i, v] for i) <= 1`
  per value; this is far stronger than pairwise `!=`.
- **`x != y` for a single pair**: a binary `d` with `addConsIndicator(x - y >= 1, d)` and
  `addConsIndicator(y - x >= 1, d, activeone=False)`.
- **Logic**: `addConsAnd(bs, r)` (r = b1 ∧ b2 ∧ …), `addConsOr(bs, r)`, all binary.
  `addConsXor(bs, rhs)` takes a Python bool `rhs`; for a variable parity use
  `quicksum(bs) == 2 * k + r`.
- **Indicators instead of big-M**: `addConsIndicator(lin_ineq, binvar=b)` enforces the
  inequality when `b == 1` (`activeone=False`: when `b == 0`). Only `<=`/`>=`; an equality
  needs two indicators on the same binary. **Always pass `binvar`**: without it SCIP
  segfaults at solve time. Indicators solved models where the big-M version timed out.
- **Counting and sparsity**: `addConsCardinality(xs, k)` (at most k nonzero),
  `addConsSOS1(xs)`, `addConsSOS2(xs)`.
- **Scheduling**: `addConsCumulative(starts, durations, demands, capacity)` with integer
  start variables and constant durations and demands.
- **Nonlinear**: `x * y`, `x ** 2`, `abs(e)`, `sqrt`, `exp`, `log`, `e / y` are accepted in
  constraints. Products of binaries and bounded integers are often better linearised
  (`z <= x`, `z <= y`, `z >= x + y - 1`) or written with indicators. An equality between
  products of integers (`a * b == n ** 2`) can be slow to prove; when the structure allows,
  search over the parameter that determines the factors instead.
- **`abs` is slow in constraints.** `d == abs(x - y)` timed out from about 13 variables
  where a sign binary `s` with indicators (`d == x - y` when `s == 1`, `d == y - x` when
  `s == 0`, two indicators each) was fast. `abs(e) <= k` is two linear inequalities.
- **Search help**: break symmetry by fixing interchangeable objects (the first round of
  an assignment, `x[0] < x[n-1]` for a sequence whose reversal is also a solution), and
  add redundant constraints derived from the data (counts per value or per period,
  cumulative constraints on the axes of a packing). Both turned timeouts into solves.
- **Not available**: Python `min`/`max` over variables (`NotImplementedError`), `//`, `%`.
  Encode `t <= x_i` (or `>=`) with the objective or a selector binary, and
  `x == d * q + r` with `0 <= r <= d - 1`.

## Solving and pitfalls

- `m.optimize()`, then `m.getStatus()`: `"optimal"` (proven; the default gap is 0),
  `"infeasible"`, `"timelimit"`, … Read values only when a solution exists:
  with no incumbent `getVal` silently returns 0. `m.getBestSol()[expr]` evaluates expressions.
- Changing a solved model needs `m.freeTransform()` first. Do not catch a rejected
  `addCons` and continue: a later solve can segfault.
- `m.count()` is unreliable with indicators (returned 0 where solutions exist); enumerate
  with no-good constraints instead.
- `m.hideOutput()` silences the solver log.
- Python reads a comment containing `coding:` or `coding=` in the first two lines of a
  file as its encoding declaration (`# Encoding: ...` fails with "unknown encoding").

## DCP-Bench (`scip_python`)

- **Contract**: one file with `build(instance)` returning `(model, outputs)`. `instance` is
  the instance dict; read only the fields you use and take every size from the data (the
  brief's shapes come from the example instance). `outputs` maps each declared output name
  to a variable, an expression, an int, or a (nested) list of them, with integer values.
  Do not call `optimize()`, set limits, threads, gap or presolve: the runner does.
- **Runner**: solves in a worker process with one thread and the request's time limit,
  sets the gap to 0, emits solutions only for a proven optimum (`timeout` otherwise), then
  enumerates further optima by fixing the objective and adding no-goods on the outputs.
  A crash, `sys.exit` or abort is reported as `error` with its signal or status. Status
  `limit` means the solution limit was reached, not a failure.
- **Objective**: hold it in a bounded integer variable (`z == expr`, bounds from the data,
  `setObjective(z)`). With a bare expression, one model proved its optimum in 2 s and then
  timed out searching for the second optimal solution.
- **Readability**: open the file with a `#` line stating the problem, and start each
  block of constraints with a `#` comment taken from the problem description.
- **Check**: `python -m evaluation.check MODEL.py --problem P --solver scip_python
  --instance-count 2 --solution-limit 2`, then `python -m generation.manage evaluate`.
  Read the per-instance results: a top-level `accepted` can hide skipped timeouts.

```python
from pyscipopt import Model, quicksum

# n-queens: place n queens so that no two attack each other.
def build(instance):
    n = instance["n"]
    m = Model()
    b = {(r, c): m.addVar(vtype="B") for r in range(n) for c in range(n)}
    # one queen per row and per column
    for i in range(n):
        m.addCons(quicksum(b[i, c] for c in range(n)) == 1)
        m.addCons(quicksum(b[r, i] for r in range(n)) == 1)
    # at most one queen per diagonal
    for d in range(-n + 1, n):
        m.addCons(quicksum(b[r, r - d] for r in range(n) if 0 <= r - d < n) <= 1)
        m.addCons(quicksum(b[r, d + n - 1 - r] for r in range(n) if 0 <= d + n - 1 - r < n) <= 1)
    # the output gives each row's queen column, numbered from 1
    queens = [quicksum((c + 1) * b[r, c] for c in range(n)) for r in range(n)]
    return m, {"queens": queens}
```

The example is accepted on all instances of `csplib_054_n_queens`.

Sources and version notes: `sources.md`.
