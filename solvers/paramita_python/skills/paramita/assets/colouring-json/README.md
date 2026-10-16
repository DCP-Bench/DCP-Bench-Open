# Graph colouring from a JSON file (minimise)

**Problem:** colour a 5-node graph (a triangle with a tail) with the fewest colours. The edges come as cliques of varying length (a ragged list). Reads `data.json` by default, or the path given as the first argument.
**Shows:** reading an instance file with `json`, deriving the edges from a ragged list, one-hot colours, minimise by maximising the negated objective, the `constant + benefit()` arithmetic, ignoring extra keys.
**Run:** `python3 model.py`
**Expected:** `Colours: 3`
