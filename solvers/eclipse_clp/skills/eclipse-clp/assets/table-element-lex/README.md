# Table, element, lexicographic order

**Problem:** three stops from 1..5, consecutive stops must form an allowed pair, each stop has a cost; the stop vector is compared with its mirror to cut symmetric routes.
**Shows:** `table/2` from `lib(ic_mdd)`, `element/3` (1-based), `lex_le/2` and `sorted/2` from `lib(ic_global)`, `findall/3` over `labeling/1`.
**Run:** `eclipse.exe -f model.ecl -e main` (`eclipse.exe` must be on PATH, or call it by its full path)
**Expected:** `4 routes`
**Expected:** `[2, 3, 4] cost 6`
**Expected:** `sorted: [7, 3, 2, 9] -> [2, 3, 7, 9]`
**Time:** about 0.3 s wall, start-up included.
