"""Diamond-free graph: find a simple undirected graph on N vertices, as an
adjacency matrix, that has no diamond (four vertices joined by five or more
edges), no isolated vertex, every vertex degree a multiple of 3, and a total
degree (the sum of the whole matrix, twice the number of edges) that is a
multiple of 12.
"""
import itertools

import pulp


def build(instance):
    n = instance["N"]  # number of vertices

    problem = pulp.LpProblem("diamond_free", pulp.LpMinimize)

    # edge[i][j] = 1 if vertices i and j are adjacent. The graph is undirected, so
    # the pair (i, j) and the pair (j, i) share one variable; there are no loops,
    # so the diagonal is the constant 0.
    edge = {(i, j): pulp.LpVariable(f"edge_{i}_{j}", cat="Binary")
            for i in range(n) for j in range(i + 1, n)}

    def adjacent(i, j):
        if i == j:
            return 0
        return edge[(min(i, j), max(i, j))]

    # the adjacency matrix (declared output)
    matrix = [[adjacent(i, j) for j in range(n)] for i in range(n)]

    # every vertex has at least one neighbour, and its degree is a multiple of 3:
    # degree = 3 * thirds with thirds a whole number of at least 1
    for i in range(n):
        thirds = pulp.LpVariable(f"thirds_{i}", 1, (n - 1) // 3, cat="Integer")
        problem += pulp.lpSum(adjacent(i, j) for j in range(n) if j != i) == 3 * thirds

    # the sum of the whole matrix (every edge counted twice) is a multiple of 12
    twelves = pulp.LpVariable("twelves", 0, n * (n - 1) // 12, cat="Integer")
    problem += 2 * pulp.lpSum(edge.values()) == 12 * twelves

    # no diamond: any four vertices have at most four edges among them
    for a, b, c, d in itertools.combinations(range(n), 4):
        problem += pulp.lpSum([adjacent(a, b), adjacent(a, c), adjacent(a, d),
                               adjacent(b, c), adjacent(b, d), adjacent(c, d)]) <= 4

    return problem, {"matrix": matrix}
