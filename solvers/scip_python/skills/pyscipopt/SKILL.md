---
name: pyscipopt
description: Write instance-agnostic PySCIPOpt models for the DCP-Bench scip_python integration, covering the build(instance) contract, how the runner proves optimality and enumerates optima, the SCIP API for variables, linear and general constraints, and the sequences that crash SCIP.
---

# PySCIPOpt models for `scip_python`

Write one Python file that builds a `pyscipopt.Model` from instance data. The runner
solves it inside a container, proves the optimum, and enumerates solutions. You never
call `optimize()` or read values yourself.

Image: Python 3.12 with PySCIPOpt 6.3.0 (SCIP 10.0.2 inside the wheel) and NumPy 2.4.6.
Imports available: `pyscipopt` and `numpy`. Nothing else is installed.

## Contract

```python
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    model = Model()
    x = model.addVar(name="x", vtype="I", lb=0, ub=n)
    y = model.addVar(name="y", vtype="I", lb=0, ub=n)
    if instance["optimize"]:
        model.addCons(x + y >= n)
        model.setObjective(x + y, "minimize")
    else:
        model.addCons(x + y == n)
    return model, {"x": x, "y": y}
```

- `build(instance)` returns `(model, outputs)`. `instance` is a dict with exactly the
  fields the instance provides; read only the ones you use.
- `outputs` is a nonempty dict. Its keys are the declared output names, and each value is
  a variable, a linear expression, or a list/nested list of those, with integer values.
- The objective is whatever you set with `setObjective(expr, "minimize" | "maximize")`.
  An objective with no variable terms, or none at all, is a satisfaction problem.
- The objective must be linear. SCIP rejects a product of variables in `setObjective`;
  use an epigraph variable `z` with `z == x*x` style constraints instead.

## What the runner does

1. Runs the model in a worker process, with `hideOutput`, one thread, and the time budget
   from the request.
2. Sets `limits/gap` and `limits/absgap` to 0 after `build` returns. `optimal` therefore
   means proven, whatever the model set.
3. Reports `unsat` on `infeasible`, `unbounded` as an error, and anything short of a
   proven optimum as `timeout` with no solution. No incumbent is ever emitted for an
   optimization that is not proven.
4. For enumeration, pins the objective to the proven optimum (`obj >= best` and
   `obj <= best`, with a 0.5 band for integer objectives), sets the objective to 0, and
   adds one no-good per solution over the variables the outputs are built from: a linear
   cut for binaries, indicator constraints with explicit binary selectors for general
   integers. Solutions are deduplicated on the declared outputs.
5. Rounds integer outputs. A continuous declared value must be integral within 1e-6, or
   the run is an error.

A worker that dies (a signal, `sys.exit`, `os.abort`) is reported as `error` with the
signal or exit status in the detail. Do not wrap solver calls in `try` blocks to hide
failures; the runner needs the error to surface.

## Variables and linear constraints

- `model.addVar(name=, vtype=, lb=, ub=)`. `vtype` is `"B"` (binary), `"I"` (integer) or
  `"C"` (continuous, the default). `"X"` raises a warning and creates nothing useful.
- `ub=None` means infinity. An unbounded integer output still enumerates through
  indicator no-goods.
- Constraints: `model.addCons(expr <= rhs)`, `>=`, `==`. Build sums with
  `quicksum(c * x[i] for i in ...)`.
- Ranged constraints (`1 <= x <= 3`) raise `TypeError`; write two constraints.
- `x != y` is not supported. Encode it with a binary and two indicators, or with
  `addConsIndicator` as shown below.

## General constraints

- `model.addConsAnd(vars, resvar)` and `addConsOr(vars, resvar)`: all binary.
- `model.addConsXor(vars, rhs)`: `rhs` is a Python bool, not a variable. For a variable
  result use the parity form `x + y + z == 2 * k` with integer `k` in `{0, 1}`.
- `model.addConsIndicator(cons, binvar=b)`: active when `b == 1`; use
  `activeone=False` for active when `b == 0`. `cons` must be a single inequality
  (`<=` or `>=`), not an equation. Always pass an explicit binary as `binvar`.
  Leaving `binvar` out crashes SCIP with SIGSEGV (verified). To state an equality, use
  two indicators on the same binary, one `<=` and one `>=`.
- `model.addConsCardinality(xs, k)`, `addConsSOS1(xs)`, `addConsSOS2(xs)`.
- `abs(x - 1)`, `x * y` in constraints, `sqrt`, `exp`, `log` are accepted as nonlinear
  constraints. `x // 2` and `x % 2` are not: encode `x == 2 * k + r`, `r` binary.
- Python `min` and `max` over variables raise `NotImplementedError`. Encode `t <= x`,
  `t <= y` and maximize `t`, or use a selector binary.
- There is no global all-different constraint. Encode pairwise differences with a binary
  per pair and two indicators (`activeone` true and false).

## Solutions and values

- Read values only after `optimize()` has finished with status `optimal`. With no
  incumbent, `getVal` returns 0.0 silently. The runner does this for you; in helper code,
  check `model.getStatus()` and `model.getBestSol()` first.
- `getBestSol()[expr]` evaluates a variable or an expression, constants included.
- `count()` is unreliable with indicator constraints: it returned 0 where six solutions
  exist. Do not use it. Enumeration is the runner's no-good loop.

## Crashes to avoid

- Modifying a solved model without `freeTransform()`: `addCons` or `addVar` after
  `optimize()` raises `Exception: method cannot be called at this time in solution process`.
- A rejected modification followed by `freeTransform()` and another solve segfaults
  (exit 139). Do not catch and continue after a rejected `addCons`; the runner needs the
  first error to stop the worker.
- Indicator constraint without `binvar`: SIGSEGV at solve time. Always pass the binary.

## Pitfalls that change the verdict

- Do not change `limits/gap` or `limits/absgap` to chase speed. The runner resets them to
  0, and the verdict depends on it.
- Do not call `setPresolve`, `setParam("limits/...")`, or `setIntParam` for threads.
  The runner sets them after `build`, and a changed value would only be overridden.
- Integer outputs whose solver value is 2.9999995 are rounded. A value 0.5 away from an
  integer is refused.

## Tiny reference models

- Satisfaction with enumeration: `x + y == n` over integers in `[0, n]` has `n + 1`
  solutions. Enumerating with `solution_limit` above that returns `complete`.
- Minimization with a tie: `x + y >= n`, minimize `x + y` has `n + 1` optima; the runner
  returns all of them and then `complete`.
- Maximization: `x + y <= n`, maximize `2 * x + y` has one optimum `x = n, y = 0`.

Verified models are in `tests/fixtures/model_scip.py` at the repository root and in
`solvers/scip_python/readiness_test.py`.

Sources and version notes: `sources.md` in this bundle.
