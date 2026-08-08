
import cpmpy as cp
import json

# Devices and connections
devices = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
n = len(devices)

# Map device to index
index = {d: i for i, d in enumerate(devices)}

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

# Positions in rack: 1 to 8 (1U each)
pos_min = 1
pos_max = 8

model = cp.Model()

# Decision variables: position of each device in the rack (1 to 8)
pos = cp.intvar(pos_min, pos_max, shape=n, name="pos")

# All devices must have distinct positions
model += cp.AllDifferent(pos)

# Calculate cable lengths weighted by number of cables
# Cable length = number of cables * distance between devices (abs difference in positions)
cable_lengths = []
for d1, d2, cables in connections:
    i1 = index[d1]
    i2 = index[d2]
    dist = cp.Abs(pos[i1] - pos[i2])
    cable_lengths.append(cables * dist)

# Objective: minimize sum of all cable lengths
total_length = cp.sum(cable_lengths)
model.minimize(total_length)

# Solve and print
if model.solve():
    solution = {'final_sum': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
