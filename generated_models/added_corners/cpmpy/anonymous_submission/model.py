# Import libraries
from cpmpy import *
import json

# Decision Variables
positions = intvar(1, 8, shape=8, name="positions")  # Values for each position (4 circles and 4 squares)

# Model
model = Model()

# Constraint: All positions must have distinct values (digits 1-8)
model += AllDifferent(positions)

# Assuming positions 0,2,5,7 are circles and 1,3,4,6 are squares
# Constraint: Each square equals sum of adjacent circles
# Top row: C F C
model += positions[1] == positions[0] + positions[2]
# Middle connections
model += positions[3] == positions[0] + positions[5]  # Vertical connection from top-left
model += positions[4] == positions[2] + positions[7]  # Vertical connection from top-right
# Bottom row: C F C
model += positions[6] == positions[5] + positions[7]

# Solve
model.solve()

# Print solution
solution = {"positions": positions.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script