# Routing tour (circuit)

**Problem:** shortest tour through 6 cities given a distance matrix.
**Shows:** successor variables with `circuit/1` (library `ic`), `element/3` to read the chosen arc length from a matrix row, `nth1/3` from `lib(listut)` to follow the tour, `bb_min/3`.
**Run:** `eclipse.exe -f model.ecl -e main` (`eclipse.exe` must be on PATH, or call it by its full path)
**Expected:** `Tour length: 44`
**Expected:** `Tour: [1, 2, 4, 6, 5, 3]`
**Time:** about 0.3 s wall, start-up included.
