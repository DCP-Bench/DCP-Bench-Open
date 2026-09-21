# One candy per child at least, more than a lower-rated neighbour, fewest overall.
from dcp_pb import Pb


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)

    pb = Pb()
    x = pb.ints(n, 1, n)
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            pb.ge([(1, x[i - 1]), (-1, x[i])], 1)
        elif ratings[i - 1] < ratings[i]:
            pb.le([(1, x[i - 1]), (-1, x[i])], -1)

    z = pb.int(n, n * n)
    pb.eq([(1, v) for v in x] + [(-1, z)], 0)
    pb.ge([(1, z)], n)
    pb.minimise([(1, z)])
    return pb, {"x": x, "z": z}
