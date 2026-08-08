
import cpmpy as cp
import json

# Data
demands = [4, 8, 10, 7, 12, 4]  # Demand for buses in each 4-hour time slot
# End of data

# Model definition
model = cp.Model()

# Decision variables
# b[s] = number of buses starting at slot s, for s = 0..4 (each works 2 consecutive slots)
b = cp.intvar(0, max(demands), shape=5, name='b')

# x[i] = number of buses operating in slot i, for i = 0..5
x = cp.intvar(0, sum(demands), shape=6, name='x')

# Constraints
# Link x to b: each bus starting at s covers slots s and s+1
model += [
    x[0] == b[0],           # slot 0 covered only by b[0]
    x[5] == b[4]            # slot 5 covered only by b[4]
]
for i in range(1, 5):
    model += x[i] == b[i-1] + b[i]

# Meet demand in each slot
for i in range(6):
    model += x[i] >= demands[i]

# Objective: minimize total number of buses (counted by their start times)
model.minimize(cp.sum(b))

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
