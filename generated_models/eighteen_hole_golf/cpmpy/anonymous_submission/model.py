# Import libraries
from cpmpy import *
import json

# Parameters
n_holes = 18  # Number of holes in the golf course
total_length = 72  # Total length of the course
possible_lengths = [3, 4, 5]  # Possible lengths for each hole

# Decision Variables
holes = intvar(possible_lengths[0], possible_lengths[-1], shape=n_holes, name="holes")  # Length of each hole

# Model
model = Model()

# Constraint: each hole must be one of the possible lengths
for i in range(n_holes):
    model += sum([holes[i] == l for l in possible_lengths]) == 1

# Constraint: total length must equal 72
model += sum(holes) == total_length

# Solve
model.solve()

# Print solution
solution = {
    "holes": holes.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script