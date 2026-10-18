# Knapsack (maximise)

**Problem:** 0/1 knapsack with 5 items, capacity 26; maximise the total value.
**Shows:** `bb_min/3` minimising a negated value (a variable, not an expression), `bb_options` that silence the "Found a solution" lines, `search/6` with `complete`.
**Run:** `eclipse.exe -f model.ecl -e main` (`eclipse.exe` must be on PATH, or call it by its full path)
**Expected:** `Chosen: [0, 1, 1, 1, 0]`
**Expected:** `Value: 51`
**Time:** about 0.3 s wall, start-up included.
