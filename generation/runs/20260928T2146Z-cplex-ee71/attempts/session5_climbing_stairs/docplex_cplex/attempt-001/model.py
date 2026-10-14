"""Climbing stairs: climb n steps in moves of m1 to m2 steps each, padding with zero moves once at the top."""
from docplex.mp.model import Model


def build(instance):
    n, m1, m2 = instance["n"], instance["m1"], instance["m2"]
    # At most n moves, as when every move is one step.

    model = Model("climbing_stairs")

    # steps[i] is the number of steps taken at move i, 0..m2.
    steps = model.integer_var_list(n, 0, m2, name="steps")
    # moving[i] is 1 exactly when move i takes at least one step.
    moving = model.binary_var_list(n, name="moving")

    # The moves climb the whole stair.
    model.add_constraint(model.sum(steps) == n, ctname="total")

    for i in range(n):
        # A move that is taken covers m1 to m2 steps (and at least one, so that
        # moving[i] is 1 only for a real move); a move not taken covers none.
        model.add_constraint(steps[i] >= max(m1, 1) * moving[i], ctname=f"at_least_{i}")
        model.add_constraint(steps[i] <= m2 * moving[i], ctname=f"at_most_{i}")

    # Once a move is zero, every later move is zero too.
    for i in range(1, n):
        model.add_constraint(moving[i] <= moving[i - 1], ctname=f"trailing_zeros_{i}")

    return model, {"steps": steps}
