
import cpmpy as cp
import json

at_most = [1, 2, 2, 2, 1]
per_slots = [2, 3, 3, 5, 5]
demand = [1, 1, 2, 2, 2, 2]
requires = [
    [1, 0, 1, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 1, 0, 0, 1],
    [0, 1, 0, 1, 0],
    [1, 0, 1, 0, 0],
    [1, 1, 0, 0, 0]
]

total_cars = sum(demand)
sequence = cp.intvar(0, 5, shape=total_cars, name="sequence")

model = cp.Model()

# Ensure each car type is used exactly demand times
for t in range(6):
    model += (cp.Count(sequence, t) == demand[t])

# Add station constraints
for station in range(5):
    window_size = per_slots[station]
    max_count = at_most[station]
    requires_col = [requires[type_idx][station] for type_idx in range(6)]
    num_windows = total_cars - window_size + 1
    for k in range(num_windows):
        window = sequence[k : k + window_size]
        sum_expr = cp.sum([cp.Element(requires_col, var) for var in window])
        model += (sum_expr <= max_count)

if model.solve():
    solution = {'sequence': sequence.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
