# Bales of hay: the bales were weighed in all combinations of two and the
# weights, in numerical order, are given. Find the weight of each bale.
from collections import Counter
from itertools import combinations

from exact import Exact


def build(instance):
    n = instance["n"]  # number of bales
    weights = instance["weights"]  # the weights of the pairs, in numerical order
    pairs = list(combinations(range(n), 2))
    values = sorted(set(weights))

    solver = Exact()
    # bales[i] = the weight of bale i
    bales = [f"bales_{i}" for i in range(n)]
    for name in bales:
        solver.addVariable(name, 0, 50)

    # is_[p][v] = 1 when the p-th pair of bales weighs values[v]
    is_ = [[f"pair_{i}_{j}_is_{v}" for v in range(len(values))] for i, j in pairs]
    for p, (i, j) in enumerate(pairs):
        for name in is_[p]:
            solver.addVariable(name, 0, 1)
        # a pair weighs one of the written-down weights, and that is the sum of its two bales
        solver.addConstraint([(1, name) for name in is_[p]], True, 1, True, 1)
        solver.addConstraint([(values[v], is_[p][v]) for v in range(len(values))]
                             + [(-1, bales[i]), (-1, bales[j])], True, 0, True, 0)

    # each weight value is the weight of as many pairs as times it was written down
    counts = Counter(weights)
    for v, value in enumerate(values):
        solver.addConstraint([(1, is_[p][v]) for p in range(len(pairs))],
                             True, counts[value], True, counts[value])

    return solver, {"bales": bales}
