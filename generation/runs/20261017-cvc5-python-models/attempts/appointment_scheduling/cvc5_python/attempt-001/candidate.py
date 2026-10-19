# Appointment scheduling: schedule 4 people into 4 interview slots based on their
# free-busy schedules. m[i][j] = 1 means person i is free in slot j.
# Output x[i][j] is True if person i is assigned to slot j.
import cvc5.pythonic as cz


def build(instance):
    m = instance["m"]
    n = len(m)

    x = [[cz.Bool(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    constraints = []

    # Each person is assigned to exactly one slot.
    for i in range(n):
        constraints.append(cz.Sum([cz.If(x[i][j], 1, 0) for j in range(n)]) == 1)

    # Each slot takes exactly one person.
    for j in range(n):
        constraints.append(cz.Sum([cz.If(x[i][j], 1, 0) for i in range(n)]) == 1)

    # A person can only be assigned to a slot in which they are free.
    for i in range(n):
        for j in range(n):
            if m[i][j] == 0:
                constraints.append(cz.Not(x[i][j]))

    return constraints, {"x": x}
