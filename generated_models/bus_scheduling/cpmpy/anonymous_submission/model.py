# Import libraries
from cpmpy import *
import json

# Parameters
demands = [4, 8, 10, 7, 12, 4]  # Demand for buses in each 4-hour time slot
n_slots = len(demands)

# Decision Variables
x = intvar(0, max(demands), shape=n_slots, name="x")  # Number of buses starting in each time slot

# Model
model = Model()

# Constraint: Available buses in each time slot must meet demand
for i in range(n_slots):
    # Buses available in this slot are those starting in this slot and previous slot
    available_buses = x[i] + x[(i-1) % n_slots]
    model += available_buses >= demands[i]

# Objective: minimize the total number of buses used
model.minimize(sum(x))

# Solve
model.solve()

# Print solution
solution = {
    "x": x.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script