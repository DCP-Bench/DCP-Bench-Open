"""Curious numbers (Dudeney 114): a number other than 48 such that it plus 1, and its half plus 1, are both squares."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data. Every quantity in the reference lies in
# 1..10000, and 48 is the known example to exclude.
UPPER = 10000
KNOWN = 48


def build(instance):
    model = gp.Model("cur_num")

    # b is the square root of peculiar + 1, and e that of peculiar / 2 + 1; both
    # squares are at most 10000, so the roots are at most 100. root_b[v] = 1
    # when b = v, which makes the squares linear.
    roots = range(1, int(UPPER ** 0.5) + 1)
    root_b = model.addVars(roots, vtype=GRB.BINARY, name="b")
    root_e = model.addVars(roots, vtype=GRB.BINARY, name="e")
    model.addConstr(root_b.sum() == 1, name="one_b")
    model.addConstr(root_e.sum() == 1, name="one_e")

    # If you add 1 to the number, the result is a square number: peculiar = b^2 - 1.
    peculiar = gp.quicksum((v * v - 1) * root_b[v] for v in roots)
    model.addConstr(peculiar >= 1, name="peculiar_at_least_1")

    # Its half c, plus 1, is also a square number: peculiar = 2 c and c + 1 = e^2,
    # with c and c + 1 in 1..10000.
    half = gp.quicksum((v * v - 1) * root_e[v] for v in roots)
    model.addConstr(half >= 1, name="half_at_least_1")
    model.addConstr(peculiar == 2 * half, name="halving")

    # The number is not 48, which is already known: no root makes peculiar 48.
    for v in roots:
        if v * v - 1 == KNOWN:
            model.addConstr(root_b[v] == 0, name="not_48")

    return model, {"peculiar": peculiar}
