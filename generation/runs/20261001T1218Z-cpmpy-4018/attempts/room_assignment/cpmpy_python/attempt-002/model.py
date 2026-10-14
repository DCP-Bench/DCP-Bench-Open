# Room assignment: give each request (a stay from a start date up to, not including, an end
# date) one room for its whole stay, so that no room hosts two requests on the same day.
from datetime import date, timedelta

import cpmpy as cp


def build(instance):
    max_rooms = instance["max_rooms"]
    starts = [date.fromisoformat(d) for d in instance["start_data"]]
    ends = [date.fromisoformat(d) for d in instance["end_data"]]
    preassigned = instance["preassigned_room_data"]  # room already fixed for a request, -1 if none
    n_requests = len(starts)

    # room[i] = the room (0 .. max_rooms - 1) request i stays in
    room = cp.intvar(0, max_rooms - 1, shape=(n_requests,), name="room")

    model = cp.Model()

    # Some requests already have a room.
    for i in range(n_requests):
        if preassigned[i] != -1:
            model += room[i] == preassigned[i]

    # A room serves one request at a time: the requests that occupy a given day (start <= day <
    # end, so the end date itself is free again) must all be in different rooms.
    day = min(starts)
    while day <= max(ends):
        on_this_day = [i for i in range(n_requests) if starts[i] <= day < ends[i]]
        if len(on_this_day) > 1:
            model += cp.AllDifferent([room[i] for i in on_this_day])
        day += timedelta(days=1)

    return model, {"room_assignments": room}
