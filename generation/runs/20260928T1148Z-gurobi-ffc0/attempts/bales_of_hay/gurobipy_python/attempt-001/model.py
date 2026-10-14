"""Bales of hay: recover the weight of each bale from the unlabelled weights of every pair of bales."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    weights = instance["weights"]  # the written-down pair weights, in no particular order
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    written = range(len(weights))

    model = gp.Model("bales_of_hay")

    # bales[i] is the weight of bale i; the reference model declares 0..50,
    # so every pair weighs at most 100, as its pair weights allow.
    bales = model.addVars(n, lb=0, ub=50, vtype=GRB.INTEGER, name="bales")

    # matches[k, p] is 1 when written weight k is the weight of pair p.
    matches = model.addVars(written, range(len(pairs)), vtype=GRB.BINARY, name="matches")

    # Every written weight belongs to exactly one pair, and no pair takes two
    # written weights: each weight was recorded for a pair of its own.
    for k in written:
        model.addConstr(matches.sum(k, "*") == 1, name=f"weight[{k}]")
    for p in range(len(pairs)):
        model.addConstr(matches.sum("*", p) <= 1, name=f"pair[{p}]")

    # A written weight matched to a pair is that pair's total weight.
    for k in written:
        for p, (i, j) in enumerate(pairs):
            model.addConstr((matches[k, p] == 1) >> (bales[i] + bales[j] == weights[k]),
                            name=f"weighs[{k},{p}]")

    return model, {"bales": [bales[i] for i in range(n)]}
