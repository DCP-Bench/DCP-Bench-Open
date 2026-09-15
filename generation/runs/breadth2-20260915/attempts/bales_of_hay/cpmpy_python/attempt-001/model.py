import itertools

import cpmpy as cp

# The reference's own bound on a single bale.
HEAVIEST = 50


def build(instance):
    n, weights = instance["n"], instance["weights"]
    bales = cp.intvar(0, HEAVIEST, shape=n, name="bales")
    model = cp.Model()
    for weight in weights:
        # Some pair of distinct bales weighs this much.
        model += cp.any([bales[i] + bales[j] == weight
                         for i, j in itertools.combinations(range(n), 2)])
    return model, {"bales": [bales[i] for i in range(n)]}
