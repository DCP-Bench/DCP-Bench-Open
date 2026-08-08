# Import libraries
from cpmpy import *
import json
from datetime import datetime

# Parameters
max_rooms = 5  # Maximum number of rooms available
start_data = ["2024-05-01", "2024-05-02", "2024-05-03", "2024-05-04"]  # Start date of the requests
end_data = ["2024-05-05", "2024-05-06", "2024-05-07", "2024-05-08"]  # End date of the requests
preassigned_room_data = [3, -1, -1, -1]  # Room 3 pre-assigned for the first request, -1 for no pre-assignment

# Convert dates to datetime objects for proper comparison
start_dates = [datetime.strptime(date, "%Y-%m-%d") for date in start_data]
end_dates = [datetime.strptime(date, "%Y-%m-%d") for date in end_data]
n_requests = len(start_dates)

# Decision Variables
room_assignments = intvar(0, max_rooms-1, shape=n_requests, name="room_assignments")  # Room assignments for each request

# Model
model = Model()

# Pre-assignment constraints
for i in range(n_requests):
    if preassigned_room_data[i] != -1:
        model += (room_assignments[i] == preassigned_room_data[i])

# No overlapping requests in the same room
for i in range(n_requests):
    for j in range(i+1, n_requests):
        # If two requests are assigned to the same room, they must not overlap
        model += (
            (room_assignments[i] != room_assignments[j]) |
            (end_dates[i] <= start_dates[j]) |
            (end_dates[j] <= start_dates[i])
        )

# Solve
model.solve()

# Print solution
solution = {
    "room_assignments": room_assignments.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script