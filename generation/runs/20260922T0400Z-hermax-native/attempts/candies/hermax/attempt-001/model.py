# One candy per child at least, more than a lower-rated neighbour, fewest overall.
from hermax.model import Model


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)

    m = Model()
    x = m.int_vector("x", n, 1, n)
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            m &= (x[i - 1] >= x[i] + 1)
        elif ratings[i - 1] < ratings[i]:
            m &= (x[i - 1] + 1 <= x[i])

    # The brief declares the total as an output, so it needs a variable. Every
    # child takes at least one and at most n, which bounds it to n..n*n.
    z = m.sum_var(list(x), name="z")
    m.obj += z
    return m, {"x": x, "z": z}
