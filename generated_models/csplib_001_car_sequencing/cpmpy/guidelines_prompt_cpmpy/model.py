
import cpmpy as cp
import json

# Data
at_most = [1, 2, 2, 2, 1]  # The amount of times a property can be present in a group of consecutive timeslots
per_slots = [2, 3, 3, 5, 5]  # The size of each sliding window for the corresponding property
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

# Derived data
num_types = len(demand)
total_cars = sum(demand)

# Model definition
model = cp.Model()

# Decision Variables
# x[p, t] = 1 if at position p we produce a car of type t
x = cp.boolvar(shape=(total_cars, num_types))

# Constraints

# 1) Each position has exactly one car type
for p in range(total_cars):
    model += cp.sum(x[p, :]) == 1

# 2) Satisfy demand for each car type
for t in range(num_types):
    model += cp.sum(x[:, t]) == demand[t]

# 3) Sliding window constraints for each option
for j in range(len(at_most)):
    window = per_slots[j]
    capacity = at_most[j]
    # Identify which car types require option j
    types_with_option = [t for t in range(num_types) if requires[t][j] == 1]
    # For each sliding window over positions
    for start in range(total_cars - window + 1):
        # Sum of cars in the window requiring this option <= capacity
        model += cp.sum([x[p, t] for p in range(start, start + window) for t in types_with_option]) <= capacity

# Solve and print
if model.solve():
    x_val = x.value().tolist()
    # Reconstruct the sequence: for each position, find the type with value 1
    sequence = [row.index(1) for row in x_val]
    solution = {'sequence': sequence}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
