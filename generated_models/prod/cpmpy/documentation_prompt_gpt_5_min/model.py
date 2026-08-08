
import cpmpy as cp
import json
import math

# Data
input_data = {
    "a": [3, 1, 2],
    "c": [5, 10, 8],
    "u": [4, 6, 3],
    "b": 4
}
a = input_data["a"]
c = input_data["c"]
u = input_data["u"]
b = input_data["b"]
# End of data

# Model definition
model = cp.Model()

# Problem size
n = len(a)

# Decision Variables: x[j] between 0 and u[j]
# Use a common upper bound and add per-variable upper bound constraints
x = cp.intvar(0, max(u), shape=n, name="x")

# Constraints
# To avoid fractional coefficients, multiply the constraint by lcm of a's
l = math.lcm(*a)
coeffs = [l // aj for aj in a]  # integer coefficients

# sum((1/a[j]) * x[j]) <= b  <=>  sum((l/a[j]) * x[j]) <= b * l
model += cp.sum([coeffs[j] * x[j] for j in range(n)]) <= b * l

# upper bounds per variable
for j in range(n):
    model += x[j] <= u[j]

# Objective: maximize total profit sum(c[j] * x[j])
model.maximize(cp.sum([c[j] * x[j] for j in range(n)]))

# Solve and print
if model.solve():
    solution = {
        "x": x.value().tolist(),
        "total_profit": int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
