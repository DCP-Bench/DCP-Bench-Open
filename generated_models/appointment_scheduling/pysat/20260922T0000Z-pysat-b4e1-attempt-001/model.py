# Put each person in a free interview slot, one person per slot.
from dcp_sat import Sat


def build(instance):
    free = instance["m"]
    n = len(free)

    sat = Sat()
    x = sat.bool_grid(n, n)
    for i in range(n):
        # the chosen slot must be one the person is free for
        sat.bool_sum_eq(free[i], x[i], 1)
        sat.exactly(x[i], 1)
        sat.exactly([x[j][i] for j in range(n)], 1)
    return sat, {"x": x}
