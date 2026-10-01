# Ternary Steiner problem: find n * (n - 1) / 6 triples of distinct elements of {1, ..., n} such
# that any two triples share at most one element (n is 1 or 3 modulo 6).
import cpmpy as cp


def build(instance):
    n = instance["n"]
    n_sets = n * (n - 1) // 6  # number of triples required

    # sets[i, j] = True iff element j is part of triple i
    sets = cp.boolvar(shape=(n_sets, n), name="sets")

    model = cp.Model()

    # Each triple has exactly three elements.
    for i in range(n_sets):
        model += cp.sum(sets[i, :]) == 3

    # Any two triples have at most one element in common.
    for i in range(n_sets):
        for k in range(i + 1, n_sets):
            model += cp.sum(sets[i, :] & sets[k, :]) <= 1

    return model, {"sets": sets}
