from cpmpy import *
import json

# Parameters
n_pieces = 4  # Number of pieces the weight broke into
max_weight = 40  # Maximum weight that can be measured

# Decision variables
weights = intvar(1, max_weight, shape=n_pieces, name="weights")

# Model
model = Model()

# All weights must be distinct
model += [AllDifferent(weights)]

# The sum of the weights must be 40
model += [sum(weights) == 40]

# For each weight from 1 to 40, it must be possible to measure it using the pieces
# This is done by checking all combinations of placing weights on the left or right side or not using them
for w in range(1, max_weight + 1):
    # Create a variable for the combination of weights that can be used to measure w
    # We use a list of variables to represent the left and right side of the balance
    left = intvar(0, 1, shape=n_pieces)
    right = intvar(0, 1, shape=n_pieces)
    
    # The difference between the left and right side must be equal to w
    model += [sum(left * weights) - sum(right * weights) == w]
    
    # Each weight can be on the left, right, or not used
    for i in range(n_pieces):
        model += [(left[i] == 0) | (left[i] == 1)]
        model += [(right[i] == 0) | (right[i] == 1)]
        model += [left[i] + right[i] <= 1]

# Solve the model
model.solve()

# Sort the weights before outputting
weights_sorted = sorted(weights.value().tolist())

# Print the solution
solution = {"weights": weights_sorted}
print(json.dumps(solution))