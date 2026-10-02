# Diamond-free graphs: find a simple undirected graph on N vertices, given as
# an adjacency matrix, with no diamond (four vertices joined by at least five
# edges), no isolated vertex, every vertex degree a multiple of 3 and a total
# degree (twice the number of edges) that is a multiple of 12.
from itertools import combinations

from hermax.model import Model


def build(instance):
    n = instance["N"]  # number of vertices

    m = Model()
    # matrix[i][j] = vertices i and j are adjacent
    matrix = m.bool_matrix("matrix", n, n)

    # the graph is simple and undirected: no loops, and the matrix is symmetric
    for i in range(n):
        m &= ~matrix[i][i]
        for j in range(i + 1, n):
            m &= (~matrix[i][j] | matrix[j][i])
            m &= (matrix[i][j] | ~matrix[j][i])

    # Every degree is positive and a multiple of 3, i.e. 3 * k[i] with k[i] >= 1.
    # The degree of a vertex is at most n - 1, which bounds k[i]. A multiple of 3
    # is written as three times a small integer because a modulo test is not
    # part of the modelling layer.
    k = m.int_vector("k", n, 1, (n - 1) // 3)
    for i in range(n):
        m &= (sum(matrix[i][j] for j in range(n)) == 3 * k[i])

    # The sum of all degrees is a multiple of 12. The degrees add up to
    # 3 * sum(k), so sum(k) must be a multiple of 4; t is the number of fours.
    t = m.int("t", 1, (n * ((n - 1) // 3)) // 4)
    m &= (sum(k[i] for i in range(n)) == 4 * t)

    # No diamond: among any four vertices at most four of the six possible
    # edges are present. Forbidding every set of five of the six edges is the
    # same statement, and each such set is one short clause.
    for quad in combinations(range(n), 4):
        edges = [matrix[a][b] for a, b in combinations(quad, 2)]
        for five in combinations(edges, 5):
            clause = ~five[0]
            for edge in five[1:]:
                clause = clause | ~edge
            m &= clause

    return m, {"matrix": matrix}
