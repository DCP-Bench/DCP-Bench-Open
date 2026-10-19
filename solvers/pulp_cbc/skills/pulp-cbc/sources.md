# Sources for `pulp-cbc`

Tested with PuLP 3.3.2 (which bundles CBC 2.10.3), Python 3.12.11, on Linux x86_64, inside a container image.

Existing skills: none searched for this version; the skill was refactored from an earlier integration skill, which holds the API facts below.

- <https://coin-or.github.io/pulp/technical/pulp.html> — PuLP API reference (accessed 2026-09-14, and the variable, problem and solve calls checked in 2026-10-15)
- <https://coin-or.github.io/pulp/> — PuLP user guide (accessed 2026-09-14)
- <https://coin-or.github.io/pulp/technical/solvers.html> — CBC parameters: `timeLimit`, `threads`, `logPath`, `timeMode` (accessed 2026-10-15)
- <https://coin-or.github.io/pulp/guides/how_to_configure_solvers.html>, `how_to_debug.html`, `how_to_mip_start.html` — solver configuration, debugging, warm starts (accessed 2026-10-15)
- <https://coin-or.github.io/pulp/guides/how_to_migrate_to_v4.html> — PuLP 4.0 changes: `LpVariable(...)` replaced by `add_variable`, `PULP_CBC_CMD` removed, CBC no longer bundled (accessed 2026-10-15; read, not run, as 4.0 is not installed in the image; unverified)
- <https://pypi.org/project/PuLP/3.3.2/> — PuLP 3.3.2, the tested version; 4.0.1 is on PyPI since 2026-10-14, which is why the install range stops below 4
- <https://coin-or.github.io/pulp/CaseStudies/a_set_partitioning_problem.html>, `a_sudoku_problem.html` — case studies linked from Further reading

Verified by running (inside the image): `x*y`, `x*x`, `abs(x)`, `x/y` and `x%2` raise `TypeError`, while `x/2` is linear; `x != y` adds no constraint and raises no error; a second bare objective overwrites the first with a `UserWarning`; a `Binary` reports `Integer` with bounds 0 and 1, and an unbounded `Integer` reports `None`; a satisfaction problem with no objective solves with status 1 and `objective` `None`; `add_variable_dicts` with two index sets gives `x[i][j]`, and `x[i, j]` raises `KeyError`; a 200-item, 10-constraint knapsack under `timeLimit=2` gives status `Optimal` with `sol_status` 2; a 60-item equality subset-sum under `timeLimit=2` gives status 0 with no values; an infeasible model gives status -1 and an unbounded one -2; the satisfaction snippet in SKILL.md gives "satisfiable" (`Optimal`, `sol_status` 1), "unsatisfiable" (`Infeasible`, -1) and "unknown" (`Not Solved`, 0, under a time limit); `PULP_CBC_CMD().available()` returns the bundled binary's path; `COIN_CMD` without a path fails to find `cbc`; `PULP_CBC_CMD(path=...)` raises `PulpSolverError` (use `COIN_CMD(path=...)`); `msg=True` prints CBC's log to stdout, `logPath` writes a file, and `writeLP` works; `sum()` takes 0.28 s and `pulp.lpSum` 0.001 s on 3,000 variables; the AND, all-different and disjunction encodings solve to the expected values; every program in `assets/` prints its README's expected output; the job-shop example (`assets/job-shop-makespan`) gives makespan 11, matching a brute-force search over machine orders.

Independent toy-problem test (a fresh agent given only SKILL.md and `assets/`, before this revision; the add-solver runner in the same image): 18/18 passed, with 0 repair attempts used.

| Problem / instance | Result |
|---|---|
| cryptarithm/ab-ab-aaa | PASS: infeasibility reported |
| cryptarithm/send-more-money | PASS: feasible solution |
| cryptarithm/two-two-four | PASS: feasible solution |
| graph-colouring/cycle6 | PASS: optimal (2) |
| graph-colouring/k4-tail | PASS: optimal (4) |
| graph-colouring/petersen | PASS: optimal (3) |
| jobshop/ft06 | PASS: optimal (55) |
| jobshop/small | PASS: optimal (11) |
| knapsack/p01 | PASS: optimal (309) |
| knapsack/small | PASS: optimal (15) |
| knapsack-all-optimal/fourteen | PASS: all 9 optimal solutions |
| knapsack-all-optimal/ties | PASS: all 5 optimal solutions |
| knapsack-all-optimal/unique | PASS: all 1 optimal solutions |
| n-queens/n3 | PASS: infeasibility reported |
| n-queens/n4 | PASS: feasible solution |
| n-queens/n8 | PASS: feasible solution |
| n-queens-all/n6 | PASS: all 4 solutions |
| n-queens-all/n8 | PASS: all 92 solutions |

Total: 18/18 passed. The tester's gaps (job shop, `!=` big-M rule, `msg=True` on parsed stdout, satisfaction status, pinned objective, unverified 4.0 claims) were closed in SKILL.md and `assets/job-shop-makespan`; the toy-test rerun against this revision is not yet done.

Refactored from that earlier integration skill; examples verified inside the same image.
