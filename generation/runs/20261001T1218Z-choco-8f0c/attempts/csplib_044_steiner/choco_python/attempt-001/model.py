# Ternary Steiner problem of order n: find n*(n-1)/6 triples of distinct elements out of
# 1..n such that any two triples have at most one element in common.
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # order of the Steiner triple system (n mod 6 is 1 or 3)
    n_sets = n * (n - 1) // 6  # number of triples

    model = Model()

    # sets[i][j] is true when element j is part of triple i
    sets = [[model.boolvar(name=f"sets_{i}_{j}") for j in range(n)] for i in range(n_sets)]

    # every triple has exactly 3 elements
    for triple in sets:
        model.sum(triple, "=", 3).post()

    # Any two triples have at most one element in common. This is posted as the same
    # statement seen from the elements: no pair of elements {a, b} lies in two triples
    # (two triples sharing a and b would have two common elements).
    # together[i][a][b] is true when triple i contains both a and b.
    # If n*(n-1)/6 triples of 3 elements are chosen, they hold 3 * n_sets = n*(n-1)/2
    # pairs, which is every pair of elements, and no pair repeats; so every pair then
    # occurs exactly once (implied, and stronger for the solver than "at most once").
    pair_count_operator = "=" if 3 * n_sets == n * (n - 1) // 2 else "<="
    for a in range(n):
        for b in range(a + 1, n):
            together = [model.sum([sets[i][a], sets[i][b]], "=", 2).reify() for i in range(n_sets)]
            model.sum(together, pair_count_operator, 1).post()

    return model, {"sets": sets}
