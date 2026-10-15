# Twelve-pack problem: choose how many packs of each size to buy so that the
# total number of items meets or exceeds the target, with the smallest possible
# total (the closest combination that is not below the target).
from pyscipopt import Model, quicksum


def build(instance):
    packs = instance["packs"]
    target = instance["target"]
    n = len(packs)

    m = Model()
    # counts[j] = number of packs of size packs[j] that are used
    # the largest useful count is the target divided by the smallest pack, plus one
    ub = target // min(packs) + 1
    counts = [m.addVar(name=f"counts_{j}", vtype="I", lb=0, ub=ub) for j in range(n)]

    # total number of items bought
    total = quicksum(packs[j] * counts[j] for j in range(n))

    # the items must meet or exceed the target
    m.addCons(total >= target)

    # closest combination: minimise the total number of items bought
    m.setObjective(total, "minimize")

    # the output gives the count of each pack size, in the order of the packs
    return m, {"counts": counts}
