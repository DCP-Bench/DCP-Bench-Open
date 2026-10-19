# Graph colouring from a JSON file (data input, minimise)

**Problem:** Colour a graph read from a JSON file (here a wheel, a hub joined to a 5-cycle, plus one isolated vertex) with the fewest colours.
**Shows:** reading data with the standard `json` module from the path given as the first argument (default `data.json`), sizes taken from the data, a ragged adjacency list, extra keys ignored, symmetry breaking over interchangeable colours, and every vertex linked to its colour's `used` binary (`x[v, c] <= used[c]`) so an isolated vertex cannot take an uncounted colour.
**Run:** `python model.py data.json`
**Expected:** `Status: optimal`
**Expected:** `Colours: 4`
