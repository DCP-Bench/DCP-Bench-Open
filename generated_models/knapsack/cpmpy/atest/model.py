from cpmpy import *
import json

# Input data
values = [4, 2, 3, 7, 1]  # Values of the items
weights = [3, 1, 2, 5, 4]  # Weights of the items
capacity = 7  # Capacity of the knapsack

# Decision variables
x = boolvar(shape=len(values), name="x")  # x[i] = 1 if item i is taken, 0 otherwise

# Model
model = Model()

# Objective: maximize the total value
model.maximize(sum(values[i] * x[i] for i in range(len(values))))

# Constraint: total weight must not exceed the capacity
model += [sum(weights[i] * x[i] for i in range(len(weights))) <= capacity]

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))