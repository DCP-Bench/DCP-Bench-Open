# Room assignment: give every booking (a request for a room from a start date
# up to, but not including, an end date) one of the rooms for its whole stay,
# so that no room hosts two bookings on the same night. Some bookings already
# have their room fixed.
from datetime import date

from exact import Exact


def build(instance):
    n_rooms = instance["max_rooms"]
    starts = [date.fromisoformat(d) for d in instance["start_data"]]
    ends = [date.fromisoformat(d) for d in instance["end_data"]]
    preassigned = instance["preassigned_room_data"]  # -1 when the room is not fixed
    n = len(starts)

    solver = Exact()
    # room_assignments[i] = the room given to booking i; in_room[i][r] is 1 when it is room r
    room_assignments = [f"room_{i}" for i in range(n)]
    in_room = [[f"booking_{i}_in_{r}" for r in range(n_rooms)] for i in range(n)]
    for i in range(n):
        solver.addVariable(room_assignments[i], 0, n_rooms - 1)
        for name in in_room[i]:
            solver.addVariable(name, 0, 1)
        solver.addConstraint([(1, name) for name in in_room[i]], True, 1, True, 1)
        solver.addConstraint([(r, in_room[i][r]) for r in range(1, n_rooms)] + [(-1, room_assignments[i])],
                             True, 0, True, 0)

    # bookings whose room is already fixed
    for i in range(n):
        if preassigned[i] != -1:
            solver.addConstraint([(1, in_room[i][preassigned[i]])], True, 1, True, 1)

    # a room serves one booking at a time: two bookings that share a night,
    # that is, that both cover some day d with start <= d < end, need different rooms
    for i in range(n):
        for j in range(i + 1, n):
            if max(starts[i], starts[j]) < min(ends[i], ends[j]):
                for r in range(n_rooms):
                    solver.addConstraint([(1, in_room[i][r]), (1, in_room[j][r])], False, 0, True, 1)

    return solver, {"room_assignments": room_assignments}
