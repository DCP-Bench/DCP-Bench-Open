from cpmpy import *
import json

# Decision variables
# Permutation of the 8 devices (A to H) in the rack
# Represented as indices 0 to 7 for simplicity
order = intvar(0, 7, shape=8, name="order")

# Ensure all devices are placed exactly once (permutation constraint)
model = Model([
    AllDifferent(order)
])

# Define the number of cables between each pair of devices
# We'll use a dictionary to store the number of cables between each pair
cable_connections = {
    ('A', 'H'): 1,
    ('A', 'E'): 2,
    ('B', 'F'): 4,
    ('C', 'G'): 1,
    ('C', 'D'): 1,
    ('C', 'E'): 1,
    ('D', 'H'): 3,
    ('G', 'H'): 1
}

# Map device names to indices (A=0, B=1, ..., H=7)
device_to_index = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}

# Calculate the total cable length
total_cable_length = 0
for (dev1, dev2), num_cables in cable_connections.items():
    idx1 = device_to_index[dev1]
    idx2 = device_to_index[dev2]
    # Get the positions of the two devices in the rack
    pos1 = order[idx1]
    pos2 = order[idx2]
    # Add the cable length (distance between positions) multiplied by the number of cables
    total_cable_length += num_cables * abs(pos1 - pos2)

# Objective: minimize the total cable length
model.minimize(total_cable_length)

# Solve the model
model.solve()

# Print the solution
solution = {"final_sum": total_cable_length.value()}
print(json.dumps(solution))