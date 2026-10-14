"""Climbing stairs: climb n steps in moves of m1 to m2 steps each, padding with zero moves once at the top."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n, m1, m2 = instance["n"], instance["m1"], instance["m2"]
    moves = range(n)  # at most n moves, as when every move is one step

    model = gp.Model("climbing_stairs")

    # steps[i] is the number of steps taken at move i, 0..m2.
    steps = model.addVars(moves, lb=0, ub=m2, vtype=GRB.INTEGER, name="steps")
    # moving[i] is 1 exactly when move i takes at least one step.
    moving = model.addVars(moves, vtype=GRB.BINARY, name="moving")

    # The moves climb the whole stair.
    model.addConstr(steps.sum() == n, name="total")

    for i in moves:
        # A move that is taken covers m1 to m2 steps (and at least one, so that
        # moving[i] is 1 only for a real move); a move not taken covers none.
        model.addConstr(steps[i] >= max(m1, 1) * moving[i], name=f"at_least[{i}]")
        model.addConstr(steps[i] <= m2 * moving[i], name=f"at_most[{i}]")

    # Once a move is zero, every later move is zero too.
    for i in range(1, n):
        model.addConstr(moving[i] <= moving[i - 1], name=f"trailing_zeros[{i}]")

    return model, {"steps": [steps[i] for i in moves]}
