"""Broken weights: a weight of total mass m breaks into n pieces so that every mass from 1 to m can be weighed on a balance scale, pieces going on either pan or staying off."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    m = instance["m"]  # total mass of the original weight, and the largest mass to weigh
    n = instance["n"]  # number of pieces
    pieces = range(n)
    targets = range(1, m + 1)

    model = gp.Model("broken_weights")

    # weights[j] is the mass of piece j. Each piece weighs at least 1 and the pieces sum to m,
    # so no piece can weigh more than m - (n - 1): the bound used for every product below.
    top = m - (n - 1)
    weights = model.addVars(pieces, lb=1, ub=top, vtype=GRB.INTEGER, name="weights")
    model.addConstr(weights.sum() == m, name="total_mass")

    # Every mass t from 1 to m can be weighed. Piece j is on the same pan as the mass (+1), on the
    # other pan (-1) or off the scale (0); it contributes sign * weights[j] to the balance, held in
    # load[t, j]. A sign is a three-way choice, and the product of the sign and the
    # weight is posted with one indicator per choice, which is linear.
    for t in targets:
        loads = []
        for j in pieces:
            plus = model.addVar(vtype=GRB.BINARY, name=f"plus[{t},{j}]")
            minus = model.addVar(vtype=GRB.BINARY, name=f"minus[{t},{j}]")
            off = model.addVar(vtype=GRB.BINARY, name=f"off[{t},{j}]")
            load = model.addVar(lb=-top, ub=top, vtype=GRB.INTEGER, name=f"load[{t},{j}]")
            model.addConstr(plus + minus + off == 1, name=f"one_sign[{t},{j}]")
            model.addConstr((plus == 1) >> (load == weights[j]), name=f"plus_load[{t},{j}]")
            model.addConstr((minus == 1) >> (load == -weights[j]), name=f"minus_load[{t},{j}]")
            model.addConstr((off == 1) >> (load == 0), name=f"off_load[{t},{j}]")
            loads.append(load)
        # The pieces on the pans balance the mass t.
        model.addConstr(gp.quicksum(loads) == t, name=f"weigh[{t}]")

    return model, {"weights": [weights[j] for j in pieces]}
