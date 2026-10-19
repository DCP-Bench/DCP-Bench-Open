# Sources for `cpmpy-python`

Tested with CPMpy 1.0.0, OR-Tools 9.15.6755, NumPy 2.5.3, Python 3.12.11, Linux (Docker image).

Existing skills: none found for CPMpy (not searched on skills.sh in this refactor).

- <https://cpmpy.readthedocs.io/en/latest/> — CPMpy documentation: model, variables, global constraints, globals functions, solver interface, OR-Tools backend
- <https://github.com/CPMpy/cpmpy> — CPMpy 1.0.0, source and README (installation, extras)
- <https://github.com/CPMpy/cpmpy/tree/master/examples> — the official examples folder (pattern reference)

Verified by running: every name in the API tables resolves in `cpmpy` 1.0.0; every example in `assets/` and every snippet in `SKILL.md` ran inside the image; `Cumulative` and `NoOverlap` take `end` as optional; built-in `max`, `min`, `any`, `all` raise `ValueError: __bool__ should not be called on a CPMPy expression`; built-in `sum` yields the same expression as `cp.sum`; a float coefficient raises `TypeError: Multiplication does not support float constants`; a NumPy array indexed by a variable raises `IndexError`, while `cp.cpm_array(...)` works; `solveAll` on a model with an objective raises `NotSupportedError` under OR-Tools; `solveAll` counts a free auxiliary variable as duplicates (6 solutions became 12 with one free Boolean; 10 instead of 6 in an earlier probe), while an auxiliary fixed by the outputs and diagonal expressions such as `q[i] + i` give no duplicates (16 and 24 counted correctly); `cp.max` and `cp.Maximum` build identical expressions, and `cp.max` accepts several arguments; `NValue` as an objective gives the number of distinct values (3 for a 5-cycle with a chord); `minimize(cp.max(colour))` gives colours minus one; a job-shop model with one `NoOverlap` per machine (`zip(*tasks)` unpacking) proves makespan 11 on the 3x3 example in `assets/scheduling-jobshop`; satisfaction problems report `FEASIBLE`; a tiny time limit gives `UNKNOWN`; the installed metadata requires Python 3.10+ and pulls in `ortools`.

Refactored from an earlier integration skill; examples verified inside the same Docker image.

## Independent toy-test (add-solver)

A tester who had only this skill solved the add-solver toy problems. Result: **18/18 passed**, 0 repair attempts.

| Problem | Instance | Result |
|---|---|---|
| cryptarithm | ab-ab-aaa | PASS, infeasibility reported |
| cryptarithm | send-more-money | PASS, feasible solution |
| cryptarithm | two-two-four | PASS, feasible solution |
| graph-colouring | cycle6 | PASS, optimal (2) |
| graph-colouring | k4-tail | PASS, optimal (4) |
| graph-colouring | petersen | PASS, optimal (3) |
| jobshop | ft06 | PASS, optimal (55) |
| jobshop | small | PASS, optimal (11) |
| knapsack | p01 | PASS, optimal (309) |
| knapsack | small | PASS, optimal (15) |
| knapsack-all-optimal | fourteen | PASS, all 9 optimal solutions |
| knapsack-all-optimal | ties | PASS, all 5 optimal solutions |
| knapsack-all-optimal | unique | PASS, all 1 optimal solutions |
| n-queens | n3 | PASS, infeasibility reported |
| n-queens | n4 | PASS, feasible solution |
| n-queens | n8 | PASS, feasible solution |
| n-queens-all | n6 | PASS, all 4 solutions |
| n-queens-all | n8 | PASS, all 92 solutions |

Gaps the tester reported, and where they are now covered: no NoOverlap example (now
`assets/scheduling-jobshop` and the disjunctive snippet); `max`/`min` naming (Modelling,
Naming paragraph); distinct-value objectives (Scheduling and objectives); job-order
precedences (Scheduling and objectives); the eval assertion on built-in `sum` (fixed in
`evals/evals.json`); solveAll with expression-valued constraints (All solutions).
