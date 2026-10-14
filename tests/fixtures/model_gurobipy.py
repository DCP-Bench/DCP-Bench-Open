import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    model = gp.Model()
    x = model.addVar(lb=0, ub=n, vtype=GRB.INTEGER, name="x")
    y = model.addVar(lb=0, ub=n, vtype=GRB.INTEGER, name="y")
    if instance["optimize"]:
        model.addConstr(x + y >= n)
        model.setObjective(x + y, GRB.MINIMIZE)
    else:
        model.addConstr(x + y == n)
    return model, {"x": x, "y": y}
