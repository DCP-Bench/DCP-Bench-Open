This problem, arising from Conway's Game of Life, seeks to find the most densely
populated stable pattern (a "still life") on an n x m active grid. A still life is a
pattern of live and dead cells that does not change from one generation to the next.
Life is played on an infinite board. Cells outside the n x m active grid are dead and are not printed,
but they are still part of the board.

The rules for a pattern to be a still life are:
1. A live cell must have exactly 2 or 3 live neighbors to remain alive.
2. A dead cell, including any dead cell just outside the active grid, must not have exactly 3 live neighbors (otherwise it would become alive).

The goal is to maximize the number of live cells in the active grid.

Print the stable configuration (grid) as a list of n lists of 0/1 integers, representing the n x m active area,
where 1 represents a live cell and 0 represents a dead cell.
