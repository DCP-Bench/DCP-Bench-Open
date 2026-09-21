# Reconstruct a 0/1 matrix from its row and column sums.
from dcp_pb import Pb


def build(instance):
    row_sums = instance["row_sums"]
    col_sums = instance["col_sums"]
    rows, cols = len(row_sums), len(col_sums)

    pb = Pb()
    # 0/1 integers rather than booleans: the brief declares integers.
    matrix = pb.int_grid(rows, cols, 0, 1)
    for i in range(rows):
        pb.sum_eq(matrix[i], row_sums[i])
    for j in range(cols):
        pb.sum_eq([matrix[i][j] for i in range(rows)], col_sums[j])
    return pb, {"matrix": matrix}
