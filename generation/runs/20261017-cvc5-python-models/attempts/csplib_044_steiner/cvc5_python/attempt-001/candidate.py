# csplib_044_steiner: ternary Steiner system of order n. Find n(n-1)/6 triples of
# distinct integer elements from {1, ..., n} such that any two triples have at most
# one common element. Output "sets" is a boolean matrix: row = triple, column = element.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    b = n * (n - 1) // 6
    x = [[cz.Bool(f"x_{i}_{j}") for j in range(n)] for i in range(b)]
    cons = []

    # triples of distinct integer elements: each row holds exactly three elements
    for i in range(b):
        cons.append(cz.Sum([cz.If(x[i][j], 1, 0) for j in range(n)]) == 3)

    # any two triples have at most one common element. Equivalently, each pair of
    # elements lies in at most one triple. With n(n-1)/6 triples covering 3 pairs each,
    # the count forces each pair of elements into exactly one triple.
    for j in range(n):
        for k in range(j + 1, n):
            cons.append(
                cz.Sum([cz.If(cz.And(x[i][j], x[i][k]), 1, 0) for i in range(b)]) == 1
            )

    return cons, {"sets": x}
