from cpmpy import *
import json
from datetime import datetime

# Input data
max_rooms = 5  # Maximum number of rooms available
start_data = ["2024-05-01", "2024-05-02", "2024-05-03", "2024-05-04"]  # Start date of the requests
end_data = ["2024-05-05", "2024-05-06", "2024-05-07", "2024-05-08"]  # End date of the requests
preassigned_room_data = [3, -1, -1, -1]  # Room 3 pre-assigned for the first request, -1 for no pre-assignment

# Convert date strings to integers (e.g., YYYYMMDD)
start_int = [int(date.replace('-', '')) for date in start_data]
end_int = [int(date.replace('-', '')) for date in end_data]

# Number of requests
num_requests = len(start_data)

# Decision variables
room_assignments = intvar(1, max_rooms, shape=num_requests, name="room_assignments")

# Model
model = Model()

# Constraint: If a request has a preassigned room, it must be assigned to that room
for i in range(num_requests):
    if preassigned_room_data[i] != -1:
        model += [room_assignments[i] == preassigned_room_data[i]]

# Constraint: No overlapping requests in the same room
for r in range(1, max_rooms + 1):
    for i in range(num_requests):
        for j in range(i + 1, num_requests):
            # Only apply constraint if both are assigned to room r
            model += ((room_assignments[i] != r) | (room_assignments[j] != r) |
                      (end_int[i] <= start_int[j]) |
                      (end_int[j] <= start_int[i]))

# Solve the model
model.solve()

# Print the solution
solution = {"room_assignments": room_assignments.value().tolist()}
print(json.dumps(solution))