# Room assignment: assign each request to one of max_rooms rooms. Some requests
# are pre-assigned a room. A room can only serve one request at a time.
# A request occupies the days from its start date up to, not including, its end date.
from datetime import date

import mip


def build(instance):
    starts = [date.fromisoformat(s).toordinal() for s in instance["start_data"]]
    ends = [date.fromisoformat(s).toordinal() for s in instance["end_data"]]
    pre = instance["preassigned_room_data"]
    rooms = instance["max_rooms"]
    n = len(starts)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    x = [[model.add_var(f"x_{i}_{r}", var_type=mip.BINARY) for r in range(rooms)]
         for i in range(n)]
    z = [model.add_var(f"z_{i}", lb=0, ub=rooms - 1, var_type=mip.INTEGER)
         for i in range(n)]

    # Each request is assigned to exactly one room.
    for i in range(n):
        model += mip.xsum(x[i]) == 1

    # Print the room assignment of each request as an integer room number.
    for i in range(n):
        model += z[i] == mip.xsum(r * x[i][r] for r in range(rooms))

    # Some requests are pre-assigned a room.
    for i in range(n):
        if pre[i] >= 0:
            model += x[i][pre[i]] == 1

    # A room can only serve one request at a time, so no two overlapping requests
    # are assigned to the same room.
    for i in range(n):
        for j in range(i + 1, n):
            if starts[i] < ends[j] and starts[j] < ends[i]:
                for r in range(rooms):
                    model += x[i][r] + x[j][r] <= 1

    # A room can only serve one request at a time: on each day, the requests
    # staying that day use different rooms (this strengthens the pairwise rows above).
    if n > 0:
        for d in range(min(starts), max(ends)):
            active = [i for i in range(n) if starts[i] <= d < ends[i]]
            if len(active) > 1:
                for r in range(rooms):
                    model += mip.xsum(x[i][r] for i in active) <= 1

    return model, {"room_assignments": z}
