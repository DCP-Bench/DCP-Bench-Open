# Linear encodings: not-equal, absolute value, min/max, products, strict bounds, flags

**Problem:** Seven small models, one per encoding, each printing one answer.
**Shows:** `x != v` with one binary, `abs` by two inequalities under minimisation, `min` and `max` without binaries, `z = p * q` for binaries, `w = b * x` for a binary and an integer, strict inequalities on integers, a flag that is 1 exactly when `x >= 3`.
**Run:** `python model.py`
**Expected:** `x != 5: max x = 4`
**Expected:** `abs: min |a-b| = 1`
**Expected:** `min/max: max min(x,y) = 4 , min max(x,y) = 5`
**Expected:** `product of binaries: z = 1`
**Expected:** `product of binary and integer: w = 7`
**Expected:** `strict: x = 5`
**Expected:** `flag = 1`
