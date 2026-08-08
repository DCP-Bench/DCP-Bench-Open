from cpmpy import *
import json

# Parameters
n_steps = 20  # Total number of steps to climb
allowed_steps = [3, 4, 5]  # Steps that can be taken at a time

# Decision variables
steps = intvar(0, 5, shape=n_steps, name="steps")  # Steps taken at each move

# Model
model = Model()

# The sum of all steps taken must be exactly 20
model += [sum(steps) == n_steps]

# Only allowed steps (3, 4, 5) or 0 can be taken at each move
model += [((steps == 3) | (steps == 4) | (steps == 5) | (steps == 0))]

# After the last move that reaches the top, all subsequent moves must be 0
# Define a binary variable to indicate if a step is non-zero
is_non_zero = boolvar(shape=n_steps, name="is_non_zero")
for i in range(n_steps):
    model += [is_non_zero[i] == (steps[i] > 0)]

# Define the index of the last non-zero step
last_non_zero = intvar(0, n_steps - 1, name="last_non_zero")
for i in range(n_steps):
    model += [last_non_zero >= i * is_non_zero[i]]

# All steps after the last non-zero step must be 0
for i in range(n_steps):
    model += [steps[i] == 0 | i <= last_non_zero]

# Solve the model
model.solve()

# Print the solution
solution = {"steps": steps.value().tolist()}
print(json.dumps(solution))