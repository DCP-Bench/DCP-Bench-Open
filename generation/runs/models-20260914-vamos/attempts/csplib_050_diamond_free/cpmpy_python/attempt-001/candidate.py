import itertools

import cpmpy as cp


def build(instance):
    n = instance["N"]
    matrix = cp.boolvar(shape=(n, n), name="matrix")
    model = cp.Model()
    for i in range(n):
        row = [matrix[i, j] for j in range(n)]
        # No isolated vertex, and every degree is a multiple of three.
        model += cp.sum(row) > 0
        model += cp.sum(row) % 3 == 0
        # No self loop, and the graph is undirected.
        model += ~matrix[i, i]
        for j in range(i + 1, n):
            model += matrix[i, j] == matrix[j, i]
    model += cp.sum([matrix[i, j] for i in range(n) for j in range(n)]) % 12 == 0
    # Diamond-free: any four vertices span at most four of their six edges.
    for a, b, c, d in itertools.combinations(range(n), 4):
        model += cp.sum([matrix[a, b], matrix[a, c], matrix[a, d],
                         matrix[b, c], matrix[b, d], matrix[c, d]]) <= 4
    return model, {"matrix": [[matrix[i, j] for j in range(n)] for i in range(n)]}
