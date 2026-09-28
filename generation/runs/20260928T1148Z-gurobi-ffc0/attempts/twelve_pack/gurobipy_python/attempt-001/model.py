"""Twelve pack: buy packs of the given sizes to get at least the target number of items, as few over it as possible."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    packs, target = instance["packs"], instance["target"]
    sizes = range(len(packs))
    # The reference model caps each pack count at twice the target, and the
    # total number of items at that cap times the number of pack sizes.
    max_count = 2 * target

    model = gp.Model("twelve_pack")

    # counts[i] is how many packs of size i are bought.
    counts = model.addVars(sizes, lb=0, ub=max_count, vtype=GRB.INTEGER, name="counts")

    # total is the number of items bought, which meets or exceeds the target.
    total = model.addVar(lb=0, ub=max_count * len(packs), vtype=GRB.INTEGER, name="total")
    model.addConstr(total == gp.quicksum(packs[i] * counts[i] for i in sizes), name="items")
    model.addConstr(total >= target, name="enough")

    # Get as close to the target as possible, which means buying the fewest items.
    model.setObjective(total, GRB.MINIMIZE)

    return model, {"counts": [counts[i] for i in sizes]}
