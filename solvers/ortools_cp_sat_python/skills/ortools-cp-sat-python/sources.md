# Sources for `ortools-cp-sat-python`

Tested with OR-Tools 9.15.6755 (`ortools.sat.python.cp_model`), Python 3.12.11, NumPy 2.5.3, Linux (Docker image `dcp-eval/ortools_cp_sat_python:v1`).

Existing skills: not searched in this refactor; the skill was written earlier as a DCP-Bench integration skill and is refactored here.

- https://developers.google.com/optimization/cp/cp_solver — CP-SAT guide, first-solution and all-solutions program (section "Finding all solutions")
- https://developers.google.com/optimization/install/python — install with pip
- https://or-tools.github.io/docs/pdoc/ortools/sat/python/cp_model.html — CP-SAT Python API reference (pdoc, v9.15)
- https://github.com/google/or-tools/blob/stable/ortools/sat/cp_model.proto — status definitions
- https://developers.google.com/optimization/scheduling/job_shop — interval variables and no-overlap pattern (the scheduling example is a different problem)

Refactored from the DCP-Bench integration skill; examples verified inside the dcp-eval/ortools_cp_sat_python:v1 image.

Independent toy-test (round 2): an add-solver tester solved the seven toy problems from this skill alone, with no repair attempts: 18/18 instances passed (n-queens 3/3, n-queens-all 2/2, knapsack 2/2, knapsack-all-optimal 3/3, graph-colouring 3/3, cryptarithm 3/3, jobshop 2/2).

Verified by running: install and `import` in the image; every example's Expected output (`check_assets.py`, 9 examples); the Quick start; `new_int_var` requires a name (TypeError); `bool(expr)`, `//`, `/` and `x*y` in constraints raise; float coefficients in a constraint raise, while `maximize(z*0.5)` solves OPTIMAL locally (1.5), so the runner's refusal of float objectives is the contract's rule, not a local failure; `validate()` on lb > ub returns a message and solving gives `MODEL_INVALID`; `enumerate_all_solutions` with the objective still set returns one optimal solution, and with the objective cleared all three optimal solutions (`assets/ties-all-optimal`); auxiliary variables multiply solutions in enumeration (6 instead of 3); a finished enumeration of `sum == 3` over six Booleans gives 20 solutions and status `OPTIMAL`; an infeasible enumeration (`sum == 5` over three Booleans) gives status `INFEASIBLE` and zero callbacks; `add_all_different` accepts linear expressions (`col[i] + i`, validate returns ''); a 1-second time limit on an optimisation gives `FEASIBLE` (objective 2084, bound 264); `solver.value` before `solve` raises RuntimeError; job-shop makespan 11 (`assets/jobshop-no-overlap`) matches a brute-force search over machine orders; the graph-colouring objective (largest index) gives 3 colours on the example graph, matching the chromatic number found by hand; scheduling makespan 11 for `assets/tasks-scheduling` matches a brute-force search over start times; sudoku, production and coin answers matched brute-force enumeration.

Links checked: the install page, CP-SAT guide (anchor `#finding_all_solutions`), pdoc reference and job-shop page return content.
