# Project selection from a JSON file (maximise)

**Problem:** Choose projects (value, cost) within a budget, never taking two that clash, to maximise the total value. The data is a JSON file given as the first argument (default `data.json`).
**Shows:** reading data with Python's standard `json` module and writing the structure from it (every size from the data); a ragged list turned into a predicate given as its set of true pairs (`{}` when empty); unused keys ignored; `Theory.optimize(term, minimize=False)` then one model.
**Run:** `python model.py data.json`
**Expected:** `Maximum value: 17`
**Expected:** `Projects: [1, 2, 4]`
