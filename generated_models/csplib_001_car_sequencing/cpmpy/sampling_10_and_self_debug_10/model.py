
import cpmpy as cp
import json

# Data
at_most = [1, 2, 2, 2, 1]  # max number of cars with option in per_slots window
per_slots = [2, 3, 3, 5, 5]  # window size for each option
demand = [1, 1, 2, 2, 2, 2]  # demand per car type
requires = [[1, 0, 1, 1, 0],
            [0, 0, 0, 1, 0],
            [0, 1, 0, 0, 1],
            [0, 1, 0, 1, 0],
            [1, 0, 1, 0, 0],
            [1, 1, 0, 0, 0]]  # properties per car type

num_cars = sum(demand)
num_types = len(demand)
num_options = len(at_most)

# Model definition
model = cp.Model()

# Decision Variables
# sequence[i] = car type at position i in the sequence
sequence = cp.intvar(0, num_types - 1, shape=num_cars, name="sequence")

# Constraints

# 1) Demand constraints: each car type appears exactly demand[type] times
for t in range(num_types):
    model += (cp.Count(sequence, t) == demand[t])

# 2) Capacity constraints for each option:
# For each option, in every window of per_slots[option] consecutive cars,
# the number of cars requiring that option <= at_most[option]
for opt in range(num_options):
    window_size = per_slots[opt]
    max_allowed = at_most[opt]
    for start in range(num_cars - window_size + 1):
        # Count how many cars in sequence[start:start+window_size] require option opt
        # We sum over the window: for each position, if the car requires option opt, count 1 else 0
        # We use element constraints to check requires[car_type][opt]
        # We create boolean variables for each position in the window indicating if that car requires option opt
        bool_vars = []
        for pos in range(start, start + window_size):
            # Create boolean variable: 1 if sequence[pos] requires option opt, else 0
            # We can use element constraint: requires[sequence[pos]][opt]
            # But requires is a constant matrix, so we can use cp.Element requires with sequence[pos]
            # However, cp.Element requires index to be intvar, so we do:
            # bool_var = cp.Element(requires_column, sequence[pos])
            # requires_column = [requires[t][opt] for t in range(num_types)]
            requires_column = [requires[t][opt] for t in range(num_types)]
            bool_var = cp.intvar(0, 1)
            model += (bool_var == cp.Element(requires_column, sequence[pos]))
            bool_vars.append(bool_var)
        model += (cp.sum(bool_vars) <= max_allowed)

# Solve and print
if model.solve():
    solution = {'sequence': sequence.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
