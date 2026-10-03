# Climbing stairs: climb a stair of n steps taking between m1 and m2 steps at a time.
# Give the number of steps taken at each of n moves, with 0 for the moves that come after
# the top has been reached.
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # total number of steps in the stair
    m1 = instance["m1"]  # fewest steps taken at a time
    m2 = instance["m2"]  # most steps taken at a time

    model = Model()

    # steps[i] = steps taken at move i. In the worst case every move is one step, so
    # there are n moves. A move is either 0 (no move) or between m1 and m2, which is
    # the domain {0} + [m1, m2] (the reference states it as steps >= m1 or steps == 0,
    # and steps <= m2).
    allowed = [0] + list(range(max(m1, 1), m2 + 1))
    steps = [model.intvar(allowed, name=f"steps_{i}") for i in range(n)]

    # the steps taken add up to the total number of steps of the stair
    model.sum(steps, "=", n).post()

    # trailing zeros: once a move takes no steps, all the following moves take none
    # (zero[i] is true when move i takes no steps; zero[i - 1] <= zero[i])
    zero = [model.arithm(steps[i], "=", 0).reify() for i in range(n)]
    for i in range(1, n):
        model.arithm(zero[i - 1], "<=", zero[i]).post()

    return model, {"steps": steps}
