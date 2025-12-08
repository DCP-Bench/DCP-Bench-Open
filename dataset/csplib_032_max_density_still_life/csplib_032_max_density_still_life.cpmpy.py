#!/usr/bin/python3
# Category: csplib
# Source: https://www.csplib.org/Problems/prob032/
# Example model: https://www.csplib.org/Problems/prob032/models/StillLife.py.html

"""
This problem, arising from Conway's Game of Life, seeks to find the most densely
populated stable pattern (a "still life") on an n x n grid. A still life is a
pattern of live and dead cells that does not change from one generation to the next.
The grid is assumed to be surrounded by an infinite expanse of dead cells.

The rules for a pattern to be a still life are:
1. A live cell must have exactly 2 or 3 live neighbors to remain alive.
2. A dead cell must not have exactly 3 live neighbors (otherwise it would become alive).

The goal is to maximize the number of live cells.

Print the stable configuration (grid) as a list of lists of 0/1 integers, representing the n x m active area.
"""

# Data
n = 6  # The number of rows in the active grid.
m = 6  # The number of columns in the active grid.
# End of data

import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# grid[i, j] is 1 if cell (i, j) is alive, 0 otherwise.
grid = cp.boolvar(shape=(n, m), name="grid")

# Constraints
# Define the valid combinations of (neighbor_count, cell_state) for a still life.
still_life_table = []
# Rule for dead cells: neighbor count can be anything except 3.
for i in range(9):
    if i != 3:
        still_life_table.append((i, 0))
# Rule for live cells: neighbor count must be 2 or 3.
still_life_table.append((2, 1))
still_life_table.append((3, 1))

# Apply the still-life rules to every cell in the grid.
for i in range(n):
    for j in range(m):
        # Collect all valid neighbor cells. Off-board neighbors are implicitly dead (0)
        # and do not need to be added to the sum.
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                nx, ny = i + dx, j + dy
                if 0 <= nx < n and 0 <= ny < m:
                    neighbors.append(grid[nx, ny])

        num_neighbors = cp.sum(neighbors)

        # Enforce that the combination of the neighbor count and the cell's own state
        # is a valid still-life configuration.
        model += cp.Table([num_neighbors, grid[i, j]], still_life_table)

# Symmetry Breaking constraints for square boards to reduce search space.
if n == m:
    model += grid[0, 0] >= grid[n-1, m-1]
    model += grid[0, m-1] >= grid[n-1, 0]

# Objective
# Maximize the total number of live cells on the grid.
model.maximize(cp.sum(grid))

# Solve and print
model.solve()
solution = {
    "grid": grid.value().tolist()
}
print(json.dumps(solution))
# End of CPMpy script

# # pretty print
# def pp(grid):
#     for row in grid:
#         print("".join(['#' if cell else '.' for cell in row]))
# pp(grid.value())