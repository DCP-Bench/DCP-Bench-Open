# Six queens (all solutions)

**Problem:** list every placement of 6 non-attacking queens on a 6 x 6 board (there are 4).
**Shows:** a `given` read from a parameter file (`n6.param`), `allDiff` over comprehensions, `branching on`, `-all-solutions` with `-S0` so that no solution is lost, solutions on stdout separated by `----------`. Without `-solutions-to-stdout` they go to `n6.param.solution.000001` to `.000004`.
**Run:** `savilerow queens.eprime n6.param -run-solver -all-solutions -S0 -solutions-to-stdout`
**Expected:** `letting q be [2, 4, 6, 1, 3, 5]`
**Expected:** `letting q be [3, 6, 2, 5, 1, 4]`
**Expected:** `letting q be [4, 1, 5, 2, 6, 3]`
**Expected:** `letting q be [5, 3, 1, 6, 4, 2]`
