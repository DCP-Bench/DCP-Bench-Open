"""Candies: give every child at least one candy, more than any lower-rated neighbour, using as few candies as possible."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)
    children = range(n)

    model = gp.Model("candies")

    # x[i] is the candies child i gets; the reference model declares 1..n.
    x = model.addVars(children, lb=1, ub=n, vtype=GRB.INTEGER, name="x")

    # Of two neighbours, the one with the higher rating gets more candies.
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            model.addConstr(x[i - 1] >= x[i] + 1, name=f"neighbours[{i}]")
        elif ratings[i - 1] < ratings[i]:
            model.addConstr(x[i - 1] + 1 <= x[i], name=f"neighbours[{i}]")

    # Minimise the total number of candies z.
    z = x.sum()
    model.setObjective(z, GRB.MINIMIZE)

    return model, {"z": z, "x": [x[i] for i in children]}
