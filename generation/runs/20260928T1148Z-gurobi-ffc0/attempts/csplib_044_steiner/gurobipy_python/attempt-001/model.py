"""Steiner triple system: choose n(n-1)/6 triples of 1..n such that any two triples share at most one element."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    triples = range(n * (n - 1) // 6)
    elements = range(n)

    model = gp.Model("steiner")

    # sets[t, e] is 1 when element e is in triple t; every triple has three elements.
    sets = model.addVars(triples, elements, vtype=GRB.BINARY, name="sets")
    for t in triples:
        model.addConstr(sets.sum(t, "*") == 3, name=f"size[{t}]")

    # Two triples share at most one element. both[s, t, e] is 1 when element e
    # is in triples s and t; the lower bound is all that is needed, since the
    # constraint caps the number of shared elements from above.
    pairs = [(s, t) for s in triples for t in triples if s < t]
    both = model.addVars([(s, t, e) for (s, t) in pairs for e in elements], vtype=GRB.BINARY, name="both")
    for (s, t) in pairs:
        for e in elements:
            model.addConstr(both[s, t, e] >= sets[s, e] + sets[t, e] - 1, name=f"both[{s},{t},{e}]")
        model.addConstr(gp.quicksum(both[s, t, e] for e in elements) <= 1, name=f"share[{s},{t}]")

    return model, {"sets": [[sets[t, e] for e in elements] for t in triples]}
