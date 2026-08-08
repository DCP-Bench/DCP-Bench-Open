
import cpmpy as cp
import json
from datetime import datetime

# Data (optional)
max_rooms = 5  # Maximum number of rooms available
start_data = ["2024-05-01", "2024-05-02", "2024-05-03", "2024-05-04"]  # Start date of the requests
end_data = ["2024-05-05", "2024-05-06", "2024-05-07", "2024-05-08"]  # End date of the requests
preassigned_room_data = [3, -1, -1, -1]  # Room 3 pre-assigned for the first request, -1 for no pre-assignment.
# End of data

# Helper: convert ISO date string to integer (days since epoch)
def date_to_int(d):
    return (datetime.strptime(d, "%Y-%m-%d") - datetime(1970, 1, 1)).days

# Process dates into integer intervals [start, end) with end exclusive
starts = [date_to_int(d) for d in start_data]
ends = [date_to_int(d) for d in end_data]
n = len(starts)

# Model definition
model = cp.Model()

# Decision Variables
room_assignments = cp.intvar(0, max_rooms - 1, shape=n, name="room_assignments")

# Constraints

# 1) Respect pre-assignments
for i, r in enumerate(preassigned_room_data):
    if r != -1:
        model += (room_assignments[i] == r)

# 2) No overlap in the same room: if intervals overlap, rooms must be different
# Overlap condition for [s1,e1) and [s2,e2): s1 < e2 and s2 < e1
for i in range(n):
    for j in range(i + 1, n):
        overlap = (starts[i] < ends[j]) and (starts[j] < ends[i])
        if overlap:
            model += (room_assignments[i] != room_assignments[j])

# Solve and print
if model.solve():
    solution = {'room_assignments': room_assignments.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
