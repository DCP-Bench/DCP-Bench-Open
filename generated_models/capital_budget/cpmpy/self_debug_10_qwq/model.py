
import cpmpy as cp
import json

# Data
costs = [5000, 7000, 4000, 3000]
npvs = [16000, 22000, 12000, 8000]

# Model definition
model = cp.Model()

# Decision Variables
x = cp.boolvar(shape=4, name="x")  # x[0] to x[3] represent investments 1 to 4

# Constraints
total_cost = cp.sum([costs[i] * x[i] for i in range(4)])
model += (total_cost <= 14000)

# Objective
total_npv = cp.sum([npvs[i] * x[i] for i in range(4)])
model.maximize(total_npv)

# Solve and print
if model.solve():
    # Convert boolean array to 0/1 integers
    solution = {'x': x.value().astype(int).tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
