# Magic square (satisfy)

**Problem:** 4x4 magic square, entries 1..16 all different, every row, column and diagonal sums to 34.
**Shows:** `dim/2` arrays, `M[1..N,1..N] :: 1..NN`, `flatten_array/2`, `collection_to_list/2` on a row or column slice, `alldifferent/1` with the `import` that resolves the `ic` / `ic_global` clash, `search/6`.
**Run:** `eclipse.exe -f model.ecl -e main` (`eclipse.exe` must be on PATH, or call it by its full path)
**Expected:** `[1, 2, 15, 16]`
**Expected:** `[8, 11, 6, 9]`
Output is one valid square; the search is deterministic, so the same square prints each run:
```
[1, 2, 15, 16]
[12, 14, 3, 5]
[13, 7, 10, 4]
[8, 11, 6, 9]
```
**Time:** about 0.3 s wall, start-up included.
