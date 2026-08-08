from cpmpy import *
import json

# Input data
demands = [4, 8, 10, 7, 12, 4]  # Demand for buses in each 4-hour time slot

# Number of time slots (4-hour intervals)
num_slots = len(demands)

# Decision variables
# x[i] is the number of buses scheduled to start at time slot i
x = intvar(0, 100, shape=num_slots, name="x")

# Model
model = Model()

# Each bus works for 8 hours, which is 2 consecutive 4-hour time slots
# For each time slot i, the number of buses available is the sum of buses starting at i and i-1
# Ensure that the number of buses available in each time slot meets the demand
for i in range(num_slots):
    if i == 0:
        model += [x[i] + x[i + 1] >= demands[i]]
    else:
        model += [x[i] + x[i - 1] >= demands[i]]

# Objective: minimize the total number of buses scheduled
model.minimize(sum(x))

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))