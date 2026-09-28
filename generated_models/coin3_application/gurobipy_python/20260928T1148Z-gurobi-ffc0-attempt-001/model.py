"""Coin set: the fewest coins from which every amount below the maximum can be paid exactly."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    denominations = instance["denominations"]
    top = instance["max_amount_to_pay"]
    kinds = range(len(denominations))
    amounts = range(1, top)

    model = gp.Model("coin3_application")

    # x[i] is how many coins of denomination i are in the set; the reference
    # model allows 0..top for each, and 0..top for their total.
    x = model.addVars(kinds, lb=0, ub=top, vtype=GRB.INTEGER, name="x")
    model.addConstr(x.sum() <= top, name="total_coins")

    # For every amount from 1 to top - 1, some selection of the coins in the set
    # pays it exactly: pay[j, i] coins of denomination i, never more than x[i].
    pay = model.addVars(amounts, kinds, lb=0, ub=top, vtype=GRB.INTEGER, name="pay")
    for j in amounts:
        model.addConstr(gp.quicksum(denominations[i] * pay[j, i] for i in kinds) == j, name=f"pays[{j}]")
        for i in kinds:
            model.addConstr(pay[j, i] <= x[i], name=f"from_set[{j},{i}]")

    # Minimise the number of coins in the set.
    model.setObjective(x.sum(), GRB.MINIMIZE)

    return model, {"x": [x[i] for i in kinds]}
