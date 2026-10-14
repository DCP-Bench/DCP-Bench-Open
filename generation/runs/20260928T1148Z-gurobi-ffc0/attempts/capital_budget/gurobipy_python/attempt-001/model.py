"""Capital budgeting: choose investments within the budget to maximise the total net present value."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    npv = instance["npv"]
    cash_flow = instance["cash_flow"]
    investments = range(len(npv))

    model = gp.Model("capital_budget")

    # x[i] is 1 when investment i is chosen.
    x = model.addVars(investments, vtype=GRB.BINARY, name="x")

    # The cash outflow of the chosen investments stays within the budget.
    model.addConstr(gp.quicksum(cash_flow[i] * x[i] for i in investments) <= instance["budget"],
                    name="budget")

    # z is the total NPV of the chosen investments, and it is maximised.
    z = gp.quicksum(npv[i] * x[i] for i in investments)
    model.setObjective(z, GRB.MAXIMIZE)

    return model, {"x": [x[i] for i in investments], "z": z}
