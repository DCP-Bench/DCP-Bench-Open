
import cpmpy as cp
import json

# Devices and connections
devices = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
n = len(devices)

# Map device to index
idx = {d: i for i, d in enumerate(devices)}

# Connections with number of cables
# Format: (device1, device2, cables)
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

# Model definition
model = cp.Model()

# Decision Variables
# pos[i] = position of device i in the rack (1 to 8)
pos = cp.intvar(1, n, shape=n, name="pos")

# All devices must have different positions
model += cp.AllDifferent(pos)

# Calculate cable lengths weighted by number of cables
# length = sum over connections of cables * abs(pos[d1] - pos[d2])
lengths = []
for (d1, d2, cables) in connections:
    i1 = idx[d1]
    i2 = idx[d2]
    diff = cp.abs(pos[i1] - pos[i2])
    lengths.append(cables * diff)

total_length = cp.sum(lengths)

# Objective: minimize total cable length
model.minimize(total_length)

# Solve and print
if model.solve():
    solution = {'final_sum': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
