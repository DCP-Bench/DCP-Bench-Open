"""0-1 knapsack: choose items of maximal total value whose total weight fits the capacity."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]
    items = range(len(values))

    model = gp.Model("knapsack")

    # x[i] is 1 when item i is packed.
    x = [model.addVar(vtype=GRB.BINARY, name=f"x[{i}]") for i in items]

    # The packed items must not exceed the weight capacity.
    model.addConstr(gp.quicksum(weights[i] * x[i] for i in items) <= capacity, name="capacity")

    # Maximise the total value of the packed items.
    model.setObjective(gp.quicksum(values[i] * x[i] for i in items), GRB.MAXIMIZE)

    return model, {"x": x}
