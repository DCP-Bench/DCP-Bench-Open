# Project selection from a JSON file (maximise)

**Problem:** choose projects from `data.json` within the budget, at most one project from each group (groups have different sizes), maximising the profit.
**Shows:** reading `args[0]` (default `data.json`) with Gson (`JsonParser`), every size taken from the data, ragged `groups`, unused keys ignored, `makeBoolVarArray`, `mul` views, `sum`, `maximize`, the proof check `isCompleted()`, and the values read inside `onSolution`.
**Run:** `java ProjectSelection.java data.json`
**Expected:** `Best value: 16`
**Expected:** `Items: tent lamp`
**Expected:** `Proven optimal: true`
