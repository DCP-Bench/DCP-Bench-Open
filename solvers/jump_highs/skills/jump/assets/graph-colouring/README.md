# Graph colouring (minimise the colours used)

**Problem:** Colour the 6 nodes of a 5-cycle with a pendant node so that adjacent nodes differ, using as few colours as possible.
**Shows:** a binary x[i, c] per node and colour, one colour per node, a binary per colour marking use, `Min` over the colours used, `mip_rel_gap` 0 for a proven optimum.
**Run:** `julia model.jl`
**Expected:** `Status: OPTIMAL`
**Expected:** `Colours used: 3`
**Expected:** `Proper: true`
