# Hanging weights: thirteen weights A-M, each an integer from 1 to 13 and all
# different, hang from a system of bars that has to balance.
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
    m &= (4 * a == b)
    m &= (5 * c == d)
    m &= (3 * e == 2 * f)
    m &= (3 * g == 2 * c + 2 * d)
    m &= (3 * a + 3 * b + 2 * j == k + 2 * g + 2 * c + 2 * d)
    m &= (3 * h == 2 * e + 2 * f + 3 * i)
    m &= (h + i + e + f == l + 4 * mm)

    # The top bar: 4 * (the weights of the left part) = 3 * (the weights of the right
    # part). Both parts are built as sums, and the two sums are tied by a table, since
    # a single equation over all thirteen weights is very slow to build in this solver.
    left = m.sum_var([m.scale(x, 1) for x in (l, mm, h, i, e, f)])
    right = m.sum_var([m.scale(x, 1) for x in (j, k, g, a, b, c, d)])
    m &= m.vector([left, right]).is_in([(x, y) for x in range(0, 100) for y in range(0, 100)
                                        if 4 * x == 3 * y])

    return m, w
