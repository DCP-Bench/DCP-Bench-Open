
import cpmpy as cp
import json

# Data (optional)
demands = [4, 8, 10, 7, 12, 4]  # Demand for buses in each 4-hour time slot
# End of data

# Model definition
model = cp.Model()

# Decision Variables
n = len(demands)
# x[t]: number of buses starting at time slot t (each bus covers two consecutive slots)
x = cp.intvar(0, sum(demands), shape=n, name="x")

# Constraints
# Coverage in each slot t is from buses starting at t and t-1 (wrap-around for cyclic day)
for t in range(n):
    model += (x[t] + x[(t - 1) % n] >= demands[t])

# Objective (optional)
# Minimize total number of buses scheduled
model.minimize(cp.sum(x))

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
