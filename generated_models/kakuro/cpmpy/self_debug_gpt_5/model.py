
import cpmpy as cp
import json

# Data (optional)
# size of matrix
n = 7

# segments
#    [sum, [segments]]
# Note: 1-based
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
num_p = len(problem)

# The blanks
# Note: 1-based
blanks = [[1, 3], [1, 4], [2, 3], [3, 6], [3, 7], [4, 1], [4, 4], [4, 7],
          [5, 1], [5, 2], [6, 5], [7, 4], [7, 5]]
num_blanks = len(blanks)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(0, 9, shape=(n, n), name="x")

# Preprocess positions (convert to 0-based indexing)
white_set = set()
for entry in problem:
    # entry format: [sum, [r1,c1], [r2,c2], ...]
    for pos in entry[1:]:
        r, c = pos
        white_set.add((r - 1, c - 1))

blank_set = set((r - 1, c - 1) for r, c in blanks)

# Constraints

# 1) Cells not in any segment are blanks (0), cells in segments are 1..9
for i in range(n):
    for j in range(n):
        if (i, j) in white_set:
            model += (x[i, j] >= 1)
        else:
            model += (x[i, j] == 0)

# 2) Explicit blanks must be 0 (redundant for robustness)
for (i, j) in blank_set:
    model += (x[i, j] == 0)

# 3) For each segment: sum constraint and all-different within [1..9]
for entry in problem:
    sum_req = entry[0]
    vars_in_seg = []
    for pos in entry[1:]:
        r, c = pos
        ri, ci = r - 1, c - 1
        vars_in_seg.append(x[ri, ci])
        # Already ensured >=1 by white_set constraint
    # Sum equals required value
    model += (cp.sum(vars_in_seg) == sum_req)
    # All digits within a segment must be different
    model += cp.AllDifferent(vars_in_seg)

# Objective (optional)
# No objective for Kakuro (satisfaction problem)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
