# Room assignment: give each request one room, from 0 to max_rooms - 1, for its whole
# stay, so that no two overlapping requests share a room; some requests have a pre-assigned room.
from datetime import date

from pyscipopt import Model, quicksum


def build(instance):
    max_rooms = instance["max_rooms"]  # number of rooms, numbered 0 .. max_rooms - 1
    # a request runs from its start date up to its end date; the end date is exclusive,
    # so a request may check in on the day another one checks out
    start = [date.fromisoformat(s) for s in instance["start_data"]]
    end = [date.fromisoformat(e) for e in instance["end_data"]]
    preassigned = instance["preassigned_room_data"]  # -1 means no room is pre-assigned

    num_requests = len(start)

    m = Model()

    # one-hot choice: x[i, r] = 1 if request i is put in room r
    x = {(i, r): m.addVar(name=f"x_{i}_{r}", vtype="B") for i in range(num_requests) for r in range(max_rooms)}

    # each request is assigned to exactly one room
    for i in range(num_requests):
        m.addCons(quicksum(x[i, r] for r in range(max_rooms)) == 1)

    # a pre-assigned request is fixed to its given room
    for i in range(num_requests):
        if preassigned[i] >= 0:
            m.addCons(x[i, preassigned[i]] == 1)

    # a room can serve only one request at a time: two requests whose stays overlap
    # cannot share a room
    for i in range(num_requests):
        for j in range(i + 1, num_requests):
            if start[i] < end[j] and start[j] < end[i]:
                for r in range(max_rooms):
                    m.addCons(x[i, r] + x[j, r] <= 1)

    # the room of each request, numbered from 0
    room_assignments = [quicksum(r * x[i, r] for r in range(max_rooms)) for i in range(num_requests)]

    outputs = {"room_assignments": room_assignments}
    return m, outputs
