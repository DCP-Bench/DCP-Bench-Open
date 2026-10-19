# Camping knapsack from a JSON file (maximise)

**Problem:** pick items from `data.json` within the capacity, always take the required ones, at most one item from each group, maximising the value.
**Shows:** reading `argv[0]` (default `data.json`) with Gson (`JsonParser`), every size taken from the data, ragged `groups`, JSON booleans read as 1 and 0, unused keys ignored, `boolVarArray`, `scalar`, `sum`, maximisation.
**Run:** `java Knapsack.java data.json`
**Expected:** `Best value: 20`
**Expected:** `Items: tent lamp food`
