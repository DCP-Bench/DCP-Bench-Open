# JSON input (knapsack)

**Problem:** Choose items with weights [2, 3, 4, 5] and values [3, 4, 5, 6] within capacity 5, maximising value. The data is in `instance.json`.
**Shows:** `using JSON` and `JSON.parsefile`, converting JSON numbers with `Int.`, a path argument with a default, printing a result by hand, a failure message on stderr and exit 1 when the optimum is not proven.
**Run:** `julia model.jl`
**Expected:** `Status: OPTIMAL`
**Expected:** `Value: 7`
**Expected:** `Take: [1, 1, 0, 0]`
