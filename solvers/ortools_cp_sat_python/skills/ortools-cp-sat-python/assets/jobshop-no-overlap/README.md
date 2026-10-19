# Job shop (no-overlap)

**Problem:** 3 jobs, each visiting 3 machines in a fixed order, minimise the makespan (brute force over machine orders also gives 11).
**Shows:** one interval variable per operation, `add_no_overlap` per machine (one interval list per machine, built with a dict), job order as precedence, makespan with `add_max_equality`.
**Run:** `python3 model.py`
**Expected:** `OPTIMAL`
**Expected:** `Makespan: 11`
