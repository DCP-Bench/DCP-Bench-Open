# Toy problems

Solver-independent tests for a new solver skill. Give the agent under test only what `scripts/run_toy_tests.py --export DIR` writes: each `problem.md` and `instances/`, and the output convention below. `expected/` (the answer key) and `check.py` are for the runner alone; never mount this folder where the tester's code runs.

| Problem | Instances (answer) | Tests: a FAIL means the skill lacks this |
|---|---|---|
| `n-queens` | n4, n8, n3 (infeasible) | all-different; infeasibility read from the status, not from an exception or empty output |
| `n-queens-all` | n6 (4), n8 (92) | enumeration over the output variables only (auxiliary variables cause duplicates) |
| `knapsack` | small (15), p01 (309) | maximise; checking the optimum is proven, not just found (`FEASIBLE` on timeout) |
| `knapsack-all-optimal` | ties (5 at 4), unique (1 at 15), fourteen (9 at 39) | all optimal solutions: solve, post `(objective) = optimum`, enumerate |
| `graph-colouring` | petersen (3), cycle6 (2), k4-tail (4) | minimise; optimum differs per instance |
| `cryptarithm` | send-more-money, two-two-four, ab-ab-aaa (infeasible) | constraints built from data; infeasibility |
| `jobshop` | small (11), ft06 (55) | the no-overlap / disjunctive global or standard encoding (naive big-M times out on ft06) |

Two failures cut across problems:

- **Only instances with `name` / `note` keys fail**: the skill's data reading binds every key. `problem.md` leaves these keys out on purpose.
- **`exit code` with no useful message**: the skill does not say where the solver writes its errors.

## Output convention (test only)

- One program per problem, named after the problem directory with its hyphens kept (`models/n-queens-all.py`); a compiled language builds first and runs the binary.
- The model is run with the instance JSON path as its only argument.
- Each solution is printed as one JSON object on one line on stdout. Lines not starting with `{` are ignored.
- An infeasible instance prints exactly `{"status": "unsatisfiable"}`.
- Optimisation problems print exactly one solution, and it must be optimal; `knapsack-all-optimal` prints every optimal solution, each once.
