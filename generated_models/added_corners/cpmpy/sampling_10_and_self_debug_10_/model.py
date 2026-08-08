
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# Positions in reading order (left-to-right, top-to-bottom) skipping the center blank:
# 0: top-left (circle)
# 1: top-center (square)
# 2: top-right (circle)
# 3: middle-left (square)
# 4: middle-right (square)
# 5: bottom-left (circle)
# 6: bottom-center (square)
# 7: bottom-right (circle)
positions = cp.intvar(1, 8, shape=8, name="positions")

# Constraints
model += cp.AllDifferent(positions)

# Circle indices: 0,2,5,7
# Square indices and their adjoining circles:
# top-center (1) = top-left (0) + top-right (2)
model += positions[1] == positions[0] + positions[2]
# middle-left (3) = top-left (0) + bottom-left (5)
model += positions[3] == positions[0] + positions[5]
# middle-right (4) = top-right (2) + bottom-right (7)
model += positions[4] == positions[2] + positions[7]
# bottom-center (6) = bottom-left (5) + bottom-right (7)
model += positions[6] == positions[5] + positions[7]

# Solve and print
if model.solve():
    solution = {'positions': positions.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
