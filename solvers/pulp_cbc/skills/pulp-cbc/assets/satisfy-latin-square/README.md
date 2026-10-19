# Latin square by satisfaction

**Problem:** Fill a 4x4 Latin square (each value once per row and column) that matches four clues.
**Shows:** a satisfaction model with no objective, one binary per cell and value, equality constraints for "exactly one", the status check before reading values.
**Run:** `python3 model.py`
**Expected:** `Status: Optimal`
**Expected:** `Valid Latin square matching the clues: True`
