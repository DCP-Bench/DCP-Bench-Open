import itertools

import z3


def build(instance):
    n = instance["N"]
    matrix = [[z3.Bool(f"matrix_{i}_{j}") for j in range(n)] for i in range(n)]

    def count(cells):
        return z3.Sum([z3.If(cell, 1, 0) for cell in cells])

    constraints = []
    for i in range(n):
        # No isolated vertex, and every degree is a multiple of three.
        constraints.append(count(matrix[i]) > 0)
        constraints.append(count(matrix[i]) % 3 == 0)
        # No self loops.
        constraints.append(z3.Not(matrix[i][i]))
        # Undirected.
        for j in range(i + 1, n):
            constraints.append(matrix[i][j] == matrix[j][i])
    constraints.append(count([cell for row in matrix for cell in row]) % 12 == 0)
    # Diamond-free: any four vertices span at most four of their six edges.
    for a, b, c, d in itertools.combinations(range(n), 4):
        edges = [matrix[a][b], matrix[a][c], matrix[a][d],
                 matrix[b][c], matrix[b][d], matrix[c][d]]
        constraints.append(count(edges) <= 4)
    return constraints, {"matrix": matrix}
