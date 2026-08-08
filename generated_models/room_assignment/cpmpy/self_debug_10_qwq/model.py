
import cpmpy as cp
import json

# Input data
max_rooms = 5
start_data = ["2024-05-01", "2024-05-02", "2024-05-03", "2024-05-04"]
end_data = ["2024-05-05", "2024-05-06", "2024-05-07", "2024-05-08"]
preassigned_room_data = [3, -1, -1, -1]

# Convert date strings to day numbers
start_days = [int(s.split('-')[2]) for s in start_data]
end_days = [int(e.split('-')[2]) for e in end_data]
n_requests = len(start_days)

# Model definition
model = cp.Model()

# Decision variables: room assignments for each request (1-based)
room_assignments = cp.intvar(1, max_rooms, shape=n_requests, name="room_assignments")

# Preassigned rooms constraints
for i in range(n_requests):
    if preassigned_room_data[i] != -1:
        model += (room_assignments[i] == preassigned_room_data[i])

# Non-overlapping constraints for same room assignments
for i in range(n_requests):
    for j in range(i + 1, n_requests):
        # If assigned to the same room, their intervals must not overlap
        # Implication: (same_room) → (non-overlapping)
        same_room = (room_assignments[i] == room_assignments[j])
        non_overlapping = (end_days[i] <= start_days[j]) | (end_days[j] <= start_days[i])
        model += same_room.implies(non_overlapping)

# Solve and print
if model.solve():
    solution = {'room_assignments': room_assignments.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
