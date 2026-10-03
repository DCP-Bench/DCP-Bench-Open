# Climbing stairs: climb a stair of n steps in moves of m1 to m2 steps at a time. The
# answer lists the steps taken at each of n moves, with 0 for the moves that come after
# the top has been reached.
from hermax.model import Model


def build(instance):
    n = instance["n"]  # total number of steps in the stair
    m1 = instance["m1"]  # fewest steps in one move
    m2 = instance["m2"]  # most steps in one move

    m = Model()
    # steps[i] = steps taken at move i. At most n moves are needed (one step at a
    # time in the worst case), so there are n variables; each takes 0 or m1..m2.
    steps = m.int_vector("steps", n, 0, m2)

    # the steps taken add up to the whole stair
    m &= (sum(steps[i] for i in range(n)) == n)

    # A move takes 0 steps or at least m1 (m2 is the upper bound of the variable).
    # hermax gives each integer the literals "x >= t", so this reads: at least 1 step
    # means at least m1 steps.
    for i in range(n):
        if m1 > 1:
            if m1 > m2:
                m &= ~(steps[i] >= 1)
            else:
                m &= (~(steps[i] >= 1) | (steps[i] >= m1))

    # Trailing zeros: once a move takes 0 steps, every later move takes 0 steps too.
    # Stated move by move: a move that takes steps is preceded by a move that takes steps.
    for i in range(1, n):
        m &= (~(steps[i] >= 1) | (steps[i - 1] >= 1))

    return m, {"steps": steps}
