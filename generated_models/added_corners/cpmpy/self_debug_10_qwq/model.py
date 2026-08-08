
import cpmpy as cp
import json

# Define variables for each position (0 to 7)
positions = cp.intvar(1, 8, shape=8, name="positions")

model = cp.Model()

# Constraints based on the problem's structure
# Each square (positions 1, 3, 4, 6) must equal the sum of its adjacent circles
model += (positions[1] == positions[0] + positions[2])  # Position 2 (index 1) = C1 (0) + C3 (2)
model += (positions[3] == positions[0] + positions[5])  # Position 4 (index 3) = C1 (0) + C6 (5)
model += (positions[4] == positions[2] + positions[7])  # Position 5 (index 4) = C3 (2) + C8 (7)
model += (positions[6] == positions[5] + positions[7])  # Position 7 (index 6) = C6 (5) + C8 (7)

# All positions must have distinct values from 1 to 8
model += (cp.AllDifferent(positions))

# Solve and print the solution
if model.solve():
    solution = {'positions': positions.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
