# Encodings: not-equal, absolute value, element, reification

**Problem:** Small model where each of `!=`, `abs`, `TABLE[index]` and "flag iff x >= 3" is written in linear form.
**Shows:** the big-M pattern for `!=` and disjunctions, the two-sided bounds for `abs` under minimisation, an indicator per index for element, indicator binaries for reification.
**Run:** `python3 model.py`
**Expected:** `Status: Optimal`
**Expected:** `min |a-b| = 1`
**Expected:** `element value = 7 at index 2`
**Expected:** `flag = 1`
