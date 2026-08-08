from ortools.sat.python import cp_model
import json

# Devices and their connections with cable counts
devices = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
device_indices = {d: i for i, d in enumerate(devices)}

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

# Model definition
model = cp_model.CpModel()

# Decision variables: position of each device in the rack (1 to 8)
positions = [model.NewIntVar(1, 8, f'pos_{d}') for d in devices]

# All devices must have different positions
model.AddAllDifferent(positions)

# Auxiliary variables for absolute distances between connected devices
abs_distances = []
for (d1, d2, cables) in connections:
    idx1 = device_indices[d1]
    idx2 = device_indices[d2]
    diff = model.NewIntVar(-7, 7, f'diff_{d1}_{d2}')
    model.Add(diff == positions[idx1] - positions[idx2])
    abs_diff = model.NewIntVar(0, 7, f'abs_diff_{d1}_{d2}')
    model.AddAbsEquality(abs_diff, diff)
    # Weighted by number of cables
    weighted_dist = model.NewIntVar(0, 7 * cables, f'weighted_dist_{d1}_{d2}')
    model.AddMultiplicationEquality(weighted_dist, [abs_diff, cables])
    abs_distances.append(weighted_dist)

# Objective: minimize sum of weighted cable lengths
model.Minimize(sum(abs_distances))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    final_sum = solver.ObjectiveValue()
    solution = {
        'final_sum': int(final_sum)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")