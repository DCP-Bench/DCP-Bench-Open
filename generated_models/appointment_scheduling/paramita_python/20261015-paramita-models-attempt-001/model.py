# Appointment scheduling: schedule 4 people into 4 interview slots
# based on their free-busy schedules.
# x[i][j] = 1 if person i is assigned to slot j.
# instance["m"][i][j] = 1 if person i is free in slot j.
from paramita.modelling import Bool


def build(instance):
    m = instance["m"]
    n = len(m)

    x = [[Bool(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    cons = []

    # each person is assigned to exactly one slot
    for i in range(n):
        cons.append(sum(x[i]) == 1)

    # each slot is assigned to exactly one person
    for j in range(n):
        cons.append(sum(x[i][j] for i in range(n)) == 1)

    # a person is only scheduled into a slot they are free in (busy slots are excluded)
    for i in range(n):
        for j in range(n):
            if m[i][j] == 0:
                cons.append(~x[i][j])

    return cons, {"x": x}
