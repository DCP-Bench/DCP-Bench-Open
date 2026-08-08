
import cpmpy as cp
import json

# Data
demands = [4, 8, 10, 7, 12, 4]  # Demand for buses in each 4-hour time slot
n = len(demands)

# Model definition
model = cp.Model()

# Decision Variables
# x[i] = number of buses starting a shift at interval i (4-hour interval)
x = cp.intvar(0, sum(demands), shape=n, name="x")

# Constraints
# Each bus operates 8 successive hours = 2 consecutive intervals
# The number of buses available at interval i is the sum of buses starting at interval i and at interval i-1 (mod n)
# For interval 0, it includes buses starting at interval 0 and those started at interval n-1 (for circular shift coverage)
for i in range(n):
    # available buses at interval i
    available = x[i] + x[i-1] if i > 0 else x[0] + x[n-1]
    model += (available >= demands[i])

# Objective: minimize total buses used (sum of all x)
model.minimize(cp.sum(x))

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
