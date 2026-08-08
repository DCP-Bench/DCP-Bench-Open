
import cpmpy as cp
import json
import datetime

# Data
max_rooms = 5  # Maximum number of rooms available
start_data = ["2024-05-01", "2024-05-02", "2024-05-03", "2024-05-04"]
end_data = ["2024-05-05", "2024-05-06", "2024-05-07", "2024-05-08"]
preassigned_room_data = [3, -1, -1, -1]
# End of data

# Convert date strings to ordinals for overlap checking
start_ord = [datetime.datetime.strptime(d, "%Y-%m-%d").date().toordinal() for d in start_data]
end_ord   = [datetime.datetime.strptime(d, "%Y-%m-%d").date().toordinal() for d in end_data]

# Model definition
model = cp.Model()

# Decision Variables
# room_assignments[i] is the room assigned to request i (1..max_rooms)
room_assignments = cp.intvar(1, max_rooms, shape=len(start_data), name="room_assignments")

# Constraints

# 1) Pre-assigned rooms
for i, pr in enumerate(preassigned_room_data):
    if pr != -1:
        model += (room_assignments[i] == pr)

# 2) No overlapping requests in the same room
n = len(start_ord)
for i in range(n):
    for j in range(i+1, n):
        # Check if request i and j overlap
        if start_ord[i] < end_ord[j] and start_ord[j] < end_ord[i]:
            model += (room_assignments[i] != room_assignments[j])

# Solve and print
if model.solve():
    solution = {
        'room_assignments': room_assignments.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
