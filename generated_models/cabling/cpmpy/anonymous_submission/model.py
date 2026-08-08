# Import libraries
from cpmpy import *
import json

# Parameters
devices = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
n_devices = len(devices)
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

# Decision Variables
positions = intvar(1, n_devices, shape=n_devices, name="positions")  # Position of each device in the rack
final_sum = intvar(0, sum(c[2] * (n_devices-1) for c in connections), name="final_sum")  # Sum of all cable lengths

# Model
model = Model()

# Constraint: all devices have unique positions
model += AllDifferent(positions)

# Calculate cable lengths and sum them up
cable_lengths = []
for (dev1, dev2, num_cables) in connections:
    idx1 = devices.index(dev1)
    idx2 = devices.index(dev2)
    # Absolute difference between positions is the cable length
    cable_length = abs(positions[idx1] - positions[idx2])
    cable_lengths.append(cable_length * num_cables)

model += final_sum == sum(cable_lengths)

# Objective: minimize the sum of cable lengths
model.minimize(final_sum)

# Solve
model.solve()

# Print solution
solution = {
    "final_sum": final_sum.value()
}
print(json.dumps(solution))
# End of CPMPy script