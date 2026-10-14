# Appointment scheduling: give each of n people one of n interview slots, one person per slot,
# so that every person is assigned a slot in which they are free.
from exact import Exact


def build(instance):
    free = instance["m"]  # free[i][j] = 1 when person i is free in slot j
    n = len(free)  # as many slots as people

    solver = Exact()

    # x[i][j] = 1 when person i is assigned to slot j
    x = [[f"x_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(x[i][j], 0, 1)

    for i in range(n):
        # the slot a person is given must be one in which they are free
        free_slots = [(free[i][j], x[i][j]) for j in range(n) if free[i][j]]
        solver.addConstraint(free_slots, True, 1, True, 1)
        # each person gets exactly one slot
        solver.addConstraint([(1, x[i][j]) for j in range(n)], True, 1, True, 1)
        # each slot is given to exactly one person
        solver.addConstraint([(1, x[j][i]) for j in range(n)], True, 1, True, 1)

    return solver, {"x": x}
