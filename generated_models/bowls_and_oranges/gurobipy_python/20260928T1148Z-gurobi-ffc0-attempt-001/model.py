"""Bowls and oranges: put m oranges in distinct bowls 1..n so that no three are evenly spaced."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n, m = instance["n"], instance["m"]
    oranges = range(m)

    model = gp.Model("bowls_and_oranges")

    # x[i] is the bowl of the i-th orange, listed in ascending order; distinct
    # and ascending together mean strictly increasing.
    x = model.addVars(oranges, lb=1, ub=n, vtype=GRB.INTEGER, name="x")
    for i in range(1, m):
        model.addConstr(x[i] >= x[i - 1] + 1, name=f"ascending[{i}]")

    # For oranges A < B < C, the distance from A to B differs from that from B to
    # C, i.e. 2 x[B] - x[A] - x[C] is not 0. gurobipy has no != constraint, so a
    # binary picks which side of zero it lies on, through indicator constraints.
    for a in oranges:
        for b in range(a + 1, m):
            for c in range(b + 1, m):
                gap = 2 * x[b] - x[a] - x[c]
                wider = model.addVar(vtype=GRB.BINARY, name=f"wider[{a},{b},{c}]")
                model.addConstr((wider == 1) >> (gap >= 1), name=f"first_longer[{a},{b},{c}]")
                model.addConstr((wider == 0) >> (gap <= -1), name=f"second_longer[{a},{b},{c}]")

    return model, {"x": [x[i] for i in oranges]}
