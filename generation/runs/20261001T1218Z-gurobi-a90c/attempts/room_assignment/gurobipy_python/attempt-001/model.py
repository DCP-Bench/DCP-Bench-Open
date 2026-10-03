"""Room assignment: give every request one room for its whole stay, so that no room serves two requests on the same day."""
from datetime import date, timedelta

import gurobipy as gp
from gurobipy import GRB


def build(instance):
    max_rooms = instance["max_rooms"]
    starts = [date.fromisoformat(s) for s in instance["start_data"]]
    ends = [date.fromisoformat(e) for e in instance["end_data"]]
    preassigned = instance["preassigned_room_data"]
    requests = range(len(starts))
    rooms = range(max_rooms)

    model = gp.Model("room_assignment")

    # in_room[i, r] is 1 when request i is assigned room r.
    in_room = model.addVars(requests, rooms, vtype=GRB.BINARY, name="in_room")
    room_of = [gp.quicksum(r * in_room[i, r] for r in rooms) for i in requests]

    # Every request gets exactly one room, the same for its entire period.
    for i in requests:
        model.addConstr(in_room.sum(i, "*") == 1, name=f"one_room[{i}]")

    # Some requests already have a room pre-assigned (-1 means none).
    for i in requests:
        if preassigned[i] != -1:
            model.addConstr(room_of[i] == preassigned[i], name=f"preassigned[{i}]")

    # A room serves one request at a time: a request occupies its room on every day
    # from its start up to, not including, its end day.
    day = min(starts)
    while day <= max(ends):
        present = [i for i in requests if starts[i] <= day < ends[i]]
        if len(present) > 1:
            for r in rooms:
                model.addConstr(gp.quicksum(in_room[i, r] for i in present) <= 1,
                                name=f"one_per_room[{day},{r}]")
        day += timedelta(days=1)

    return model, {"room_assignments": room_of}
