
import cpmpy as cp
import json

# Data
npvs = [16000, 22000, 12000, 8000]
costs = [5000, 7000, 4000, 3000]
budget = 14000

# Model definition
model = cp.Model()

# Decision Variables: x[i] = 1 if investment i is chosen, 0 otherwise
x = cp.boolvar(shape=4, name="x")

# Constraints: total cost must not exceed the available budget
model += (cp.sum([x[i] * costs[i] for i in range(4)]) <= budget)

# Objective: maximize total NPV
model.maximize(cp.sum([x[i] * npvs[i] for i in range(4)]))

# Solve and print
if model.solve():
    solution = {'x': [int(val) for val in x.value().tolist()]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
