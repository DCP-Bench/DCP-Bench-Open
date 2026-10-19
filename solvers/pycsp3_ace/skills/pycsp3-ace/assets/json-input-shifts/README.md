# Shift assignment from a JSON file

**Problem:** give each of 4 shifts one worker who is available for it, at most 2 shifts per worker, at minimum total cost; the data is in `data.json`.
**Shows:** reading data with the standard library's `json` from the path in `sys.argv[1]` (default `data.json`), every size taken from the data, a ragged list (`available`), extra keys (`name`, `note`) ignored, `x in set(...)` as a unary table, `Count`, a `Table` of (index, value) pairs in place of indexing a Python list by a variable.
**Run:** `python model.py data.json`
**Expected:** `Objective: 8`
**Expected:** `Workers: [0, 1, 3, 1]`
