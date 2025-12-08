#!/usr/bin/python3
# Category: csplib
# Source description: https://www.csplib.org/Problems/prob014/

"""
The Battleships puzzle is played on a grid.
The fleet consists of battleships (four grid squares in length), cruisers (three grid squares long), destroyers (two squares long) and submarines (one square each).
The ships may be oriented horizontally or vertically, and no two ships will occupy adjacent grid squares, not even diagonally.
The digits along the right side of and below the grid indicate the number of grid squares in the corresponding rows and columns that are occupied by vessels.
In some puzzles, one or more `shots` have been taken to start you off. These may show water, a complete submarine, or a part of a longer vessel.
The goal is to find the grid, where each cell is one of: water, submarine, or ship part (left, right, top, bottom, middle).

Print the solution (grid) as a list of lists of integers.
"""

# Data
cols = 10
rows = 10
rowsum = [0, 2, 3, 1, 2, 4, 2, 1, 2, 3]
colsum = [1, 3, 3, 1, 5, 1, 2, 4, 0, 0]
fleet_counts = [[4,1],[3,2],[2,3],[1,4]]  # list of [ship_size, count]

# Our encoding of the grid cells
WATER = 0
_SHIP = 1
CIRCLE = 2  # submarine
LEFT = 3
RIGHT = 4
TOP = 5
BOTTOM = 6
MIDDLE = 7

# Hint (initial state): There is a submarine at row 8, col 2 (1-based). In 0-based, it's (7, 1).
hints = [(7, 1, CIRCLE)]  # (row, col, value)
# End of data

# Import libraries
from cpmpy import *
import json

# parse data
fleet_counts = {size: count for size, count in fleet_counts}

# Decision variables
grid = intvar(0, 7, shape=(rows, cols), name="grid")

# Model
model = Model()

# Hints constraint
for r, c, v in hints:
    model += grid[r, c] == v

# Row and column sums: count any non-water cell as a ship segment.
for i in range(rows):
    model += sum(grid[i, :] > WATER) == rowsum[i]
for j in range(cols):
    model += sum(grid[:, j] > WATER) == colsum[j]

