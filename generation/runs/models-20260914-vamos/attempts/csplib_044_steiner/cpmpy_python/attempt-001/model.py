import itertools

import cpmpy as cp


def build(instance):
    n = instance["n"]
    n_sets = n * (n - 1) // 6
    sets = cp.boolvar(shape=(n_sets, n), name="sets")
    model = cp.Model()
    for i in range(n_sets):
        # Every triple holds three elements.
        model += cp.sum([sets[i, j] for j in range(n)]) == 3
    for i1, i2 in itertools.combinations(range(n_sets), 2):
        # Two triples share at most one element.
        model += cp.sum([sets[i1, j] & sets[i2, j] for j in range(n)]) <= 1
    return model, {"sets": [[sets[i, j] for j in range(n)] for i in range(n_sets)]}
