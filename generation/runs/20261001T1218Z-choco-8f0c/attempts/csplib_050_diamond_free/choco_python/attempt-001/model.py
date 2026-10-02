# Diamond-free graph: find a simple undirected graph on N vertices with no
# isolated vertex, every degree a multiple of 3, a degree sum that is a multiple
# of 12, and no four vertices joined by five or more edges (no induced diamond).
from itertools import combinations

from pychoco.model import Model


def build(instance):
    n = instance["N"]  # number of vertices

    model = Model()

    # The graph is simple and undirected, so there is one edge variable per pair
    # of vertices and the matrix is symmetric by construction (matrix[a][b] and
    # matrix[b][a] are the same variable). No vertex has an edge to itself, so
    # the diagonal is fixed to 0.
    edge = {}
    for a, b in combinations(range(n), 2):
        edge[a, b] = model.boolvar(name=f"edge_{a}_{b}")
    matrix = [[edge[min(a, b), max(a, b)] if a != b else False for b in range(n)] for a in range(n)]

    # every vertex has at least one edge and its degree is a multiple of 3: its
    # degree is a variable whose domain is the positive multiples of 3
    degrees = []
    for a in range(n):
        degree = model.intvar(list(range(3, n, 3)), name=f"degree_{a}")
        model.sum([matrix[a][b] for b in range(n) if b != a], "=", degree).post()
        degrees.append(degree)

    # the sum of all matrix entries (the sum of the degrees) is a multiple of 12
    degree_sum = model.intvar(list(range(12, n * (n - 1) + 1, 12)), name="degree_sum")
    model.sum(degrees, "=", degree_sum).post()

    # every group of four vertices has at most four edges between them
    for a, b, c, d in combinations(range(n), 4):
        model.sum([matrix[a][b], matrix[a][c], matrix[a][d],
                   matrix[b][c], matrix[b][d], matrix[c][d]], "<=", 4).post()

    return model, {"matrix": matrix}
