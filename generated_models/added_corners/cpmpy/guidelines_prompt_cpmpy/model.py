
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: a 3x3 grid, center is blank (0), others will take values 1..8
positions = cp.intvar(0, 8, shape=(3, 3), name="positions")

# Center cell is blank
model += (positions[1, 1] == 0)

# All other cells must be between 1 and 8
for (i, j) in [(0,0), (0,1), (0,2),
               (1,0),         (1,2),
               (2,0), (2,1), (2,2)]:
    model += (positions[i, j] >= 1)

# All eight non-blank values must be distinct, and also distinct from 0
model += cp.allDifferent(positions.flatten())

# Sum constraints for each square (mid-edge cells)
# Top edge square equals sum of top-left and top-right circles
model += (positions[0,1] == positions[0,0] + positions[0,2])
# Left edge square equals sum of top-left and bottom-left circles
model += (positions[1,0] == positions[0,0] + positions[2,0])
# Right edge square equals sum of top-right and bottom-right circles
model += (positions[1,2] == positions[0,2] + positions[2,2])
# Bottom edge square equals sum of bottom-left and bottom-right circles
model += (positions[2,1] == positions[2,0] + positions[2,2])

# Solve and print
if model.solve():
    solution = {
        "positions": positions.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
