#!/usr/bin/python3
# Category: csplib
# Source: https://www.csplib.org/Problems/prob032/
# Example model: https://www.csplib.org/Problems/prob032/models/StillLife.py.html

"""
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
"""

# Data
n = 6  # The number of rows in the active grid.
m = 6  # The number of columns in the active grid.
# End of data

import cpmpy as cp
import json

model = cp.Model()

grid = cp.boolvar(shape=(n, m), name="grid")

still_life_table = []

# Dead cell: any neighbor count except exactly 3.
for k in range(9):
    if k != 3:
        still_life_table.append((k, 0))

# Live cell: exactly 2 or 3 live neighbors.
still_life_table.append((2, 1))
still_life_table.append((3, 1))

# In-grid still-life rules.
for i in range(n):
    for j in range(m):
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                ni, nj = i + dx, j + dy
                if 0 <= ni < n and 0 <= nj < m:
                    neighbors.append(grid[ni, nj])

        model += cp.Table([cp.sum(neighbors), grid[i, j]], still_life_table)

# Ghost-boundary rules: outside cells are dead and must not be born.
# Top and bottom outside rows.
for j in range(m):
    top_neighbors = [grid[0, jj] for jj in range(max(0, j - 1), min(m, j + 2))]
    bottom_neighbors = [grid[n - 1, jj] for jj in range(max(0, j - 1), min(m, j + 2))]

    model += cp.sum(top_neighbors) != 3
    model += cp.sum(bottom_neighbors) != 3

# Left and right outside columns.
for i in range(n):
    left_neighbors = [grid[ii, 0] for ii in range(max(0, i - 1), min(n, i + 2))]
    right_neighbors = [grid[ii, m - 1] for ii in range(max(0, i - 1), min(n, i + 2))]

    model += cp.sum(left_neighbors) != 3
    model += cp.sum(right_neighbors) != 3

model.maximize(cp.sum(grid))

model.solve()

solution = {
    "grid": grid.value().astype(int).tolist()
}
print(json.dumps(solution))
# End of CPMpy script

# pretty print
# def pp(grid):
#     for row in grid:
#         print("".join(['#' if cell else '.' for cell in row]))
# pp(grid.value())