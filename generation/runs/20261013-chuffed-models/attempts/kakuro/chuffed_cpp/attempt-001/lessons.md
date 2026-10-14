In the kakuro instance, "blanks" are the black cells (they are 0 in the solution), not the cells to fill; the white cells are exactly the cells of the "problem" runs.
The segments are [sum, [r, c], ...] with 1-based coordinates, so the model indexes a (n+1) x (n+1) array and outputs 0 for cells in no run.
