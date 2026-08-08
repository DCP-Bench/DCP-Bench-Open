
import cpmpy as cp
import json
import numpy as np

# Data (optional)
at_most = [1, 2, 2, 2, 1]  # The amount of times a property can be present
per_slots = [2, 3, 3, 5, 5]  # The amount of consecutive timeslots
demand = [1, 1, 2, 2, 2, 2]  # The demand per type of car
requires = [
    [1, 0, 1, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 1, 0, 0, 1],
    [0, 1, 0, 1, 0],
    [1, 0, 1, 0, 0],
    [1, 1, 0, 0, 0]
]  # The properties per type of car
# End of data

# Dimensions
num_types = len(demand)
num_options = len(at_most)
horizon = int(np.sum(demand))

# Model definition
model = cp.Model()

# Decision Variables
# x[p, t] = 1 if at position p we place a car of type t
x = cp.boolvar(shape=(horizon, num_types), name="x")
# sequence[p] is the car type at position p
sequence = cp.intvar(0, num_types-1, shape=horizon, name="sequence")

# Constraints

# 1) Each position has exactly one type
for p in range(horizon):
    model += (cp.sum(x[p, :]) == 1)

# 2) Demand satisfaction per type
for t in range(num_types):
    model += (cp.sum(x[:, t]) == demand[t])

# 3) Link sequence variable to x (one-hot -> value)
for p in range(horizon):
    model += (sequence[p] == cp.sum([t * x[p, t] for t in range(num_types)]))

# 4) Capacity constraints for each option using sliding windows
# requires[t][o] = 1 if type t requires option o
for o in range(num_options):
    window = per_slots[o]
    limit = at_most[o]
    for s in range(horizon - window + 1):
        # sum over window positions and all types requiring option o
        window_use = cp.sum([x[p, t] * requires[t][o]
                             for p in range(s, s + window)
                             for t in range(num_types)])
        model += (window_use <= limit)

# Solve and print
if model.solve():
    solution = {'sequence': sequence.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
