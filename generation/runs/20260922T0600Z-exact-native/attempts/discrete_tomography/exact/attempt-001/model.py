# Reconstruct a 0/1 matrix from its row and column sums.
from exact import Exact


def build(instance):
    row_sums = instance["row_sums"]
    col_sums = instance["col_sums"]
    rows, cols = len(row_sums), len(col_sums)

    solver = Exact()
    # 0/1 integers rather than Booleans: the brief declares integers.
    matrix = [[f"m{i}_{j}" for j in range(cols)] for i in range(rows)]
    for row in matrix:
        for name in row:
            solver.addVariable(name, 0, 1)
    for i in range(rows):
        solver.addConstraint([(1, name) for name in matrix[i]],
                             True, row_sums[i], True, row_sums[i])
    for j in range(cols):
        solver.addConstraint([(1, matrix[i][j]) for i in range(rows)],
                             True, col_sums[j], True, col_sums[j])
    return solver, {"matrix": matrix}
