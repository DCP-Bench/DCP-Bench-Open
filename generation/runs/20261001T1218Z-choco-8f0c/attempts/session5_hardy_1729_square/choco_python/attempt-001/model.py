# Sums of two squares: find four different numbers a, b, c, d in 1..100 with a^2 + b^2 = c^2 + d^2.
from pychoco.model import Model

# The puzzle has no instance data; the range 1..100 is its statement.
RANGE_MIN, RANGE_MAX = 1, 100


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    x = [model.intvar(RANGE_MIN, RANGE_MAX, name=name) for name in "abcd"]
    # sq[k] = x[k] squared
    sq = [model.intvar(RANGE_MIN ** 2, RANGE_MAX ** 2, name=f"sq_{name}") for name in "abcd"]
    for v, s in zip(x, sq):
        model.square(s, v).post()

    # The sum of the squares of the first two equals that of the other two.
    model.scalar(sq, [1, 1, -1, -1], "=", 0).post()

    # The four numbers are different.
    model.all_different(x).post()

    return model, {name: v for name, v in zip("abcd", x)}
