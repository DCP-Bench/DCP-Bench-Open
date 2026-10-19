# Sources for `gurobipy`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

Tested with gurobipy 13.0.3 (Gurobi Optimizer 13.0.3), Python 3.12.11, NumPy 2.4.6 and SciPy 1.18.1, inside the image `dcp-eval/gurobipy_python:v1` (Debian 12, Linux, no network).

Existing skills: not searched in this refactor; the content is carried over from the integration's earlier skill.

Independent toy-problem test (add-solver step 4, fresh agent, skill only): 18/18 instances passed, zero repair attempts. Results file: scratchpad skill-refactor/gurobipy_python/test/results.txt.

| Problem | Instances | Passed |
|---|---|---|
| cryptarithm | ab-ab-aaa, send-more-money, two-two-four | 3/3 |
| graph-colouring | cycle6, k4-tail, petersen | 3/3 |
| jobshop | ft06, small | 2/2 |
| knapsack | p01, small | 2/2 |
| knapsack-all-optimal | fourteen, ties, unique | 3/3 |
| n-queens | n3, n4, n8 | 3/3 |
| n-queens-all | n6, n8 | 2/2 |
| **Total** | | **18/18** |

Refactored from the DCP-Bench integration skill; examples verified inside the dcp-eval/gurobipy_python:v1 image.

- <https://pypi.org/project/gurobipy/> — gurobipy 13.0.3 wheel: Gurobi Optimizer shipped with a size-limited licence; wheels for CPython 3.10 to 3.13 on manylinux2014 x86_64. Accessed 2026-09-28.
- <https://docs.gurobi.com/projects/optimizer/en/current/reference/python.html> — Python API reference; `Model.addVar`, `addVars`, `addMVar`, `addConstr`, `computeIIS` on <https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html>; `quicksum` on `func_global.html`; `abs_`, `max_`, `min_`, `and_`, `or_` on `func_utility.html`. The `>>` indicator syntax is in the Model reference. Accessed 2026-09-28.
- <https://docs.gurobi.com/projects/optimizer/en/current/reference/numericcodes/statuscodes.html> — status codes 1 to 19; used for the status table (checked 2026-10-15).
- <https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html> — `MIPGap`, `IntFeasTol`, `TimeLimit`, `Threads`, `Seed`, `OutputFlag`, `DualReductions`, `PoolSearchMode`, `PoolSolutions`, `PoolGap`. Accessed 2026-09-28.
- <https://support.gurobi.com/hc/en-us/articles/360051597492> — the size-limited licence: 2000 variables and 2000 linear constraints, 200 variables with quadratic terms, and the error text "Model too large for size-limited license". Accessed 2026-09-28.
- <https://docs.gurobi.com/projects/optimizer/en/13.0/features/solutionpool.html> — Solution Pool guide (13.0): `PoolSearchMode` 2 keeps searching for the n best, `PoolSolutions` caps how many are stored, `PoolGap`; cited for the pool section. Accessed 2026-10-15 (the earlier 404 was on a different URL).
- <https://support.gurobi.com/hc/en-us/articles/13210193318033> and <https://support.gurobi.com/hc/en-us/articles/360037221732> — why the pip licence is the only one usable in a networkless container: an Academic Named-User licence cannot run in a container, and an Academic WLS licence needs internet while it runs. Accessed 2026-09-28.

Verified by running (inside `dcp-eval/gurobipy_python:v1`):

- Licence banner `Restricted license - for non-production use only - expires 2027-11-29` on the first model; `gp.gurobi.version()` is `(13, 0, 3)`.
- A model over 2000 variables, or over 2000 constraints counting linear and general constraints together, raises `GurobiError` 10010 at `optimize()`. With one quadratic constraint, 199 variables solve and 201 fail; `addGenConstrNL` and `addGenConstrPow` fail at 300 variables.
- `addConstr(x != y)` raises `GurobiError: Inequality constraints not supported`; `x // 2` and `x % 2` raise `TypeError`; `bool(x <= y)` raises `GurobiError: Constraint has no bool value`; `gp.abs_(a - b)` raises `TypeError ... is not a variable`.
- `x * y` over two variables returns a `QuadExpr`; `x * y == 12` solves without further parameters.
- A model with no `setObjective` call has an empty objective and `NumObj == 1`, the satisfaction case.
- `MVar.sum()` raised `ModuleNotFoundError: No module named 'scipy'` before SciPy was in the image.
- `getParamInfo("MIPGap")` reports default `0.0001`. A random 40-item strongly correlated knapsack (seed 3) reports `OPTIMAL 12950` with the default gap and `12951` with `MIPGap = 0`; seeds 1, 2, 4 and 5 agree between the two settings.
- Solution pool: `PoolSearchMode = 2` with `PoolSolutions = 2_000_000_000` returns exactly the feasible solutions for an 8-queens model (92) and for 3-of-6 subsets with sum 10 (3); with `PoolGap = 0` and the objective kept, a maximise over 4 binaries with at most 2 ones returns all 6 optimal solutions.
- `computeIIS` on `a >= 7`, `a <= 3` reports the two named constraints.
- The licence banner is printed to stdout at the first `gp.Model`; `model.Params.OutputFlag = 0` set after creation does not hide it, while `gp.Env(params={"OutputFlag": 0})` does (probed in the image, gurobipy 13.0.3).
- Solution pool cap: with `PoolSearchMode = 2`, `PoolSolutions = 2` on a model with 3 feasible solutions returns `SolCount` 2 with status `OPTIMAL`; `PoolSolutions = 3` and `10` return 3 (probed in the image). Hence `SolCount == PoolSolutions` is treated as possibly truncated.
- `addVars` keys: a list of strings gives string keys; a list of tuples gives tuple keys; two lists give `(a, b)` tuple keys; `x.sum(i, "*")` and `x.sum("*", j)` work on the result.
- Jobshop ft06 (`ft06.json` from add-solver toy problems), `MIPGap = 0`: indicator no-overlap and big-M no-overlap both reach 55 in about 0.01 to 0.02 s (three runs each).
- Every encoding in `references/encodings.md` (`!=`, reified equality, `abs_` through an auxiliary variable, element, all-different, binary-integer product, `//` and `%`, `max_`, `min_`, `and_`, `or_`, disjunction) was solved on small instances and matched its intended value.
