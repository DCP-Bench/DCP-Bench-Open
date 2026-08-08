"""Room-assignment feasibility problem solved with Google OR-Tools CP-SAT.

The script
1. reads the hard-coded input data provided in the task;
2. converts date strings to integer ordinals so they can be compared;
3. builds a CP-SAT model that contains one IntVar per request – its value is the room number;
4. adds constraints for valid room numbers, fixed pre-assignments, and the rule that two
   requests overlapping in time cannot share the same room;
5. solves the model (feasibility only – first solution is accepted);
6. prints a single JSON object whose key is "room_assignments" and whose value is the list
   of assigned room numbers in request order.

The script is completely self-contained and runnable with a standard OR-Tools installation.
"""

from datetime import datetime
import json
from ortools.sat.python import cp_model

# --------------------------------------------------
# 1. Input data (exactly as given in the statement)
# --------------------------------------------------
max_rooms = 5  # Maximum number of rooms available
start_data = [
    "2024-05-01",
    "2024-05-02",
    "2024-05-03",
    "2024-05-04",
]  # Start date strings (ISO-8601 YYYY-MM-DD)
end_data = [
    "2024-05-05",
    "2024-05-06",
    "2024-05-07",
    "2024-05-08",
]  # Exclusive end date strings
preassigned_room_data = [
    3,   # Request 0 must be in room 3
    -1,  # −1 means no pre-assignment
    -1,
    -1,
]

# --------------------------------------------------
# 2. Helper – convert dates to integer ordinals
# --------------------------------------------------

def iso_to_ordinal(date_str: str) -> int:
    """Return proleptic Gregorian ordinal for an ISO-8601 date string."""
    return datetime.strptime(date_str, "%Y-%m-%d").date().toordinal()

start_ord = [iso_to_ordinal(d) for d in start_data]
end_ord   = [iso_to_ordinal(d) for d in end_data]
num_requests = len(start_ord)

# --------------------------------------------------
# 3. Build CP-SAT model
# --------------------------------------------------
model = cp_model.CpModel()

# Decision variables: room number for each request (1 … max_rooms)
room_vars = [model.NewIntVar(1, max_rooms, f"room_{i}") for i in range(num_requests)]

# Pre-assignment constraints
for i, fixed_room in enumerate(preassigned_room_data):
    if fixed_room > 0:
        model.Add(room_vars[i] == fixed_room)

# Non-overlap in same room: if two requests overlap, their rooms must differ
for i in range(num_requests):
    for j in range(i + 1, num_requests):
        # Intervals [start, end) overlap if both comparisons hold
        if start_ord[i] < end_ord[j] and start_ord[j] < end_ord[i]:
            model.Add(room_vars[i] != room_vars[j])

# --------------------------------------------------
# 4. Solve – pure feasibility (no objective)
# --------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Ensure the variable exists at module level irrespective of status
room_assignments = []
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    room_assignments = [int(solver.Value(v)) for v in room_vars]

# --------------------------------------------------
# 5. Output – JSON with the exact required key
# --------------------------------------------------
print(json.dumps({"room_assignments": room_assignments}))
