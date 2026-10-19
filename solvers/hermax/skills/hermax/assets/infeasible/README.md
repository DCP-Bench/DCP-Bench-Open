# Four tasks, three slots (infeasible)

**Problem:** Give four tasks distinct time slots out of three.
**Shows:** `all_different` on integer variables, reading the status (`unsat`) instead of expecting an exception or empty output.
**Run:** `python3 model.py`
**Expected:** `status: unsat`
**Expected:** `no schedule: the solver proved there is none`
