# Import libraries
from cpmpy import *
import json

# Parameters
dummy_numbers = [15, 9, 30, 21, 19, 3, 12, 6, 25, 27]  # Numbers on the dummies
target_sum = 50  # Required sum to win the cigar

# Decision Variables
dummies = boolvar(shape=len(dummy_numbers), name="dummies")  # Whether each dummy is knocked over

# Model
model = Model()

# Constraint: Sum of knocked-over dummies must equal target_sum
model += sum(cpm_array(dummy_numbers) * dummies) == target_sum

# Solve
model.solve()

# Convert boolean array to list of boolean values
solution_dummies = [bool(dummies[i].value()) for i in range(len(dummy_numbers))]

# Print solution
solution = {
    "dummies": solution_dummies
}
print(json.dumps(solution))
# End of CPMPy script