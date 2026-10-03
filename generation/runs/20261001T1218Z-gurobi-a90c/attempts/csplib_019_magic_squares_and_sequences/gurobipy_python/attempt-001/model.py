"""Magic sequence: a sequence x of length n over 0..n-1 in which the value i occurs exactly x[i] times."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    places = range(n)

    model = gp.Model("magic_sequence")

    # holds[p, v] is 1 when x[p] = v. One-hot values let the occurrences be counted linearly.
    holds = model.addVars(places, places, vtype=GRB.BINARY, name="holds")
    for p in places:
        model.addConstr(holds.sum(p, "*") == 1, name=f"one_value[{p}]")
    x = [gp.quicksum(v * holds[p, v] for v in places) for p in places]

    # The value i occurs exactly x[i] times in the sequence.
    for i in places:
        model.addConstr(holds.sum("*", i) == x[i], name=f"occurs[{i}]")

    return model, {"x": x}
