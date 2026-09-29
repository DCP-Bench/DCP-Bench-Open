# Hanging weights: thirteen weights A-M, each an integer from 1 to 13 and all
# different, hang from a system of bars that has to balance.
from itertools import product

from hermax.model import Model


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    m = Model()
    # w[name] = the weight of the object of that name
    w = {name: m.int(name, 1, 13) for name in "abcdefghijklm"}
    a, b, c, d, e, f, g, h, i, j, k, l, mm = (w[name] for name in "abcdefghijklm")

    # the weights are all different
    m &= m.vector(list(w.values())).all_different()

    # Every bar balances: the weights on either side of the pivot, each times its
    # distance from the pivot, are equal, and a bar hanging beneath another counts as
    # one weight equal to its total. The bottom right bar has 5*C = D and the bar
    # above it 3*G = 2*(C+D).
    # The balances that involve two or three weights are written as tables of the
    # value combinations that satisfy them, which the solver propagates much better
    # than a sum.
    values = range(1, 14)
    m &= m.vector([a, b]).is_in([(x, y) for x, y in product(values, repeat=2) if 4 * x == y])
    m &= m.vector([c, d]).is_in([(x, y) for x, y in product(values, repeat=2) if 5 * x == y])
    m &= m.vector([e, f]).is_in([(x, y) for x, y in product(values, repeat=2) if 3 * x == 2 * y])
    m &= m.vector([g, c, d]).is_in([(x, y, z) for x, y, z in product(values, repeat=3)
                                    if 3 * x == 2 * y + 2 * z])
    # the balances of the higher bars add up several weights
    m &= (3 * a + 3 * b + 2 * j == k + 2 * g + 2 * c + 2 * d)
    m &= (3 * h == 2 * e + 2 * f + 3 * i)
    m &= (h + i + e + f == l + 4 * mm)
    m &= (4 * l + 4 * mm + 4 * h + 4 * i + 4 * e + 4 * f
          == 3 * j + 3 * k + 3 * g + 3 * a + 3 * b + 3 * c + 3 * d)

    return m, w
