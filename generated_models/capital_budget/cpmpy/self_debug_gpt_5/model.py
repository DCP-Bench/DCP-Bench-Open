
import cpmpy as cp
import json

# Data
values = [16, 22, 12, 8]  # NPV in thousands
weights = [5, 7, 4, 3]    # Cost in thousands
budget = 14               # Available budget in thousands
n = 4

# Model definition
model = cp.Model()

# Decision Variables
x = cp.boolvar(shape=n, name="x")  # 1 if investment i is chosen, else 0

# Constraints
model += cp.sum([weights[i] * x[i] for i in range(n)]) <= budget

# Objective
model.maximize(cp.sum([values[i] * x[i] for i in range(n)]))

# Solve and print
if model.solve():
    solution = {
        'x': list(map(int, x.value().tolist())),
        'z': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
