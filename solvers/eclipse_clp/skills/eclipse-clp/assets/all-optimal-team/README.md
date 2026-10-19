# All optimal solutions

**Problem:** pick 3 of 5 people with costs 3, 1, 4, 1, 3 for the cheapest team; list every team at that cost.
**Shows:** `bb_options{solutions:all}` makes `bb_min/3` backtrack through every optimal solution; the same result in two steps (find the optimum, then `findall/3` under that bound).
**Run:** `eclipse.exe -f model.ecl -e main` (`eclipse.exe` must be on PATH, or call it by its full path)
**Expected:** `2 optimal teams`
**Expected:** `cost 5: [0, 1, 0, 1, 1]`
**Expected:** `two-step check: 2 teams at cost 5`
**Time:** about 0.3 s wall, start-up included.