## --- Constraint Block 1: Adjacency and Connectivity ---
for r in range(rows):
    for c in range(cols):
        # Rule 1: No diagonal or corner-touching ships.
        diag_is_water = []
        if r > 0 and c > 0:           diag_is_water.append(grid[r - 1, c - 1] == WATER)
        if r > 0 and c < cols - 1:    diag_is_water.append(grid[r - 1, c + 1] == WATER)
        if r < rows - 1 and c > 0:    diag_is_water.append(grid[r + 1, c - 1] == WATER)
        if r < rows - 1 and c < cols - 1: diag_is_water.append(grid[r + 1, c + 1] == WATER)
        model += (grid[r, c] > WATER).implies(all(diag_is_water))

        # Rule 2: Local piece connectivity
        # For each piece type, define the required state of its neighbors.

        # A CIRCLE must be entirely surrounded by water.
        ortho_is_water = []
        if r > 0:        ortho_is_water.append(grid[r - 1, c] == WATER)
        if r < rows - 1: ortho_is_water.append(grid[r + 1, c] == WATER)
        if c > 0:        ortho_is_water.append(grid[r, c - 1] == WATER)
        if c < cols - 1: ortho_is_water.append(grid[r, c + 1] == WATER)
        model += (grid[r, c] == CIRCLE).implies(all(ortho_is_water))

        # A LEFT piece
        model += (grid[r, c] == LEFT).implies(
            ((grid[r, c + 1] == MIDDLE) | (grid[r, c + 1] == RIGHT) if c < cols - 1 else False) &
            (grid[r, c - 1] == WATER if c > 0 else True) &
            (grid[r - 1, c] == WATER if r > 0 else True) &
            (grid[r + 1, c] == WATER if r < rows - 1 else True)
        )

        # A RIGHT piece
        model += (grid[r, c] == RIGHT).implies(
            ((grid[r, c - 1] == MIDDLE) | (grid[r, c - 1] == LEFT) if c > 0 else False) &
            (grid[r, c + 1] == WATER if c < cols - 1 else True) &
            (grid[r - 1, c] == WATER if r > 0 else True) &
            (grid[r + 1, c] == WATER if r < rows - 1 else True)
        )

        # A TOP piece
        model += (grid[r, c] == TOP).implies(
            ((grid[r + 1, c] == MIDDLE) | (grid[r + 1, c] == BOTTOM) if r < rows - 1 else False) &
            (grid[r - 1, c] == WATER if r > 0 else True) &
            (grid[r, c - 1] == WATER if c > 0 else True) &
            (grid[r, c + 1] == WATER if c < cols - 1 else True)
        )

        # A BOTTOM piece
        model += (grid[r, c] == BOTTOM).implies(
            ((grid[r - 1, c] == MIDDLE) | (grid[r - 1, c] == TOP) if r > 0 else False) &
            (grid[r + 1, c] == WATER if r < rows - 1 else True) &
            (grid[r, c - 1] == WATER if c > 0 else True) &
            (grid[r, c + 1] == WATER if c < cols - 1 else True)
        )

        # A MIDDLE piece must be either horizontal or vertical
        is_hor_middle = (((grid[r, c - 1] == LEFT) | (grid[r, c - 1] == MIDDLE)) &
                         ((grid[r, c + 1] == RIGHT) | (grid[r, c + 1] == MIDDLE)) &
                         (grid[r - 1, c] == WATER if r > 0 else True) &
                         (grid[r + 1, c] == WATER if r < rows - 1 else True)) if 0 < c < cols - 1 else False

        is_ver_middle = (((grid[r - 1, c] == TOP) | (grid[r - 1, c] == MIDDLE)) &
                         ((grid[r + 1, c] == BOTTOM) | (grid[r + 1, c] == MIDDLE)) &
                         (grid[r, c - 1] == WATER if c > 0 else True) &
                         (grid[r, c + 1] == WATER if c < cols - 1 else True)) if 0 < r < rows - 1 else False

        model += (grid[r, c] == MIDDLE).implies(is_hor_middle | is_ver_middle)

## --- Constraint Block 2: Fleet Composition ---
# These constraints ensure we have the correct number of ships of each size.

# 1. Submarines (size 1)
model += sum(grid == CIRCLE) == fleet_counts[1]

# 2. Ship Ends
num_horizontal_ships = sum(grid == LEFT)
num_vertical_ships = sum(grid == TOP)
model += num_horizontal_ships == sum(grid == RIGHT)
model += num_vertical_ships == sum(grid == BOTTOM)

total_long_ships = sum(count for size, count in fleet_counts.items() if size > 1)
model += num_horizontal_ships + num_vertical_ships == total_long_ships

# 3. Middle pieces: for each ship of size n (n>2), there are (n-2) middle pieces.
expected_middles = sum((size - 2) * count for size, count in fleet_counts.items() if size > 2)
model += sum(grid == MIDDLE) == expected_middles

# --- Solve and Print ---
if model.solve():
    solution = {"grid": grid.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")
# End of CPMpy script

# # print pretty board with symbols
# def pretty_print(grid):
#     print("\n--- Solution Board ---")
#     symbols = {
#         WATER: '~', CIRCLE: 'O', LEFT: '<',
#         RIGHT: '>', TOP: '^', BOTTOM: 'v', MIDDLE: '#'
#     }
#     for r in range(rows):
#         print(" ".join(symbols[grid[r, c].value()] for c in range(cols)))
# pretty_print(grid)
# # get all solutions by restricting the grid to be different from previous solutions
# for _s in range(10):  # limit to 10 solutions
#     model += sum(grid != grid.value()) > 0  # at least one cell must differ
#     if model.solve():
#         pretty_print(grid)
#     else:
#         print("No more solutions.")
#         break