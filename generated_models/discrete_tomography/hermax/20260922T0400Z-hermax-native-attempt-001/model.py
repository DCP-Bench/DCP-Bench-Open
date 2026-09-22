# Reconstruct a 0/1 matrix from its row and column sums.
from hermax.model import Model


def build(instance):
    row_sums = instance["row_sums"]
    col_sums = instance["col_sums"]
    rows, cols = len(row_sums), len(col_sums)

    m = Model()
    # 0/1 integers rather than Booleans: the brief declares integers.
    matrix = m.int_matrix("matrix", rows, cols, 0, 1)
    for i in range(rows):
        m &= (sum(matrix[i][j] for j in range(cols)) == row_sums[i])
    for j in range(cols):
        m &= (sum(matrix[i][j] for i in range(rows)) == col_sums[j])
    return m, {"matrix": matrix}
