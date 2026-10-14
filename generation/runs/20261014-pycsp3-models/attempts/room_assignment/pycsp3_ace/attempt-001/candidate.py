from datetime import date

from pycsp3 import *

# Assign each request to one of max_rooms rooms, so that each request keeps its
# pre-assigned room when it has one, and no two overlapping requests share a room.
# Requests run from their start date to their end date.

max_rooms = data.max_rooms
starts = [date.fromisoformat(s) for s in data.start_data]
ends = [date.fromisoformat(e) for e in data.end_data]
preassigned = data.preassigned_room_data
n = len(starts)

# room_assignments[i] is the room of request i, counted from 0
room_assignments = VarArray(size=n, dom=range(max_rooms))

satisfy(
    # a request with a pre-assigned room stays in that room
    [room_assignments[i] == preassigned[i] for i in range(n) if preassigned[i] >= 0],

    # a room can serve only one request at a time, so overlapping requests use different rooms
    [room_assignments[i] != room_assignments[j]
     for i in range(n) for j in range(i + 1, n)
     if starts[i] < ends[j] and starts[j] < ends[i]],
)
