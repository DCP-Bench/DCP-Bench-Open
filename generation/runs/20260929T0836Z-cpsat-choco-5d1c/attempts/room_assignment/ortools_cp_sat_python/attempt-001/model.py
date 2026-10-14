# Room assignment: give every booking (a request for a room from a start date
# up to, but not including, an end date) one of the rooms for its whole stay,
# so that no room hosts two bookings on the same night. Some bookings already
# have their room fixed.
from datetime import date

from ortools.sat.python import cp_model


def build(instance):
    n_rooms = instance["max_rooms"]
    starts = [date.fromisoformat(d) for d in instance["start_data"]]
    ends = [date.fromisoformat(d) for d in instance["end_data"]]
    preassigned = instance["preassigned_room_data"]  # -1 when the room is not fixed
    n = len(starts)

    model = cp_model.CpModel()

    # room_assignments[i] = the room given to booking i
    room_assignments = [model.new_int_var(0, n_rooms - 1, f"room_{i}") for i in range(n)]

    # bookings whose room is already fixed
    for i in range(n):
        if preassigned[i] != -1:
            model.add(room_assignments[i] == preassigned[i])

    # a room serves one booking at a time: two bookings that share a night,
    # that is, that both cover some day d with start <= d < end, need different rooms
    for i in range(n):
        for j in range(i + 1, n):
            if max(starts[i], starts[j]) < min(ends[i], ends[j]):
                model.add(room_assignments[i] != room_assignments[j])

    return model, {"room_assignments": room_assignments}
