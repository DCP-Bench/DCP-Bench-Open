# Diamond-free graph on N vertices with degrees > 0, divisible by 3, sum of degrees divisible by 12, sorted non-increasing; output the adjacency matrix.
from itertools import combinations

from pyscipopt import Model, quicksum


def build(instance):
    n = instance["N"]
    vertices = range(n)
    m = Model()

    # e[u, v] = 1 if {u, v} is an edge (u < v); the graph is undirected and simple
    e = {}
    for u, v in combinations(vertices, 2):
        e[u, v] = m.addVar(name=f"e_{u}_{v}", vtype="B")

    def edge(u, v):
        return e[min(u, v), max(u, v)]

    # adjacency matrix output; the diagonal is fixed to 0 (no loop edges)
    matrix = [[None] * n for _ in vertices]
    for u in vertices:
        for v in vertices:
            if u == v:
                matrix[u][v] = m.addVar(name=f"loop_{u}", vtype="B", lb=0, ub=0)
            else:
                matrix[u][v] = edge(u, v)

    # degree of each vertex is 3 * z[v], with z[v] >= 1 so every degree is positive and divisible by 3
    z = [m.addVar(name=f"z_{v}", vtype="I", lb=1, ub=(n - 1) // 3) for v in vertices]
    for v in vertices:
        # the degree of vertex v is the number of edges incident on v
        m.addCons(quicksum(edge(v, u) for u in vertices if u != v) == 3 * z[v])

    # the degree sequence is non-increasing: d_v >= d_{v+1}
    for v in range(n - 1):
        m.addCons(z[v] >= z[v + 1])

    # the sum of the degrees is divisible by 12: sum of 3 * z[v] = 12 * w
    w = m.addVar(name="w", vtype="I", lb=0, ub=(n * (n - 1)) // 12)
    m.addCons(quicksum(3 * z[v] for v in vertices) == 12 * w)

    # no diamond: every set of four vertices spans at most four edges
    # (a diamond is four vertices with at least five edges between them)
    for quad in combinations(vertices, 4):
        m.addCons(quicksum(edge(a, b) for a, b in combinations(quad, 2)) <= 4)

    return m, {"matrix": matrix}
