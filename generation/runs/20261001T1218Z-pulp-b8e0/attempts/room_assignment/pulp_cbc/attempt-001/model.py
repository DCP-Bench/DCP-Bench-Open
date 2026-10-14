"""Room assignment: assign requests (a stay from a start date up to, but not including, an end
date) to a limited number of rooms. A request keeps one room for its whole stay, a room serves
one request at a time, and some requests already have a room pre-assigned.

The model reports the room of every request.
"""
import datetime

import pulp


def build(instance):
    max_rooms = instance["max_rooms"]  # number of rooms, numbered 0..max_rooms-1
    starts = [datetime.date.fromisoformat(d) for d in instance["start_data"]]  # first day
    ends = [datetime.date.fromisoformat(d) for d in instance["end_data"]]  # day of leaving
    preassigned = instance["preassigned_room_data"]  # room of a request, -1 if not decided
    n = len(starts)

    problem = pulp.LpProblem("room_assignment", pulp.LpMinimize)  # satisfaction: no objective

    # in_room[i][k] = 1 if request i stays in room k. A request has exactly one room for its
    # whole stay, and room_assignments reads that room back.
    in_room = pulp.LpVariable.dicts("in_room", (range(n), range(max_rooms)), cat="Binary")
    room_assignments = [pulp.LpVariable(f"room_{i}", 0, max_rooms - 1, cat="Integer")
                        for i in range(n)]
    for i in range(n):
        problem += pulp.lpSum(in_room[i][k] for k in range(max_rooms)) == 1
        problem += room_assignments[i] == pulp.lpSum(k * in_room[i][k] for k in range(max_rooms))

    # some requests already have their room
    for i in range(n):
        if preassigned[i] != -1:
            problem += room_assignments[i] == preassigned[i]

    # A room serves one request at a time: requests that are present on the same day are in
    # different rooms. Looking at the first day of every request is enough: the requests present
    # on any day are also present on the latest first day among them, so no day has a
    # larger group than one of these days.
    for day in sorted(set(starts)):
        present = [i for i in range(n) if starts[i] <= day < ends[i]]
        if len(present) > 1:
            for k in range(max_rooms):
                problem += pulp.lpSum(in_room[i][k] for i in present) <= 1

    return problem, {"room_assignments": room_assignments}
