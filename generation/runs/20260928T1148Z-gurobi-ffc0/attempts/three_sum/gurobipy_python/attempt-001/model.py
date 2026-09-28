"""Zero sum: select exactly m of the numbers so that they add up to zero."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    nums, m = instance["nums"], instance["m"]
    items = range(len(nums))

    model = gp.Model("three_sum")

    # indices[i] is 1 when nums[i] is selected.
    indices = model.addVars(items, vtype=GRB.BINARY, name="indices")

    # The selected numbers add up to zero.
    model.addConstr(gp.quicksum(nums[i] * indices[i] for i in items) == 0, name="zero_sum")

    # Exactly m numbers are selected.
    model.addConstr(indices.sum() == m, name="count")

    return model, {"indices": [indices[i] for i in items]}
