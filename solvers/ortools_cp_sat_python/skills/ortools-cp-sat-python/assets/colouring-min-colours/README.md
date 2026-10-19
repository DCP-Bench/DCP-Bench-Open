# Graph colouring (minimise the number of colours)

**Problem:** colour a 4-node graph (a 4-cycle with one chord) so that adjacent nodes differ, with the fewest colours.
**Shows:** an objective that counts distinct colours through the largest colour index (`add_max_equality` then `minimize`), and why that is exact at the optimum.
**Run:** `python3 model.py`
**Expected:** `OPTIMAL`
**Expected:** `Colours used: 3`
