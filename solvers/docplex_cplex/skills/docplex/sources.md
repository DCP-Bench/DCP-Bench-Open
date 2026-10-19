# Sources for `docplex`

Tested with docplex 2.32.264 and cplex 22.2.0.1 (CPLEX Community Edition), Python 3.12.11, Linux container.

Existing skills: not searched in this refactor (the skill predates it). `llms.txt` at the docs root returned 404 when checked.

Refactored from an earlier integration skill; examples verified inside the same container.

Documentation this skill was written from. Add an entry whenever a claim here comes from a specific page or version.

- <https://pypi.org/project/cplex/22.2.0.1/>: the cplex wheel, "A Python interface to the CPLEX Callable Library, Community Edition". Accessed 2026-09-28.
- <https://pypi.org/project/docplex/2.32.264/>: DOcplex 2.32.264, the IBM Decision Optimization modelling API for Python. Accessed 2026-09-28.
- <https://github.com/IBMDecisionOptimization/docplex>: the DOcplex repository, which gives the Community Edition limit as 1000 variables and 1000 constraints. Accessed 2026-09-28.
- <https://ibmdecisionoptimization.github.io/docplex-doc/getting_started_python.html>: installation with pip and conda. Accessed 2026-10-15.
- <https://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html> and `docplex.mp.solution.html`: the `Model` and solution API, `populate` and `SolutionPool`, `add_indicator`, `add_equivalence`, `add_if_then`. Accessed 2026-10-15.

Verified by running (in the image, Python 3.12 with docplex 2.32.264 and cplex 22.2.0.1):

- Engine reports itself as CPLEX 22.2.0.0; `import numpy` fails, since neither wheel depends on it.
- A model with 1001 variables, or with 1001 constraints, raises `DOcplexLimitsExceeded`: "Promotional version. Problem size limits (1000 vars, 1000 consts) exceeded ... CPLEX code=1016". 600 linear constraints plus 400 indicators solve; plus 401 indicators fail, so indicators count as constraints.
- With the default `mip.tolerances.mipgap` (1e-4), a 40-item knapsack (weights random 1..1000 with seed 27, values weight + 100, capacity half the total weight) returned status 102 at 12860; with the gap at 0 it returned status 101 at 12861.
- Exact status strings (`m.solve_details.status`) and what `solve()` returns:
  - `integer optimal solution` (101), with a solution; also for a feasible model with no objective.
  - `integer optimal, tolerance` (102), with a solution.
  - `time limit exceeded` (107), with a solution and a nonzero `mip_relative_gap` (0.0024 measured on a 600-item, 10-constraint knapsack with a 2 s limit).
  - `time limit exceeded, no integer solution` (107), `solve()` returns `None` (120-variable equality subset-sum with a 2 s limit).
  - `integer infeasible` (103), `None`.
  - `integer infeasible or unbounded` (119) with presolve on; `integer infeasible` (103) with presolve off.
  - `integer unbounded` (118).
  - `Non-convex QCP`: `solve()` returns `None` after CPLEX prints "Model has non-convex quadratic constraint".
  - `populate solution limit exceeded` and `all reachable solutions enumerated, integer optimal` from `populate()`.
  - An LP reports `optimal`.
- `set_time_limit` below 1 second is raised to 1 with a warning.
- `has_objective()` is false with no objective and after `minimize(0)`, and true after `minimize(5)`.
- `populate()` with `intensity = 4`, `relgap = absgap = 1e75` enumerates every feasible solution. The default `mip.limits.populate` is 20, and with it the 92 solutions of 8-queens stopped at 24 with `populate solution limit exceeded`; the pool is complete with `mip.limits.populate` raised (92). Auxiliary variables duplicate solutions. With `relgap = absgap = 0` it returns only the optimal solutions.
- The no-good loop and the pool agree on the counts of the examples checked: subset-sum and assignment (the examples), and 8-queens (92 by either path).
- Timings (wall time of the whole script, toy-problem instances, see SKILL.md Speed): n-queens-all n8 with the no-good loop 21.35 s; `populate()` alone on n8 0.68 s; ft06 jobshop (indicator encoding) 0.54 s; all other toy instances under 1.0 s.
- `x != y`, `model.abs`, `model.max`, `model.min`, `logical_and`, `logical_or`, `add_equivalence`, `add_indicator` (with `active_value`), `add_if_then` build and solve.
- `x * y == 12` is accepted by docplex and refused by CPLEX with "Non-convex QCP"; the message is printed.
- `bool(x == 1)` raises `TypeError: Cannot convert linear constraint to a boolean value`; `x // 2` and `x % 2` raise `TypeError`.
- Every python block of `references/encodings.md` was run as a complete program (preamble first, then the block), enumerated with `populate()`, and its projection on the named variables compared with a brute-force enumeration over the same small domains. All blocks matched.
- The helper cost table in SKILL.md was measured with `number_of_variables` and `number_of_constraints` before and after each posting.
- The Quick start, the program template in SKILL.md (run on the knapsack small instance and on a negative-capacity instance that prints the unsatisfiable line), and the seven example programs run inside the image and print their Expected lines.

Independent toy test: an agent that read only this skill (the refactor did not write any of the test models) solved the add-solver toy problems. Each model was run as `python3 <model> <instance.json>` in the same container and checked with the toy-problem checker.

| Problem | Instance | Result |
|---|---|---|
| cryptarithm | ab-ab-aaa | pass: infeasibility reported |
| cryptarithm | send-more-money | pass: feasible solution |
| cryptarithm | two-two-four | pass: feasible solution |
| graph-colouring | cycle6 | pass: optimal (2) |
| graph-colouring | k4-tail | pass: optimal (4) |
| graph-colouring | petersen | pass: optimal (3) |
| jobshop | ft06 | pass: optimal (55) |
| jobshop | small | pass: optimal (11) |
| knapsack | p01 | pass: optimal (309) |
| knapsack | small | pass: optimal (15) |
| knapsack-all-optimal | fourteen | pass: all 9 optimal solutions |
| knapsack-all-optimal | ties | pass: all 5 optimal solutions |
| knapsack-all-optimal | unique | pass: all 1 optimal solutions |
| n-queens | n3 | pass: infeasibility reported |
| n-queens | n4 | pass: feasible solution |
| n-queens | n8 | pass: feasible solution |
| n-queens-all | n6 | pass: all 4 solutions |
| n-queens-all | n8 | pass: all 92 solutions |

Total: 18/18 passed. The first version of the skill had no program template, so the tester wrote the I/O pattern itself; the template in SKILL.md now shows it.
