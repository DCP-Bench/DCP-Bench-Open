# Diamond-free graph: build a simple undirected graph on N vertices, given as an adjacency
# matrix, in which no four vertices span five or more edges, no vertex is isolated, every
# degree is a multiple of 3 and the sum of all degrees is a multiple of 12.
from itertools import combinations

from exact import Exact


def build(instance):
    n = instance["N"]  # number of vertices

    solver = Exact()

    # matrix[i][j] = 1 when vertices i and j are adjacent
    matrix = [[f"matrix_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(matrix[i][j], 0, 1)
        # no vertex is adjacent to itself (the diagonal is 0)
        solver.addConstraint([(1, matrix[i][i])], True, 0, True, 0)

    # the graph is undirected: matrix[i][j] == matrix[j][i]
    for i in range(n):
        for j in range(i + 1, n):
            solver.addConstraint([(1, matrix[i][j]), (-1, matrix[j][i])], True, 0, True, 0)

    # every degree is positive and a multiple of 3: degree_i = 3 * thirds[i] with thirds[i] >= 1
    # (Exact has no modulo, so the multiple is an integer variable; a degree is at most n - 1)
    thirds = [f"degree_{i}_div_3" for i in range(n)]
    for i in range(n):
        solver.addVariable(thirds[i], 1, (n - 1) // 3)
        solver.addConstraint([(1, matrix[i][j]) for j in range(n)] + [(-3, thirds[i])], True, 0, True, 0)

    # the sum of the whole matrix (the sum of all degrees) is a multiple of 12:
    # the total is 12 * matrix_total_div_12 and is at most n * (n - 1)
    solver.addVariable("matrix_total_div_12", 1, (n * (n - 1)) // 12)
    solver.addConstraint([(1, matrix[i][j]) for i in range(n) for j in range(n)]
                         + [(-12, "matrix_total_div_12")], True, 0, True, 0)

    # diamond-free: any four vertices have at most four edges among the six pairs between them
    for a, b, c, d in combinations(range(n), 4):
        pairs = [(a, b), (a, c), (a, d), (b, c), (b, d), (c, d)]
        solver.addConstraint([(1, matrix[i][j]) for i, j in pairs], False, 0, True, 4)

    return solver, {"matrix": matrix}
