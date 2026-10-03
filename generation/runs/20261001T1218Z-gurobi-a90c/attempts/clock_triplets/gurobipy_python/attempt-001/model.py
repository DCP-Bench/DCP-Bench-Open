"""Clock triplets: arrange 1..12 around a clock face so that no three adjacent numbers sum to more than 21."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: 12 positions and the limit 21 are the puzzle's
    # own, mirrored from the reference.
    n = 12
    limit = 21
    places = range(n)
    numbers = range(1, n + 1)

    model = gp.Model("clock_triplets")

    # is_[i, v] is 1 when position i of the clock shows number v; every position shows
    # one number and every number appears once (all different).
    is_ = model.addVars(places, numbers, vtype=GRB.BINARY, name="is")
    for i in places:
        model.addConstr(is_.sum(i, "*") == 1, name=f"one_number[{i}]")
    for v in numbers:
        model.addConstr(is_.sum("*", v) == 1, name=f"used_once[{v}]")
    x = [gp.quicksum(v * is_[i, v] for v in numbers) for i in places]

    # The largest sum of three adjacent numbers (wrapping around the clock) is at most 21.
    triplet_sum = model.addVar(lb=0, ub=limit, vtype=GRB.INTEGER, name="triplet_sum")
    for i in places:
        model.addConstr(x[i] + x[i - 1] + x[i - 2] <= triplet_sum, name=f"triplet[{i}]")

    return model, {"x": x}
