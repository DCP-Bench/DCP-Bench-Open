# Discrete tomography: a matrix of zeroes and ones is x-rayed by its row sums and
# column sums (the number of ones in each row and each column). Reconstruct the matrix.
import cvc5.pythonic as cz


def build(instance):
    row_sums = instance["row_sums"]
    col_sums = instance["col_sums"]
    n_rows = len(row_sums)
    n_cols = len(col_sums)

    # the matrix, one integer cell per position (the sizes come from this instance)
    matrix = [[cz.Int(f"m_{i}_{j}") for j in range(n_cols)] for i in range(n_rows)]
    constraints = []

    # the matrix contains only zeroes and ones
    for i in range(n_rows):
        for j in range(n_cols):
            constraints.append(matrix[i][j] >= 0)
            constraints.append(matrix[i][j] <= 1)

    # the number of ones in each row is the row's x-ray value
    for i in range(n_rows):
        constraints.append(cz.Sum([matrix[i][j] for j in range(n_cols)]) == row_sums[i])

    # the number of ones in each column is the column's x-ray value
    for j in range(n_cols):
        constraints.append(cz.Sum([matrix[i][j] for i in range(n_rows)]) == col_sums[j])

    return constraints, {"matrix": matrix}
