# Room assignment: give every booking (a request for a room from a start date
# up to, but not including, an end date) one of the rooms for its whole stay,
# so that no room hosts two bookings on the same night. Some bookings already
# have their room fixed.
from datetime import date

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n_rooms = instance["max_rooms"]
    starts = [date.fromisoformat(d) for d in instance["start_data"]]
    ends = [date.fromisoformat(d) for d in instance["end_data"]]
    preassigned = instance["preassigned_room_data"]  # -1 when the room is not fixed
    n = len(starts)

    pool = IDPool()
    # room_assignments[i] = the room given to booking i; one literal per room
    room_assignments = [Integer(f"room_{i}", 0, n_rooms - 1, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=room_assignments, vpool=pool)
    cnf = engine.clausify()

    # bookings whose room is already fixed. These and the clauses below are written
    # with the room literals directly, because the linear encoder of PySAT rejects a
    # variable that has a single value, as happens when there is one room.
    for i in range(n):
        if preassigned[i] != -1:
            cnf.append([room_assignments[i].equals(preassigned[i])])

    # a room serves one booking at a time: two bookings that share a night,
    # that is, that both cover some day d with start <= d < end, are not in the same room
    for i in range(n):
        for j in range(i + 1, n):
            if max(starts[i], starts[j]) < min(ends[i], ends[j]):
                for room in range(n_rooms):
                    cnf.append([-room_assignments[i].equals(room), -room_assignments[j].equals(room)])

    return cnf, {"room_assignments": room_assignments}
