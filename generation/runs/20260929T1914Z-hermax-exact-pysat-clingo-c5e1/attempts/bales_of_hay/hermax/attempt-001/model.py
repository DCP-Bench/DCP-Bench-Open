# Bales of hay: the bales were weighed in all combinations of two and the
# weights, in numerical order, are given. Find the weight of each bale.
from collections import Counter
from itertools import combinations

from hermax.model import Model


def build(instance):
    n = instance["n"]  # number of bales
    weights = instance["weights"]  # the weights of the pairs, in numerical order
    pairs = list(combinations(range(n), 2))

    m = Model()
    # bales[i] = the weight of bale i
    bales = m.int_vector("bales", n, 0, 50)
    # pair_weight[p] = the weight of the p-th pair of bales
    pair_weight = [m.int(f"pair_{i}_{j}", 0, 100) for i, j in pairs]
    for p, (i, j) in enumerate(pairs):
        m &= (pair_weight[p] == bales[i] + bales[j])

    # The written-down weights are exactly the weights of the pairs: each weight
    # value is the weight of as many pairs as times it was written down. (There are
    # as many pairs as written weights, so no pair is left over.)
    for value, times in Counter(weights).items():
        m &= (sum(1 * (pair_weight[p] == value) for p in range(len(pairs))) == times)

    return m, {"bales": bales}
