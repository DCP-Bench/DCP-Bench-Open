"""All-interval series: order 0..n-1 so that the distances between neighbours are 1..n-1, each once."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    places = range(n)
    gaps = range(n - 1)
    pitches = range(n)
    intervals = range(1, n)

    model = gp.Model("all_interval")

    # note[i, v] is 1 when position i holds pitch class v: the series is a
    # permutation of 0..n-1.
    note = model.addVars(places, pitches, vtype=GRB.BINARY, name="note")
    for i in places:
        model.addConstr(note.sum(i, "*") == 1, name=f"place[{i}]")
    for v in pitches:
        model.addConstr(note.sum("*", v) == 1, name=f"pitch[{v}]")
    x = [gp.quicksum(v * note[i, v] for v in pitches) for i in places]

    # interval[i, d] is 1 when the i-th interval is d: the intervals are a
    # permutation of 1..n-1.
    interval = model.addVars(gaps, intervals, vtype=GRB.BINARY, name="interval")
    for i in gaps:
        model.addConstr(interval.sum(i, "*") == 1, name=f"gap[{i}]")
    for d in intervals:
        model.addConstr(interval.sum("*", d) == 1, name=f"interval[{d}]")
    diffs = [gp.quicksum(d * interval[i, d] for d in intervals) for i in gaps]

    # Each interval is the distance between neighbouring notes. gp.abs_ takes a
    # variable, not an expression, so the signed step and its size get their own.
    step = model.addVars(gaps, lb=-(n - 1), ub=n - 1, vtype=GRB.INTEGER, name="step")
    size = model.addVars(gaps, lb=0, ub=n - 1, vtype=GRB.INTEGER, name="size")
    for i in gaps:
        model.addConstr(step[i] == x[i + 1] - x[i], name=f"step[{i}]")
        model.addConstr(size[i] == gp.abs_(step[i]), name=f"size[{i}]")
        model.addConstr(size[i] == diffs[i], name=f"distance[{i}]")

    return model, {"x": x, "diffs": diffs}
