# Sources for `gurobipy`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://pypi.org/project/gurobipy/13.0.3/> — gurobipy 13.0.3, the version
  pinned in the integration image, which ships the Gurobi Optimizer and a
  size-limited licence; wheels for CPython 3.10 to 3.13 on manylinux2014 x86_64.
  Accessed 2026-09-28.
- <https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html>
  — `Model.addGenConstrIndicator`, `addGenConstrAbs` (both arguments are single
  `Var`s), the `abs_`, `max_`, `min_`, `and_`, `or_` helpers and the `>>`
  indicator syntax. Accessed 2026-09-28.
- <https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html>
  — `MIPGap`, `IntFeasTol`, `FeasibilityTol`, `Threads`, `TimeLimit`,
  `OutputFlag`, `DualReductions`. The page lists `MIPGap` with default `-1`;
  in the 13.0.3 wheel `getParamInfo("MIPGap")` reports a default of `1e-4`,
  which is the value the runner overrides. Accessed 2026-09-28.
- <https://support.gurobi.com/hc/en-us/articles/360051597492> — the size-limited
  licence: 2000 variables and 2000 linear constraints, 200 variables with
  quadratic terms, and the error text "Model too large for size-limited
  license". Accessed 2026-09-28.
- <https://support.gurobi.com/hc/en-us/articles/13210193318033> and
  <https://support.gurobi.com/hc/en-us/articles/360037221732> — why no other
  licence is used: an Academic Named-User licence cannot run in a container,
  and an Academic WLS licence needs an internet connection while it runs, which
  the evaluator's networkless containers do not have. Accessed 2026-09-28.
- `solvers/gurobipy_python/run.py` and `Dockerfile` in this repository — the
  contract this skill describes.

Every API claim below was checked by running it inside the integration image,
not taken from documentation alone:

- The licence banner `Restricted license - for non-production use only -
  expires 2027-11-29` is printed on standard output when the first model is
  created; `Model.LicenseExpiration` reports `20271129`.
- A model over 2000 variables, or over 2000 constraints counting linear and
  general constraints together (500 `abs_` plus 1501 linear fails, 500 plus
  1499 passes; the same with indicators), raises `GurobiError` 10010 at
  `optimize()`. With one quadratic constraint, 199 variables solve and 201 fail;
  `addGenConstrNL` and `addGenConstrPow` fail at 300 variables.
- `addConstr(x != y)` raises `GurobiError: Inequality constraints not
  supported`; `x // 2` and `x % 2` raise `TypeError`; `bool(x == 1)` raises
  `GurobiError: Constraint has no bool value`; `gp.abs_(a - b)` raises
  `TypeError ... is not a variable`.
- `x * y` over two variables returns a `QuadExpr`, and `x * y == 12` solves
  without further parameters, which is why the size limit, not an error, is
  what a product runs into.
- A model with no `setObjective` call has an empty `LinExpr` objective and
  `NumObj == 1`, which is how the runner tells satisfaction from optimization.
- The matrix API needs SciPy: `MVar.sum()` raised `ModuleNotFoundError: No
  module named 'scipy'` before SciPy was added to the image. `MVar` has
  `tolist()`, `MLinExpr` does not.
- **With the default `MIPGap`, Gurobi reported OPTIMAL at 12168379 on a
  40-item strongly correlated knapsack whose optimum is 12168772; with
  `MIPGap=0` it returns 12168772.** `solvers/gurobipy_python/readiness_test.py`
  has a `proven_optimum` check on that instance, which fails if the runner ever
  stops setting the gap.
- Every encoding in the skill (`!=`, `abs_` through an auxiliary variable,
  reified equality, disjunction, all-different, element, the binary-integer
  product, division and remainder, `max_`/`min_`/`and_`/`or_`) was checked by
  brute force over small domains against its intended meaning.
