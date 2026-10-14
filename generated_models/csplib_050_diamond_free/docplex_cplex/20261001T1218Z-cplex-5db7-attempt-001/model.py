"""Diamond-free graph: a simple undirected graph on N vertices with no diamond.

A diamond is a set of four vertices with at least five edges among them. Every vertex has
a positive degree that is a multiple of 3, and the sum of the degrees (twice the number
of edges) is a multiple of 12. The model finds the adjacency matrix of such a graph.
"""
from itertools import combinations

from docplex.mp.model import Model


def build(instance):
    n = instance["N"]  # number of vertices
    vertices = range(n)

    model = Model("diamond_free")

    # edge[u, v] is 1 when u and v are adjacent, for u < v. The matrix is symmetric and has
    # no loops, so the lower triangle and the diagonal need no variables of their own.
    edge = {(u, v): model.binary_var(name=f"edge_{u}_{v}") for u, v in combinations(vertices, 2)}

    def adjacent(u, v):
        return edge[(u, v)] if u < v else edge[(v, u)]

    # Every vertex has a positive degree that is a multiple of 3: degree = 3 * groups with
    # groups at least 1. At most n - 1 other vertices can be neighbours.
    degree = []
    for u in vertices:
        groups = model.integer_var(1, (n - 1) // 3, name=f"groups_{u}")
        row_sum = model.sum(adjacent(u, v) for v in vertices if v != u)
        model.add_constraint(row_sum == 3 * groups)
        degree.append(row_sum)

    # The sum of the matrix (the sum of all degrees) is a multiple of 12.
    twelves = model.integer_var(0, n * (n - 1) // 12, name="twelves")
    model.add_constraint(model.sum(degree) == 12 * twelves)

    # No diamond. Four vertices hold at least five edges exactly when one edge lies in two
    # triangles: its two ends plus two more vertices adjacent to both. So it is enough to
    # allow every edge at most one triangle. This takes one row per triple of vertices and
    # one per edge, where "at most four edges among every four vertices" would take one row
    # per quadruple, more than the Community Edition's 1000 rows once n reaches 14.
    # triangle[t] is forced to 1 when all three edges of the triple t are present.
    triangle = {}
    for u, v, w in combinations(vertices, 3):
        triangle[(u, v, w)] = model.binary_var(name=f"triangle_{u}_{v}_{w}")
        model.add_constraint(
            triangle[(u, v, w)] >= edge[(u, v)] + edge[(u, w)] + edge[(v, w)] - 2)
    for u, v in combinations(vertices, 2):
        model.add_constraint(
            model.sum(triangle[tuple(sorted((u, v, w)))] for w in vertices if w not in (u, v)) <= 1)

    # The declared output: the adjacency matrix, with 0 on the diagonal (no loops).
    matrix = [[adjacent(u, v) if u != v else 0 for v in vertices] for u in vertices]
    return model, {"matrix": matrix}
