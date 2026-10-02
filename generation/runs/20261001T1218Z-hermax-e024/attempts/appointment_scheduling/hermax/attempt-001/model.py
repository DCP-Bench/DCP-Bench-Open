# Appointment scheduling: give each of n people one of n interview slots,
# every slot to exactly one person, in a slot where that person is free.
from hermax.model import Model


def build(instance):
    free = instance["m"]  # free[i][j] = 1 if person i is free in slot j
    n = len(free)

    m = Model()
    # x[i][j] = person i is assigned to slot j
    x = m.bool_matrix("x", n, n)

    for i in range(n):
        # each person is assigned exactly one slot ...
        m &= x.row(i).exactly_one()
        # ... and each slot goes to exactly one person
        m &= x.col(i).exactly_one()
        # the slot a person gets is one in which that person is free
        m &= (sum(free[i][j] * x[i][j] for j in range(n)) == 1)

    return m, {"x": x}
