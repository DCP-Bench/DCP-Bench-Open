"""Room assignment: give every request one of the available rooms for its whole stay, keeping the
rooms some requests already have, so that no room serves two requests on the same day.

The model reports the room of every request.
"""
from datetime import date, timedelta

from docplex.mp.model import Model


def build(instance):
    max_rooms = instance["max_rooms"]                    # rooms are numbered 0..max_rooms-1
    starts = [date.fromisoformat(s) for s in instance["start_data"]]
    ends = [date.fromisoformat(e) for e in instance["end_data"]]
    preassigned = instance["preassigned_room_data"]      # -1: no room given in advance
    requests = range(len(starts))
    rooms = range(max_rooms)

    model = Model("room_assignment")

    # in_room[i, r] = 1 when request i gets room r; every request gets exactly one room.
    in_room = {(i, r): model.binary_var(name=f"in_room_{i}_{r}") for i in requests for r in rooms}
    for i in requests:
        model.add_constraint(model.sum(in_room[i, r] for r in rooms) == 1)

    # A request with a room assigned in advance keeps that room.
    for i in requests:
        if preassigned[i] != -1:
            if preassigned[i] in rooms:
                model.add_constraint(in_room[i, preassigned[i]] == 1)
            else:
                model.add_constraint(model.sum(in_room[i, r] for r in rooms) == 0)

    # A room can serve only one request at a time: a request occupies the days from its start
    # up to, not including, its end, and the requests present on the same day get different
    # rooms. Each distinct group of requests sharing a day is posted once.
    groups = set()
    for i in requests:
        day = starts[i]
        while day < ends[i]:
            present = tuple(k for k in requests if starts[k] <= day < ends[k])
            if len(present) > 1:
                groups.add(present)
            day += timedelta(days=1)
    for present in sorted(groups):
        for r in rooms:
            model.add_constraint(model.sum(in_room[k, r] for k in present) <= 1)

    room_assignments = [model.sum(r * in_room[i, r] for r in rooms) for i in requests]
    return model, {"room_assignments": room_assignments}
