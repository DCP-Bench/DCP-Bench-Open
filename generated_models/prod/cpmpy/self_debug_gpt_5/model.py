
import cpmpy as cp
import json
from math import gcd
from functools import reduce

# Data (optional)
input_data = {
    "a": [3, 1, 2],
    "c": [5, 10, 8],
    "u": [4, 6, 3],
    "b": 4
}
# End of data

# Helper to compute LCM of a list
def lcm(x, y):
    return x * y // gcd(x, y)

def lcm_list(lst):
    return reduce(lcm, lst, 1)

a = input_data["a"]
c = input_data["c"]
u = input_data["u"]
b = input_data["b"]

n = len(a)

# Model definition
model = cp.Model()

# Decision Variables: x[j] in [0, u[j]]
x = [cp.intvar(0, u[j], name=f"x_{j}") for j in range(n)]

# Scale constraint to avoid fractions: sum((1/a[j]) * x[j]) <= b
# Multiply by L = lcm(a): sum((L/a[j]) * x[j]) <= b * L
L = lcm_list(a)
weights = [L // a[j] for j in range(n)]

# Constraints
model += (cp.sum([weights[j] * x[j] for j in range(n)]) <= b * L)

# Objective: maximize total profit sum(c[j] * x[j])
model.maximize(cp.sum([c[j] * x[j] for j in range(n)]))

# Solve and print
if model.solve():
    solution = {
        'x': [int(xj.value()) for xj in x],
        'total_profit': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
