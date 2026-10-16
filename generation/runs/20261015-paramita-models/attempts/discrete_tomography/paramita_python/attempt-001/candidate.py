# Discrete tomography: reconstruct a 0/1 matrix from its row and column sums.
# Each cell is one Bool. The row and column sums are plain PB constraints over
# those Bools, so no integer encoding is needed.
from paramita.modelling import Bool


def build(instance):
    row_sums = instance["row_sums"]
    col_sums = instance["col_sums"]
    rows, cols = len(row_sums), len(col_sums)

    x = [[Bool(f"x_{i}_{j}") for j in range(cols)] for i in range(rows)]

    cons = []

    # each row contains as many ones as its horizontal x-ray says
    for i in range(rows):
        cons.append(sum(x[i]) == row_sums[i])

    # each column contains as many ones as its vertical x-ray says
    for j in range(cols):
        cons.append(sum(x[i][j] for i in range(rows)) == col_sums[j])

    # print the solution matrix with 0 and 1: each cell as an integer 0 or 1
    matrix = [[1 * x[i][j] for j in range(cols)] for i in range(rows)]
    return cons, {"matrix": matrix}
