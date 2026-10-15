"""Ternary Steiner system of order n (CSPLib 044), Paramita model.

Finds b = n(n-1)/6 triples over the elements 1..n such that any two
triples share at most one element. Output: boolean matrix sets[t][e],
true when element e belongs to triple t.
"""

from paramita.modelling import Bool, And


def build(instance):
    n = instance["n"]
    # number of triples in the system, n(n-1)/6
    b = n * (n - 1) // 6

    # X[t][e] = 1 if element e is in triple t
    X = [[Bool(f"x_{t}_{e}") for e in range(n)] for t in range(b)]

    cons = []

    # each triple consists of three distinct elements
    # (a triple is a set of three elements)
    for t in range(b):
        cons.append(sum(X[t]) == 3)

    # any two triples have at most one common element
    # (the common elements of triples t and s are counted by the aux Bools)
    for t in range(b):
        for s in range(t + 1, b):
            cons.append(sum(And([X[t][e], X[s][e]]) for e in range(n)) <= 1)

    # every pair of elements lies in exactly one triple
    # (redundant: the triples cover 3b = n(n-1)/2 pairs, and no pair is covered twice)
    for i in range(n):
        for j in range(i + 1, n):
            cons.append(sum(And([X[t][i], X[t][j]]) for t in range(b)) == 1)

    return cons, {"sets": X}
