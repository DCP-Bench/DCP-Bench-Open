# Hanging weights: thirteen weights A-M, each an integer from 1 to 13 and all
# different, hang from a system of bars that has to balance.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    names = "abcdefghijklm"

    pool = IDPool()
    # w[name] = the weight of the object of that name
    w = {name: Integer(name, 1, 13, vpool=pool) for name in names}
    a, b, c, d, e, f, g, h, i, j, k, l, m = (w[name] for name in names)
    engine = IntegerEngine(vars=list(w.values()), vpool=pool)

    # the weights are all different
    engine.add_alldifferent(list(w.values()))

    # Every bar balances: the weights on either side of the pivot, each times its
    # distance from the pivot, are equal, and a bar hanging beneath another counts as
    # one weight equal to its total. The bottom right bar has 5*C = D and the bar
    # above it 3*G = 2*(C+D).
    engine.add_linear(4 * a == b)
    engine.add_linear(5 * c == d)
    engine.add_linear(3 * e == 2 * f)
    engine.add_linear(3 * g == 2 * c + 2 * d)
    engine.add_linear(3 * a + 3 * b + 2 * j == k + 2 * g + 2 * c + 2 * d)
    engine.add_linear(3 * h == 2 * e + 2 * f + 3 * i)
    engine.add_linear(h + i + e + f == l + 4 * m)
    engine.add_linear(4 * l + 4 * m + 4 * h + 4 * i + 4 * e + 4 * f
                      == 3 * j + 3 * k + 3 * g + 3 * a + 3 * b + 3 * c + 3 * d)

    return engine.clausify(), w
