import cpmpy as cp
import numpy as np
import json

# Input data
max_rooms = 5
start_data = ["2024-05-01", "2024-05-02", "2024-05-03", "2024-05-04"]
end_data = ["2024-05-05", "2024-05-06", "2024-05-07", "2024-05-08"]
preassigned_room_data = [3, -1, -1, -1]

# Convert dates to integers for easier processing
def date_to_int(date_str):
    return int(date_str.replace("-", ""))

start_times = [date_to_int(d) for d in start_data]
end_times = [date_to_int(d) for d in end_data]
n_requests = len(start_data)

# Create model
model = cp.Model()

# Decision variables: room assignment for each request
# room_assignments[i] = room number for request i (0-indexed)
room_assignments = cp.intvar(0, max_rooms-1, shape=n_requests, name="room_assignments")

# Constraint 1: Pre-assigned rooms must be respected
for i in range(n_requests):
    if preassigned_room_data[i] != -1:
        model += room_assignments[i] == preassigned_room_data[i]

# Constraint 2: No overlapping requests can be in the same room
# Two requests overlap if one starts before the other ends
for i in range(n_requests):
    for j in range(i+1, n_requests):
        # Check if requests i and j overlap
        overlap = not (end_times[i] <= start_times[j] or end_times[j] <= start_times[i])
        if overlap:
            # If they overlap, they must be in different rooms
            model += room_assignments[i] != room_assignments[j]

# Solve the model
if model.solve():
    solution_values = room_assignments.value()
    
    # Create solution in required format
    solution = {
        "room_assignments": solution_values.tolist()
    }
    
    # Verification
    def verify_solution(sol, start_data, end_data, preassigned_room_data, max_rooms):
        room_assignments = sol["room_assignments"]
        n_requests = len(start_data)
        
        def date_to_int(date_str):
            return int(date_str.replace("-", ""))
        
        start_times = [date_to_int(d) for d in start_data]
        end_times = [date_to_int(d) for d in end_data]
        
        # Structural verification
        if len(room_assignments) != n_requests:
            return False, f"Expected {n_requests} room assignments, got {len(room_assignments)}"
        
        # Logical verification
        for i, room in enumerate(room_assignments):
            if room < 0 or room >= max_rooms:
                return False, f"Request {i} assigned to invalid room {room}"
        
        # Check pre-assigned rooms
        for i in range(n_requests):
            if preassigned_room_data[i] != -1:
                if room_assignments[i] != preassigned_room_data[i]:
                    return False, f"Request {i} should be in room {preassigned_room_data[i]}"
        
        # Check no overlapping requests in same room
        for i in range(n_requests):
            for j in range(i+1, n_requests):
                overlap = not (end_times[i] <= start_times[j] or end_times[j] <= start_times[i])
                if overlap and room_assignments[i] == room_assignments[j]:
                    return False, f"Overlapping requests {i} and {j} both in room {room_assignments[i]}"
        
        return True, "All constraints satisfied"
    
    valid, msg = verify_solution(solution, start_data, end_data, preassigned_room_data, max_rooms)
    assert valid, f"Verification failed: {msg}"
    
    # Output the solution
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))