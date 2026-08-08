
import cpmpy as cp
import json

# Data
n = 7

problem = [[16, [1, 1], [1, 2]], [24, [1, 5], [1, 6], [1, 7]],
           [17, [2, 1], [2, 2]], [29, [2, 4], [2, 5], [2, 6], [2, 7]],
           [35, [3, 1], [3, 2], [3, 3], [3, 4], [3, 5]], [7, [4, 2], [4, 3]],
           [8, [4, 5], [4, 6]], [16, [5, 3], [5, 4], [5, 5], [5, 6], [5, 7]],
           [21, [6, 1], [6, 2], [6, 3], [6, 4]], [5, [6, 6], [6, 7]],
           [6, [7, 1], [7, 2], [7, 3]], [3, [7, 6], [7, 7]],
           [23, [1, 1], [2, 1], [3, 1]], [30, [1, 2], [2, 2], [3, 2], [4, 2]],
           [27, [1, 5], [2, 5], [3, 5], [4, 5], [5, 5]], [12, [1, 6], [2, 6]],
           [16, [1, 7], [2, 7]], [17, [2, 4], [3, 4]],
           [15, [3, 3], [4, 3], [5, 3], [6, 3], [7, 3]],
           [12, [4, 6], [5, 6], [6, 6], [7, 6]], [7, [5, 4], [6, 4]],
           [7, [5, 7], [6, 7], [7, 7]], [11, [6, 1], [7, 1]],
           [10, [6, 2], [7, 2]]]

blanks = [[1, 3], [1, 4], [2, 3], [3, 6], [3, 7], [4, 1], [4, 4], [4, 7],
          [5, 1], [5, 2], [6, 5], [7, 4], [7, 5]]

# Model definition
model = cp.Model()

# Decision Variables: grid x with 0..9; 0 means blank (black) cell
x = cp.intvar(0, 9, shape=(n, n), name="x")

# Precompute sets of white cells (cells that must contain digits) from segments
white_cells = set()
for seg in problem:
    for coord in seg[1:]:
        r, c = coord
        white_cells.add((r - 1, c - 1))  # convert to 0-based

# Constraints
# 1) blanks are zeros
for (r, c) in blanks:
    model += (x[r - 1, c - 1] == 0)

# 2) cells that are part of any segment must be digits 1..9
for (r, c) in white_cells:
    # If a cell is listed as white (part of a segment), it must be between 1 and 9
    model += (x[r, c] >= 1)
    model += (x[r, c] <= 9)

# 3) For each segment: sum constraint and all-different constraint
for seg in problem:
    sum_val = seg[0]
    coords = seg[1:]
    vars_in_seg = [x[r - 1, c - 1] for (r, c) in coords]
    model += (cp.sum(vars_in_seg) == sum_val)
    # All digits in an entry must be different
    model += cp.AllDifferent(vars_in_seg)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
