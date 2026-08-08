
import cpmpy as cp
import json

# Data
costs = [5000, 7000, 4000, 3000]
npv = [16000, 22000, 12000, 8000]
budget = 14000
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.boolvar(shape=4, name="x")  # x[i] = 1 if investment i+1 is chosen

# Constraints
model += cp.sum(costs[i] * x[i] for i in range(4)) <= budget

# Objective
model.maximize(cp.sum(npv[i] * x[i] for i in range(4)))

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
