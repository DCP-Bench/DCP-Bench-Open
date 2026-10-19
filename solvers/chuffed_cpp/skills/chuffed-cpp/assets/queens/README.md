# N-queens (satisfy, all solutions, no solution)

**Problem:** place n queens on an n x n board so that no two share a row, column or diagonal; n and the number of solutions wanted come from the command line.
**Shows:** a `Problem` subclass, `all_different` and `all_different_offset`, `branch`, `output_vars` (needed to get more than one solution), `so.nof_solutions` (0 = all), `print` called per solution, and reading `engine.status` / `engine.solutions` after the search, including a search that proves there is no solution.
**Run:** `cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build && ./build/model 8 && ./build/model 6 0 && ./build/model 3 0`
**Expected:** `n=8 status SAT (stopped at the solution limit), solutions 1`
**Expected:** `n=6 status COMPLETE, solutions 4`
**Expected:** `n=3 status COMPLETE, solutions 0`
**Expected:** `No placement exists`

Chuffed itself prints `----------` after each solution, `==========` when the search is complete, and `=====UNSATISFIABLE=====` when it found none. Without `output_vars(queens)` the enumeration stops after the first solution. Based on Chuffed's own `examples/queens.cpp`.
