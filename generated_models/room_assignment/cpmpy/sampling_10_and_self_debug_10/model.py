
import cpmpy as cp
import json
from datetime import datetime

# Data
max_rooms = 5
start_data = ["2024-05-01", "2024-05-02", "2024-05-03", "2024-05-04"]
end_data = ["2024-05-05", "2024-05-06", "2024-05-07", "2024-05-08"]
preassigned_room_data = [3, -1, -1, -1]

# Convert dates to integers (days since a reference date)
date_format = "%Y-%m-%d"
ref_date = datetime.strptime("2024-01-01", date_format)
start_days = [(datetime.strptime(d, date_format) - ref_date).days for d in start_data]
end_days = [(datetime.strptime(d, date_format) - ref_date).days for d in end_data]

n_requests = len(start_data)

# Model definition
model = cp.Model()

# Decision Variables
# room_assignments[i] in [1..max_rooms]
room_assignments = cp.intvar(1, max_rooms, shape=n_requests, name="room_assignments")

# Constraints
for i in range(n_requests):
    # Pre-assigned room constraint
    if preassigned_room_data[i] != -1:
        model += (room_assignments[i] == preassigned_room_data[i])

# No overlapping requests in the same room
for i in range(n_requests):
    for j in range(i+1, n_requests):
        # Check if requests i and j overlap in time
        # Overlap if not (end_i <= start_j or end_j <= start_i)
        no_overlap = (end_days[i] <= start_days[j]) | (end_days[j] <= start_days[i])
        # If they overlap, they cannot be assigned the same room
        model += no_overlap | (room_assignments[i] != room_assignments[j])

# Solve and print
if model.solve():
    solution = {'room_assignments': room_assignments.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
