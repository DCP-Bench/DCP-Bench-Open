
import cpmpy as cp
import json
import numpy as np

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

num_types = len(demand)
num_cars = sum(demand)
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
# For each option, in every window of size per_slots[o], at most at_most[o] cars require that option
for o in range(num_options):
    window_size = per_slots[o]
    max_cars = at_most[o]
    # For each window of length window_size in the sequence
    for start in range(num_cars - window_size + 1):
        # Count how many cars in sequence[start:start+window_size] require option o
        # We create boolean variables for each position in the window indicating if that car requires option o
        bool_vars = []
        for pos in range(start, start + window_size):
            # Create boolean variable: 1 if sequence[pos] requires option o, else 0
            # requires[car_type][option] is 0 or 1, so we can use element constraint
            # We use cp.Element to get requires[sequence[pos]][o]
            # But cp.Element requires array and index variable, so we create a vector for requires for option o
            # We'll create a vector of requires for option o for all car types
            # Then bool_var = requires_for_option[sequence[pos]]
            # Since requires_for_option is constant, we can use cp.Element
            pass
        # Instead of creating bool_vars, we can sum cp.Element(requires_for_option, sequence[pos]) for pos in window
        requires_for_option = [requires[t][o] for t in range(num_types)]
        sum_option = cp.sum([cp.Element(requires_for_option, sequence[pos]) for pos in range(start, start + window_size)])
        model += (sum_option <= max_cars)

# Solve and print
if model.solve():
    solution = {'sequence': sequence.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
