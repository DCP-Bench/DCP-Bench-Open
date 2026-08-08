
import cpmpy as cp
import json
from datetime import date

# Data
max_rooms = 5  # Maximum number of rooms available
start_data = ["2024-05-01", "2024-05-02", "2024-05-03", "2024-05-04"]  # Start date of the requests
end_data = ["2024-05-05", "2024-05-06", "2024-05-07", "2024-05-08"]  # End date of the requests
preassigned_room_data = [3, -1, -1, -1]  # -1 means no pre-assignment
# End of data

# Convert dates to integer days (ordinal). We treat end dates as exclusive (typical for bookings).
starts = [date.fromisoformat(s).toordinal() for s in start_data]
ends = [date.fromisoformat(e).toordinal() for e in end_data]

n = len(starts)

# Model definition
model = cp.Model()

# Decision Variables
room_assignments = cp.intvar(0, max_rooms - 1, shape=n, name="room_assignments")

# Constraints
# Apply pre-assignments
for i, r in enumerate(preassigned_room_data):
    if r != -1:
        model += (room_assignments[i] == int(r))

# No overlapping requests in the same room.
# Two requests i and j overlap if: starts[i] < ends[j] and starts[j] < ends[i]
for i in range(n):
    for j in range(i + 1, n):
        if (starts[i] < ends[j]) and (starts[j] < ends[i]):
            model += (room_assignments[i] != room_assignments[j])

# Solve and print
if model.solve():
    solution = {'room_assignments': room_assignments.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
