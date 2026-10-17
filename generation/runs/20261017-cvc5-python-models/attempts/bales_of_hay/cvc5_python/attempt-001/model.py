# Problem: bales_of_hay
# You have a number of bales of hay. The bales were weighed in all possible
# combinations of two, and the weights of these combinations were written down
# and arranged in numerical order, without keeping track of which weight matched
# which pair of bales. The weights are given in a list.
# Print the weight of each bale (bales) as a list of integers.

import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    weights = instance["weights"]
    W = len(weights)

    bales = [cz.Int(f"bale_{i}") for i in range(n)]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    K = len(pairs)

    # one index per pair of bales: which listed weight that pair produced
    t = [cz.Int(f"t_{q}") for q in range(K)]

    constraints = []

    # A bale has a weight: it is not negative, and no bale outweighs the heaviest listed combination.
    maxw = max(weights)
    for b in bales:
        constraints.append(b >= 0)
        constraints.append(b <= maxw)

    # The weights of all combinations of two bales were written down, in numerical order.
    # Each pair of bales gives one listed weight, and the combined weight of the pair is that listed weight.
    for q, (i, j) in enumerate(pairs):
        constraints.append(t[q] >= 0)
        constraints.append(t[q] < W)
        opts = [cz.And(t[q] == k, bales[i] + bales[j] == weights[k]) for k in range(W)]
        constraints.append(opts[0] if len(opts) == 1 else cz.Or(opts))

    # Without keeping track of which weight matched which pair, every listed weight is used by exactly one pair.
    if K >= 2:
        constraints.append(cz.Distinct(t))

    return constraints, {"bales": bales}
