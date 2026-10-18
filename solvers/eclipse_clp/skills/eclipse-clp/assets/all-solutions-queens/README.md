# N-queens (all solutions)

**Problem:** place 8 queens on an 8x8 board, none attacking another; list every solution.
**Shows:** decomposed `#\=` constraints with `fromto`/`foreach`/`count`, `labeling/1` inside the goal, `findall/3` to collect all solutions, filtering the collected list.
**Run:** `eclipse.exe -f model.ecl -e main` (`eclipse.exe` must be on PATH, or call it by its full path)
**Expected:** `92 solutions for 8 queens`
**Expected:** `first: [1, 5, 8, 6, 3, 7, 2, 4]`
**Expected:** `4 of them have the first queen in row 1`
**Time:** about 0.3 s wall, start-up included.
