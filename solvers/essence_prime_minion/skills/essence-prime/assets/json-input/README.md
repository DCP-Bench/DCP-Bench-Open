# Wish-list assignment from JSON (maximise, ragged data)

**Problem:** five people each list the slots they accept (lists of different lengths); give everyone one slot from their list within the slot capacities, maximising the number who get their first wish.
**Shows:** Essence' has no JSON reader, so a small Python driver (standard-library `json`, nothing to install) reads the file given as the first argument (default `data.json`), takes every size from the data, pads the ragged `wishes` with 0 plus a `wishes_len` row-length matrix, ignores keys it does not use (`name`, `note`), writes a `.param` file in a temporary directory, runs `savilerow ... -solutions-to-stdout`, checks the info file and parses the `letting ... be ...` lines. The model reads a padded row only up to its length and indexes a parameter matrix with a decision variable (`wishes[p, choice[p]]`); `atmost(X, Counts, Vals)` caps each slot.
**Run:** `python3 solve.py data.json`
**Expected:** `first wishes granted: 3`
