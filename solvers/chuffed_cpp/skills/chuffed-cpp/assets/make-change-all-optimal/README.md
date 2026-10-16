# Make change, all optimal solutions

**Problem:** pay 10 with coins of value 2, 3, 4, 5, 6, 7 using as few coins as possible, then list every way to pay with that many coins.
**Shows:** the all-optimal pattern in two solves: `fork()` a child that minimises and sends `engine.best_sol` back through a pipe (Chuffed's globals cannot be reset, so one process solves once), then build the model again in the parent with `int_rel(total, IRT_EQ, optimum)`, no `optimize`, `output_vars` on the decisions, `so.nof_solutions = 0`, and `engine.setSolutionCallback` to print each solution.
**Run:** `cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build && ./build/model`
**Expected:** `Optimal coins: 2`
**Expected:** `pay 3 7`
**Expected:** `pay 5 5`
**Expected:** `Optimal solutions: 3`

POSIX only (`fork`, `pipe`). Elsewhere, run the program twice: once to get the optimum, once with it as an argument. The optimum and the count were checked by enumerating every combination of coins.
