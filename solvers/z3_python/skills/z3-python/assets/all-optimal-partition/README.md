# Two-machine split (all optimal solutions)

**Problem:** Assign jobs of length 3, 1, 4, 2, 2 to two machines so the larger total load is as small as possible; list every such assignment.
**Shows:** `Optimize` with `minimize` and `upper`/`lower` to prove the optimum; pinning the objective with `makespan == best` in a plain `Solver`; enumeration over the Boolean decision variables, where two jobs of equal length stay distinct.
**Run:** `python3 model.py`
**Expected:** `Optimal makespan: 6`
**Expected:** `Optimal assignments: 4`
