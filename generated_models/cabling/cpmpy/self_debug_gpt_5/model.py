
import cpmpy as cp
import json

# Data
devices = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
n = len(devices)
idx = {d: i for i, d in enumerate(devices)}

# Connections: (device1, device2, number_of_cables)
connections = [
    ('A', 'H', 1),
    ('A', 'E', 2),
    ('B', 'F', 4),
    ('C', 'G', 1),
    ('C', 'D', 1),
    ('C', 'E', 1),
    ('D', 'H', 3),
    ('G', 'H', 1)
]
edges = [(idx[a], idx[b], w) for (a, b, w) in connections]
# End of data

# Model definition
model = cp.Model()

# Decision Variables: position of each device in rack units 1..n (AllDifferent -> permutation)
pos = cp.intvar(1, n, shape=n, name="pos")

# Constraints
model += cp.AllDifferent(pos)

# Objective: minimize sum of cable lengths (weighted by number of cables)
total_length = cp.sum([w * cp.Abs(pos[i] - pos[j]) for (i, j, w) in edges])
model.minimize(total_length)

# Solve and print
if model.solve():
    solution = {'final_sum': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
