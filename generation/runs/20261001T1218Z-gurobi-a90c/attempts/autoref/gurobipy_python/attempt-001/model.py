"""Self-referential sequence: a sequence s of n + 2 numbers in which the number of occurrences of i is s[i], and s[n + 1] is m."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n, m = instance["n"], instance["m"]
    places = range(n + 2)  # the sequence has n + 2 entries
    values = range(n + 1)  # each entry is a number in 0..n

    model = gp.Model("autoref")

    # holds[p, v] is 1 when s[p] = v. One-hot values let the counts be read off linearly.
    holds = model.addVars(places, values, vtype=GRB.BINARY, name="holds")
    for p in places:
        model.addConstr(holds.sum(p, "*") == 1, name=f"one_value[{p}]")
    s = [gp.quicksum(v * holds[p, v] for v in values) for p in places]

    # The number of occurrences of the value i in the whole sequence is s[i], for i = 0..n.
    for i in values:
        model.addConstr(holds.sum("*", i) == s[i], name=f"count[{i}]")

    # The last entry is the given number m.
    model.addConstr(s[n + 1] == m, name="last_is_m")

    return model, {"s": s}
