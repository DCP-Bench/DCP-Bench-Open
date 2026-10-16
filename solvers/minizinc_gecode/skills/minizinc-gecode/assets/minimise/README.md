# Minimum vertex cover (minimise)

**Problem:** the fewest nodes of a 6-node graph touching every edge.
**Shows:** boolean variables over a set of nodes, `\/` on edge endpoints, `bool2int` for the size, a `where` filter in output, `solve minimize`.
**Run:** `minizinc --solver gecode model.mzn`
**Expected:** `size = 3`
