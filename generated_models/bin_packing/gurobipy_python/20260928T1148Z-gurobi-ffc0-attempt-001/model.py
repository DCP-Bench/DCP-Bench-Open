"""Bin packing: put every item in one of the bins so that no bin holds more than its capacity."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    weights = instance["weights"]
    capacity = instance["capacity"]
    items = range(len(weights))
    bins = range(instance["num_bins"])

    model = gp.Model("bin_packing")

    # put[j, b] is 1 when item j goes into bin b.
    put = model.addVars(items, bins, vtype=GRB.BINARY, name="put")

    # Every item goes into exactly one bin.
    for j in items:
        model.addConstr(put.sum(j, "*") == 1, name=f"one_bin[{j}]")

    # The items in a bin weigh no more than the bin's capacity.
    for b in bins:
        model.addConstr(gp.quicksum(weights[j] * put[j, b] for j in items) <= capacity,
                        name=f"capacity[{b}]")

    # The bin of each item, 0-indexed, read back from the assignment.
    bin_of = [gp.quicksum(b * put[j, b] for b in bins) for j in items]
    return model, {"bins": bin_of}
