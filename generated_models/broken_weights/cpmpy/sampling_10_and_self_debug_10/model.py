
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# Four pieces with integer weights, sum to 40
weights = cp.intvar(1, 40, shape=4, name="weights")

# Constraints
# Sum of weights is 40
model += (cp.sum(weights) == 40)

# Sort weights to avoid symmetric solutions (non-decreasing order)
model += cp.Increasing(weights)

# The key constraint: using these four weights on a balance scale,
# we can weigh every integral weight from 1 to 40.
# On a balance scale, weights can be placed on either side.
# For each target weight t in 1..40, there must be a way to assign each piece
# to left pan (-1), right pan (+1), or not used (0), so that sum(piece_weight * assignment) == t

# For each target weight t, define 4 variables for assignments: -1, 0, or 1
assignments = cp.intvar(-1, 1, shape=(40, 4), name="assignments")

for t in range(1, 41):
    # sum of weights * assignments == t
    model += (cp.sum(weights * assignments[t-1]) == t)
    # Each assignment is in {-1,0,1} already by domain

# Solve and print
if model.solve():
    solution = {'weights': weights.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
