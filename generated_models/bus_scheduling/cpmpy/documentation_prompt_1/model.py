
import cpmpy as cp
import json

# Data
demands = [4, 8, 10, 7, 12, 4]  # Demand for buses in each 4-hour time slot
n_slots = len(demands)

# Model definition
model = cp.Model()

# Decision Variables
# Let y[i] be the number of buses starting their 8-hour shift at time slot i
# Since each bus works 8 successive hours = 2 consecutive 4-hour slots,
# a bus starting at slot i covers slot i and slot (i+1) mod n_slots
y = cp.intvar(0, sum(demands), shape=n_slots, name="y")

# Constraints
# For each time slot, the sum of buses covering that slot must be >= demand
# Buses starting at slot i cover slots i and (i+1) mod n_slots
for t in range(n_slots):
    # Buses covering slot t are those starting at t and those starting at (t-1) mod n_slots
    prev = (t - 1) % n_slots
    model += (y[prev] + y[t] >= demands[t])

# Objective: minimize total number of buses scheduled
model.minimize(cp.sum(y))

# Solve and print
if model.solve():
    solution = {'x': y.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
