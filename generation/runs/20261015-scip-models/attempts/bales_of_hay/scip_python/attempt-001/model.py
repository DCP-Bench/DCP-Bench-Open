# Bales of hay: find the weight of each of n bales, given the weights of all
# combinations of two bales (in numerical order, not matched to their pairs).
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]  # combinations of two bales
    weights = instance["weights"][: len(pairs)]  # the weighings, one per pair
    # bale weights are nonnegative, and a bale is at most any sum it takes part in
    top = max(weights)

    model = Model()
    bales = [model.addVar(name=f"bale_{i}", vtype="I", lb=0, ub=top) for i in range(n)]
    # bales are listed in ascending order of weight (symmetry breaking, any order is a valid answer up to permutation)
    for i in range(n - 1):
        model.addCons(bales[i] <= bales[i + 1])

    # match[p, k] = 1 when the pair p of bales is the one that gave the k-th weighing
    match = {(p, k): model.addVar(name=f"match_{p}_{k}", vtype="B")
             for p in range(len(pairs)) for k in range(len(weights))}

    # the weight of each pair of bales is one of the given weighings, and each pair gets exactly one
    for p, (i, j) in enumerate(pairs):
        model.addCons(quicksum(match[p, k] for k in range(len(weights))) == 1)
        model.addCons(bales[i] + bales[j] == quicksum(weights[k] * match[p, k] for k in range(len(weights))))

    # each given weighing is used by exactly one pair of bales
    for k in range(len(weights)):
        model.addCons(quicksum(match[p, k] for p in range(len(pairs))) == 1)

    return model, {"bales": bales}
