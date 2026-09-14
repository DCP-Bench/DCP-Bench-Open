import itertools

from ortools.sat.python import cp_model


def build(instance):
    n = instance["N"]
    model = cp_model.CpModel()
    matrix = [[model.new_bool_var(f"matrix_{i}_{j}") for j in range(n)] for i in range(n)]
    for i in range(n):
        # No isolated vertex, and every degree is a multiple of three.
        degree = model.new_int_var(1, n, f"degree_{i}")
        model.add(degree == sum(matrix[i]))
        multiple = model.new_int_var(1, n // 3, f"degree_third_{i}")
        model.add(degree == 3 * multiple)
        # No self loop, and the graph is undirected.
        model.add(matrix[i][i] == 0)
        for j in range(i + 1, n):
            model.add(matrix[i][j] == matrix[j][i])
    edges = model.new_int_var(0, n * n // 12, "edge_twelfths")
    model.add(sum(cell for row in matrix for cell in row) == 12 * edges)
    # Diamond-free: any four vertices span at most four of their six edges.
    for a, b, c, d in itertools.combinations(range(n), 4):
        model.add(matrix[a][b] + matrix[a][c] + matrix[a][d]
                  + matrix[b][c] + matrix[b][d] + matrix[c][d] <= 4)
    return model, {"matrix": matrix}
