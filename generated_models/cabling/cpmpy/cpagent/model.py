import cpmpy as cp
import json

# Step 1: Deconstruct & Pre-compute
# Problem: 8 devices (A-H) in a rack, minimize total cable length
# Devices: A=0, B=1, C=2, D=3, E=4, F=5, G=6, H=7

# Connections from problem description:
# A <-> H: 1 cable, A <-> E: 2 cables, B <-> F: 4 cables
# C <-> G: 1 cable, C <-> D: 1 cable, C <-> E: 1 cable  
# D <-> H: 3 cables, G <-> H: 1 cable
connections = [
    (0, 7, 1),  # A <-> H, 1 cable
    (0, 4, 2),  # A <-> E, 2 cables  
    (1, 5, 4),  # B <-> F, 4 cables
    (2, 6, 1),  # C <-> G, 1 cable
    (2, 3, 1),  # C <-> D, 1 cable
    (2, 4, 1),  # C <-> E, 1 cable
    (3, 7, 3),  # D <-> H, 3 cables
    (6, 7, 1),  # G <-> H, 1 cable
]

# Step 2: Model with CPMpy
n_devices = 8
model = cp.Model()

# Decision variables: position[i] = rack position (0-7) of device i
positions = cp.intvar(0, n_devices-1, shape=n_devices, name="positions")

# Constraint: All devices in different positions (permutation)
model += cp.AllDifferent(positions)

# Objective: minimize total cable length
total_length = cp.intvar(0, 1000, name="total_length")

# Calculate cable lengths for each connection
cable_lengths = []
for i, (dev1, dev2, num_cables) in enumerate(connections):
    # Distance between positions (absolute value using auxiliary variable)
    dist = cp.intvar(0, n_devices-1, name=f"dist_{i}")
    model += dist >= positions[dev1] - positions[dev2]
    model += dist >= positions[dev2] - positions[dev1]
    
    # Cable length for this connection
    cable_length = num_cables * dist
    cable_lengths.append(cable_length)

# Total length constraint
model += total_length == cp.sum(cable_lengths)

# Symmetry breaking: fix device A at position 0
model += positions[0] == 0

# Step 3: Solve & Verify
model.minimize(total_length)

if model.solve():
    optimal_length = total_length.value()
    
    # Verification
    device_positions = positions.value()
    calculated_total = 0
    for dev1, dev2, num_cables in connections:
        distance = abs(device_positions[dev1] - device_positions[dev2])
        calculated_total += num_cables * distance
    
    assert calculated_total == optimal_length, f"Verification failed: {calculated_total} != {optimal_length}"
    
    # Step 4: Output
    solution = {"final_sum": optimal_length}
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))