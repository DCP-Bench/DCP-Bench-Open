# Room assignment (cvc5 Python model).
# Each request is assigned one room for its entire duration, from its start date to its
# end date (both days included). Some requests already have a room pre-assigned.
# A room can only serve one request at a time, so no overlapping requests share a room.
# room_assignments: for each request, an integer from 0 to max_rooms - 1.
import datetime

import cvc5.pythonic as cz


def _day(text):
    return datetime.date.fromisoformat(text).toordinal()


def build(instance):
    max_rooms = instance["max_rooms"]
    starts = [_day(s) for s in instance["start_data"]]
    ends = [_day(e) for e in instance["end_data"]]
    preassigned = instance["preassigned_room_data"]
    n = len(starts)

    room = [cz.Int(f"room_{i}") for i in range(n)]
    constraints = []

    # Each request is assigned one room, from 0 to max_rooms - 1.
    for i in range(n):
        constraints.append(room[i] >= 0)
        constraints.append(room[i] <= max_rooms - 1)

    # Some requests have a room pre-assigned.
    for i in range(n):
        if preassigned[i] >= 0:
            constraints.append(room[i] == preassigned[i])

    # A room can only serve one request at a time, meaning no overlapping requests
    # can be assigned to the same room.
    for i in range(n):
        for j in range(i + 1, n):
            if starts[i] < ends[j] and starts[j] < ends[i]:
                constraints.append(room[i] != room[j])

    return constraints, {"room_assignments": room}
