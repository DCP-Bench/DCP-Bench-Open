
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# positions in reading order (skipping the empty center):
# [C11, F12, C13, F21, F23, C31, F32, C33]
positions = cp.intvar(1, 8, shape=8, name="positions")

# Indices for convenience
C11, F12, C13, F21, F23, C31, F32, C33 = range(8)

# Constraints
# All digits 1..8 used exactly once
model += cp.AllDifferent(positions)

# Square equals sum of adjoining circles:
# Top middle square equals sum of top-left and top-right circles
model += positions[F12] == positions[C11] + positions[C13]
# Left middle square equals sum of top-left and bottom-left circles
model += positions[F21] == positions[C11] + positions[C31]
# Right middle square equals sum of top-right and bottom-right circles
model += positions[F23] == positions[C13] + positions[C33]
# Bottom middle square equals sum of bottom-left and bottom-right circles
model += positions[F32] == positions[C31] + positions[C33]

# Solve and print
if model.solve():
    solution = {'positions': positions.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
