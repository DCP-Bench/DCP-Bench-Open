
import cpmpy as cp
import json

# Data
demands = [4, 8, 10, 7, 12, 4]  # Demand for buses in each 4-hour time slot
n = len(demands)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# x[i] = number of buses that start operating at time slot i and therefore cover slots i and i+1 (mod n)
max_buses = sum(demands)
x = cp.intvar(0, max_buses, shape=n, name="x")

# Constraints
# For each time slot j, the available buses are those that started at j and those that started at j-1 (with wrap-around)
for j in range(n):
    model += x[j] + x[(j - 1) % n] >= demands[j]

# Objective: minimize total number of buses scheduled (sum of starts)
model.minimize(cp.sum(x))

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
