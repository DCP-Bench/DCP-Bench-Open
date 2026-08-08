
import cpmpy as cp
import json

# Data
npv = [16000, 22000, 12000, 8000]
cost = [5000, 7000, 4000, 3000]
budget = 14000
n = len(npv)

# Model definition
model = cp.Model()

# Decision Variables: x[i] = 1 if investment i is chosen, else 0
x = cp.boolvar(shape=n, name="x")

# Constraints
# Total cost of chosen investments must not exceed the budget
model += (cp.sum([x[i]*cost[i] for i in range(n)]) <= budget)

# Objective: maximize total NPV
model.maximize(cp.sum([x[i]*npv[i] for i in range(n)]))

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
