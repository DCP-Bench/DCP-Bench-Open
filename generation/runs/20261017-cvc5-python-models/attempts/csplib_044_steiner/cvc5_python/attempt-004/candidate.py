# csplib_044_steiner: ternary Steiner system of order n. Find n(n-1)/6 triples of
# distinct integer elements from {1, ..., n} such that any two triples have at most
# one common element. Output "sets" is a boolean matrix: row = triple, column = element.
#
# Boolean clauses carry the set structure; a sum per element carries the implied degree.
from itertools import combinations

import cvc5.pythonic as cz


def clause(lits):
    return lits[0] if len(lits) == 1 else cz.Or(lits)


def build(instance):
    n = instance["n"]
    b = n * (n - 1) // 6
    r = (n - 1) // 2
    x = [[cz.Bool(f"x_{i}_{j}") for j in range(n)] for i in range(b)]
    cons = []

    # triples of distinct integer elements: each row holds exactly three elements.
    # At most three true: no 4 elements of a row are all true.
    # At least three true: no n-2 elements of a row are all false.
    for i in range(b):
        for quad in combinations(range(n), 4):
            cons.append(clause([cz.Not(x[i][j]) for j in quad]))
        for rest in combinations(range(n), n - 2):
            cons.append(clause([x[i][j] for j in rest]))

    # implied by the Steiner condition: element j is paired with each of the other
    # n-1 elements exactly once, and each triple through j covers two of those pairs,
    # so j lies in (n-1)/2 triples
    for j in range(n):
        cons.append(cz.Sum([cz.If(x[i][j], 1, 0) for i in range(b)]) == r)

    # any two triples have at most one common element: no two triples both contain
    # the same two elements. Two rows i < i2 cannot both hold the pair j < k.
    for i in range(b):
        for i2 in range(i + 1, b):
            for j, k in combinations(range(n), 2):
                cons.append(
                    clause([cz.Not(x[i][j]), cz.Not(x[i][k]),
                            cz.Not(x[i2][j]), cz.Not(x[i2][k])])
                )

    # the triples cover every pair of elements (the Steiner condition); with the
    # count n(n-1)/6 this is exactly one triple per pair
    for j, k in combinations(range(n), 2):
        covers = [cz.And(x[i][j], x[i][k]) for i in range(b)]
        cons.append(clause(covers))

    return cons, {"sets": x}
