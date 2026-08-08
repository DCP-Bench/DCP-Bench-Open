
from ortools.sat.python import cp_model
import json

# Devices and cable requirements: (device1, device2, number_of_cables)
devices = ["A", "B", "C", "D", "E", "F", "G", "H"]
cables = [
    ("A", "H", 1),
    ("A", "E", 2),
    ("B", "F", 4),
    ("C", "G", 1),
    ("C", "D", 1),
    ("C", "E", 1),
    ("D", "H", 3),
    ("G", "H", 1),
]

# Model definition
model = cp_model.CpModel()

# Decision variables: position of each device in the rack (1 to 8)
pos = {}
for d in devices:
    pos[d] = model.NewIntVar(1, len(devices), f"pos_{d}")

# All devices must occupy different positions
model.AddAllDifferent(pos.values())

# Create auxiliary vars for absolute distances and build objective terms
distance_terms = []
for d1, d2, count in cables:
    # Absolute difference variable
    diff = model.NewIntVar(0, len(devices) - 1, f"diff_{d1}_{d2}")
    # Link diff to absolute difference of positions
    model.AddAbsEquality(diff, pos[d1] - pos[d2])
    # Accumulate weighted distance
    distance_terms.append(count * diff)

# Objective: minimize total cable length
model.Minimize(sum(distance_terms))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution as JSON
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        "final_sum": int(solver.ObjectiveValue())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
