# Climbing stairs: climb a stair of n steps in moves of m1 to m2 steps each. Of the n move slots the
# first ones are real moves and the rest are 0 (no more steps are taken once the top is reached).
from exact import Exact


def build(instance):
    n = instance["n"]  # steps in the stair, and the number of move slots
    m1 = instance["m1"]  # fewest steps in one move
    m2 = instance["m2"]  # most steps in one move

    solver = Exact()

    # steps[i] = number of steps taken at move i, between 0 and m2
    steps = [f"steps_{i}" for i in range(n)]
    # moves[i] = 1 if move i is a real move (takes at least one step)
    moves = [f"move_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(steps[i], 0, m2)
        solver.addVariable(moves[i], 0, 1)

    # the sum of the steps taken equals the number of steps in the stair
    solver.addConstraint([(1, name) for name in steps], True, n, True, n)

    # the steps of a move are between m1 and m2, or 0 when it is not a real move (a real move
    # takes at least 1 step, whatever m1 is)
    smallest = max(m1, 1)
    for i in range(n):
        solver.addConstraint([(1, steps[i]), (-m2, moves[i])], False, 0, True, 0)
        solver.addConstraint([(1, steps[i]), (-smallest, moves[i])], True, 0)

    # trailing zeros: once a move takes no steps, all following moves take no steps
    for i in range(1, n):
        solver.addConstraint([(1, moves[i - 1]), (-1, moves[i])], True, 0)

    return solver, {"steps": steps}
