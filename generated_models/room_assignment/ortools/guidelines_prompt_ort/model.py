
from ortools.sat.python import cp_model
import json
from datetime import datetime

# Input data
max_rooms = 5  # Maximum number of rooms available
start_data = ["2024-05-01", "2024-05-02", "2024-05-03", "2024-05-04"]  # Start dates
end_data = ["2024-05-05", "2024-05-06", "2024-05-07", "2024-05-08"]    # End dates (exclusive)
preassigned_room_data = [3, -1, -1, -1]  # -1 means no pre-assignment

# Convert date strings to ordinal integers for easy comparison
start_ord = [datetime.strptime(d, "%Y-%m-%d").date().toordinal() for d in start_data]
end_ord   = [datetime.strptime(d, "%Y-%m-%d").date().toordinal() for d in end_data]

# Number of requests
num_requests = len(start_data)

# Create the CP model
model = cp_model.CpModel()

# Decision variables: room assignment for each request (1..max_rooms)
room_assignments = [
    model.NewIntVar(1, max_rooms, f"room_{i}") for i in range(num_requests)
]

# Apply pre-assigned rooms
for i, r in enumerate(preassigned_room_data):
    if r != -1:
        model.Add(room_assignments[i] == r)

# Add non-overlap constraints: if two requests overlap, they cannot share the same room
for i in range(num_requests):
    for j in range(i + 1, num_requests):
        # Check if intervals [start_i, end_i) and [start_j, end_j) overlap
        if not (end_ord[i] <= start_ord[j] or end_ord[j] <= start_ord[i]):
            model.Add(room_assignments[i] != room_assignments[j])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'room_assignments': [solver.Value(room_assignments[i]) for i in range(num_requests)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
