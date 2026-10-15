# Room assignment: each request gets one room for its whole stay, and a room serves one request at a time.
# Dates are read from the instance as ISO strings; a stay ends on its end date, which is exclusive,
# so a request that checks out on the day another checks in does not overlap it.

from datetime import date

from paramita.modelling import Bool


def build(instance):
    max_rooms = instance["max_rooms"]
    starts = [date.fromisoformat(s) for s in instance["start_data"]]
    ends = [date.fromisoformat(e) for e in instance["end_data"]]
    preassigned = instance["preassigned_room_data"]  # -1 when the request has no pre-assigned room
    n = len(starts)

    # One-hot encoding: x[i][r] is true when request i is assigned to room r
    x = [[Bool(f"x_{i}_{r}") for r in range(max_rooms)] for i in range(n)]

    cons = []

    # each request is assigned to exactly one room
    cons += [sum(x[i]) == 1 for i in range(n)]

    # a request with a pre-assigned room stays in that room
    for i in range(n):
        if preassigned[i] >= 0:
            cons.append(x[i][preassigned[i]])

    # a room serves one request at a time: two requests whose stays overlap
    # (start_i < end_j and start_j < end_i) may not share a room
    for i in range(n):
        for j in range(i + 1, n):
            if starts[i] < ends[j] and starts[j] < ends[i]:
                for r in range(max_rooms):
                    cons.append(~(x[i][r] & x[j][r]))

    # the assigned room of each request, as an integer from 0 to max_rooms - 1
    room_assignments = [sum(r * x[i][r] for r in range(max_rooms)) for i in range(n)]

    return cons, {"room_assignments": room_assignments}
