# Climbing stairs: climb n steps, each move takes between m1 and m2 steps; list the move sizes, 0 after the top.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    m1 = instance["m1"]
    m2 = instance["m2"]
    # the output has one slot per move; with m1 >= 1 there are at most n moves
    slots = n
    m = Model()

    # move[i] = 1 if move i is taken (before reaching the top), 0 if the climb is already over
    move = [m.addVar(name=f"move_{i}", vtype="B") for i in range(slots)]
    # steps[i] = number of steps in move i, 0 when no move is taken
    steps = [m.addVar(name=f"steps_{i}", vtype="I", lb=0, ub=m2) for i in range(slots)]

    # the moves are taken in a prefix: once the top is reached, no further move is made
    for i in range(slots - 1):
        m.addCons(move[i] >= move[i + 1])

    # a taken move is between m1 and m2 steps, a move not taken is 0 steps
    # (m1 and m2 come from the instance; m1 >= 1 so each taken move climbs at least one step)
    for i in range(slots):
        m.addCons(steps[i] >= m1 * move[i])
        m.addCons(steps[i] <= m2 * move[i])

    # the moves together climb exactly n steps (the top of the stair)
    m.addCons(quicksum(steps) == n)

    return m, {"steps": steps}
