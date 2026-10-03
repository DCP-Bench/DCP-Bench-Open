"""Added corners: place the digits 1..8 on a 3x3 ring of circles (corners) and squares (edges) so that each square is the sum of its two adjoining circles."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: the eight positions and their layout are the
    # puzzle's own, mirrored from the reference.
    #   a b c        corners a, c, f, h are circles,
    #   d   e        b, d, e, g are squares.
    #   f g h
    n = 8
    places = range(n)
    digits = range(1, n + 1)

    model = gp.Model("added_corners")

    # put[p, v] is 1 when position p holds digit v.
    put = model.addVars(places, digits, vtype=GRB.BINARY, name="put")
    positions = [gp.quicksum(v * put[p, v] for v in digits) for p in places]
    a, b, c, d, e, f, g, h = positions

    # Every position holds one digit, and the digits 1..8 are all different.
    for p in places:
        model.addConstr(put.sum(p, "*") == 1, name=f"one_digit[{p}]")
    for v in digits:
        model.addConstr(put.sum("*", v) == 1, name=f"used_once[{v}]")

    # Each square equals the sum of the two circles next to it.
    model.addConstr(b == a + c, name="top")
    model.addConstr(d == a + f, name="left")
    model.addConstr(e == c + h, name="right")
    model.addConstr(g == f + h, name="bottom")

    return model, {"positions": positions}
