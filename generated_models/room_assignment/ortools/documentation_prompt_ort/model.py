from ortools.sat.python import cp_model
import json
from datetime import datetime

# Input data
max_rooms = 5  # Maximum number of rooms available
start_data = ["2024-05-01", "2024-05-02", "2024-05-03", "2024-05-04"]  # Start date of the requests
end_data = ["2024-05-05", "2024-05-06", "2024-05-07", "2024-05-08"]  # End date of the requests
preassigned_room_data = [3, -1, -1, -1]  # Room 3 pre-assigned for the first request, -1 for no pre-assignment.

# Convert date strings to integers (days since a reference date)
date_format = "%Y-%m-%d"
ref_date = datetime.strptime("2024-01-01", date_format)
start_days = [(datetime.strptime(d, date_format) - ref_date).days for d in start_data]
end_days = [(datetime.strptime(d, date_format) - ref_date).days for d in end_data]

num_requests = len(start_days)

# Model definition
model = cp_model.CpModel()

# Decision variables: room assignment for each request (1-based room index)
room_assignments = []
for i in range(num_requests):
    if preassigned_room_data[i] != -1:
        # Fixed room assignment
        room_assignments.append(model.NewIntVar(preassigned_room_data[i], preassigned_room_data[i], f'room_{i}'))
    else:
        # Room can be any from 1 to max_rooms
        room_assignments.append(model.NewIntVar(1, max_rooms, f'room_{i}'))

# Constraints
# No overlapping requests can be assigned to the same room
for i in range(num_requests):
    for j in range(i + 1, num_requests):
        # Check if requests i and j overlap in time
        # Overlap if start_i < end_j and start_j < end_i
        if not (end_days[i] <= start_days[j] or end_days[j] <= start_days[i]):
            # If they overlap, they cannot be assigned the same room
            model.Add(room_assignments[i] != room_assignments[j])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'room_assignments': [solver.Value(room_assignments[i]) for i in range(num_requests)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")