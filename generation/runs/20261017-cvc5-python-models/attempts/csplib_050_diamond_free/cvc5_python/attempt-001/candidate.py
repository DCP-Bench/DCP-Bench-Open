# Problem csplib_050_diamond_free: degree sequences of simple diamond-free graphs.
# The model finds an adjacency matrix of a simple graph on N vertices whose degree
# sequence is nonincreasing, has every degree > 0 and modulo 3, has a degree sum
# modulo 12, and has no diamond (four vertices with at least five edges between them).
from itertools import combinations

import cvc5.pythonic as cz


def build(instance):
    n = instance["N"]

    # One Boolean per unordered pair {i, j} with i < j: the edge is in E.
    edge = {}
    for i in range(n):
        for j in range(i + 1, n):
            edge[(i, j)] = cz.Bool(f"e_{i}_{j}")

    def has_edge(i, j):
        return edge[(min(i, j), max(i, j))]

    # Degree of each vertex: the number of edges incident on it (simple graph, no loops).
    deg = [cz.Sum([cz.If(has_edge(i, j), 1, 0) for j in range(n) if j != i]) for i in range(n)]

    constraints = []

    # The degree of each vertex is greater than zero (isolated vertices are disallowed)
    # and modulo 3. A degree is at most n - 1, so it is one of 3, 6, 9, ... up to n - 1.
    for d in deg:
        constraints.append(cz.Or([d == v for v in range(3, n, 3)]))

    # The degree sequence d_1, ..., d_n is nonincreasing: d_i >= d_{i+1}.
    for i in range(n - 1):
        constraints.append(deg[i] >= deg[i + 1])

    # The sum of the degrees is modulo 12 (the number of edges is modulo 6).
    t = cz.Int("t")
    constraints.append(cz.Sum(deg) == 12 * t)

    # A graph is diamond-free: for every set of four vertices the number of edges
    # between them is at most four (no induced subgraph with at least five edges).
    for quad in combinations(range(n), 4):
        pairs = list(combinations(quad, 2))
        constraints.append(cz.Sum([cz.If(edge[p], 1, 0) for p in pairs]) <= 4)

    # Adjacency matrix: the diagonal is False (no loop edges), the matrix is symmetric.
    matrix = [
        [False if i == j else has_edge(i, j) for j in range(n)]
        for i in range(n)
    ]
    return constraints, {"matrix": matrix}
