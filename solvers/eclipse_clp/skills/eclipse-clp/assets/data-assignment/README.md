# Assignment from a JSON file

**Problem:** assign each worker a different task, minimise the total cost; the cost matrix is read from `data.json`.
**Shows:** `lib(json)` (`json_read/3` with `names_as_atoms` returns an object as `{[key:Value, ...]}`), `argv(all, L)` for the file path, `element/3`, `bb_min/3`, `printf/2`.
**Run:** `eclipse.exe -f model.ecl -e main` (`eclipse.exe` must be on PATH, or call it by its full path). Another file: `eclipse.exe -f model.ecl -e main -- other.json`
**Expected:** `total 13, task [2, 1, 3, 4]`
**Time:** about 0.3 s wall, start-up included.
