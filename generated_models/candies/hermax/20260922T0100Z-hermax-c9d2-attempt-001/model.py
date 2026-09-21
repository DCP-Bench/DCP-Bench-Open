# One candy per child at least, more than a lower-rated neighbour, fewest overall.
from dcp_maxsat import MaxSat


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)

    sat = MaxSat()
    x = sat.ints(n, 1, n)
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            sat.linear_ge([(1, x[i - 1]), (-1, x[i])], 1)
        elif ratings[i - 1] < ratings[i]:
            sat.linear_le([(1, x[i - 1]), (-1, x[i])], -1)

    z = sat.int(n, n * n)
    sat.link_sum([(1, v) for v in x], z)
    return sat, {"x": x, "z": z}, ("minimize", z)
