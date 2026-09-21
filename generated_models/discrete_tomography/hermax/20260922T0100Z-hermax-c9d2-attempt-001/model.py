# Reconstruct a 0/1 matrix from its row and column sums.
from dcp_maxsat import MaxSat


def build(instance):
    row_sums = instance["row_sums"]
    col_sums = instance["col_sums"]
    rows, cols = len(row_sums), len(col_sums)

    sat = MaxSat()
    matrix = sat.int_grid(rows, cols, 0, 1)
    for i in range(rows):
        sat.sum_eq(matrix[i], row_sums[i])
    for j in range(cols):
        sat.sum_eq([matrix[i][j] for i in range(rows)], col_sums[j])
    return sat, {"matrix": matrix}
