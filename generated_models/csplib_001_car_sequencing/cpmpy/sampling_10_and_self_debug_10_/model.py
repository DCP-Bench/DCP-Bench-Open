
import cpmpy as cp
import json

# Data
at_most = [1, 2, 2, 2, 1]  # The amount of times a property can be present in a group of consecutive timeslots
per_slots = [2, 3, 3, 5, 5]  # The amount of consecutive timeslots (window sizes)
demand = [1, 1, 2, 2, 2, 2]  # The demand per type of car
requires = [[1, 0, 1, 1, 0],
            [0, 0, 0, 1, 0],
            [0, 1, 0, 0, 1],
            [0, 1, 0, 1, 0],
            [1, 0, 1, 0, 0],
            [1, 1, 0, 0, 0]]  # The properties per type of car

# Problem sizes
num_types = len(demand)
num_properties = len(at_most)
n = sum(demand)  # total number of cars / sequence length

# Model definition
model = cp.Model()

# Decision Variables
sequence = cp.intvar(0, num_types - 1, shape=n, name="sequence")

# Constraints

# 1) Respect demand for each car type: exact count of each type in the sequence
for t in range(num_types):
    model += (cp.Count(sequence, t) == demand[t])

# 2) For each property, in every sliding window of length per_slots[prop],
#    at most at_most[prop] cars in that window may require the property.
# We use cp.Element to map sequence positions to whether that car type requires the property.
for p in range(num_properties):
    window = per_slots[p]
    cap = at_most[p]
    # prepare list of requirement flags for this property per car type
    prop_req = [requires[t][p] for t in range(num_types)]
    # for each possible window start
    for start in range(0, n - window + 1):
        exprs = [cp.Element(prop_req, sequence[start + k]) for k in range(window)]
        model += (cp.sum(exprs) <= cap)

# Solve
if model.solve():
    solution = {'sequence': sequence.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
