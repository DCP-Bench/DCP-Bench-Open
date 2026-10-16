# Impossible roster (infeasible)

**Problem:** Three people may each work 0 to 3 hours; together they must work exactly 10 hours.
**Shows:** that `Theory.expand` reports infeasibility as the single string `"No models."`, not as an exception, while `Theory.optimize` raises `AssertionError("Optimization requires satisfiable specification")`, the same error it raises when z3 gives up.
**Run:** `python model.py`
**Expected:** `expand: 'No models.'`
**Expected:** `status: infeasible`
**Expected:** `optimize: Optimization requires satisfiable specification`
