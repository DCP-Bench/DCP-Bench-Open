# Room assignment: put every request (a stay from a start date up to an end date) in one of
# the rooms for its whole duration, so that a room serves only one request at a time. Some
# requests already have a room.
import datetime

import z3


def build(instance):
    max_rooms = instance["max_rooms"]                  # number of rooms available
    starts = [datetime.date.fromisoformat(s) for s in instance["start_data"]]  # ISO dates
    ends = [datetime.date.fromisoformat(e) for e in instance["end_data"]]
    preassigned = instance["preassigned_room_data"]    # room already given, or -1 for none
    n_requests = len(starts)

    # room[i] is the room that request i is assigned to.
    room = [z3.Int(f"room_{i}") for i in range(n_requests)]

    solver = z3.Solver()

    # Every request gets one of the rooms 0..max_rooms-1 for its whole stay.
    for i in range(n_requests):
        solver.add(room[i] >= 0, room[i] <= max_rooms - 1)

    # Some requests already have a room.
    for i in range(n_requests):
        if preassigned[i] != -1:
            solver.add(room[i] == preassigned[i])

    # A room can only serve one request at a time: requests that are active on the same day
    # (start <= day < end) must be in different rooms.
    if n_requests > 0:
        groups = set()
        day = min(starts)
        while day <= max(ends):
            active = tuple(i for i in range(n_requests) if starts[i] <= day < ends[i])
            if len(active) > 1:
                groups.add(active)
            day += datetime.timedelta(days=1)
        for active in sorted(groups):
            solver.add(z3.Distinct([room[i] for i in active]))

    return solver, {"room_assignments": room}
