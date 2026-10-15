# Flip the signs of whole rows and columns of an integer matrix so that every
# row and every column sums to a positive number or zero, and minimise the
# overall sum of the resulting matrix.
from paramita.modelling import Bool, Iff


def build(instance):
    a = instance["input_matrix"]  # the input array, read from the instance
    n_rows = len(a)
    n_cols = len(a[0])

    # flip the sign of entire rows and columns: R[i] = 1 when row i is flipped, C[j] = 1 when column j is flipped
    R = [Bool(f"row_flip_{i}") for i in range(n_rows)]
    C = [Bool(f"col_flip_{j}") for j in range(n_cols)]

    # the sign of a cell changes when exactly one of its row and column is flipped
    X = [[Bool(f"cell_flip_{i}_{j}") for j in range(n_cols)] for i in range(n_rows)]
    cons = []
    # cell (i, j) is negated exactly when row i xor column j is flipped
    for i in range(n_rows):
        for j in range(n_cols):
            cons.append(Iff(X[i][j], R[i] + C[j] == 1))

    # the value of cell (i, j) after flipping is a[i][j] * (1 - 2 * X[i][j]), linear in X
    def signed(i, j):
        return a[i][j] - 2 * a[i][j] * X[i][j]

    # all the rows sum to positive numbers (or zero)
    for i in range(n_rows):
        cons.append(sum(signed(i, j) for j in range(n_cols)) >= 0)

    # all the columns sum to positive numbers (or zero)
    for j in range(n_cols):
        cons.append(sum(signed(i, j) for i in range(n_rows)) >= 0)

    # minimise the overall sum of the signed matrix
    total = sum(signed(i, j) for i in range(n_rows) for j in range(n_cols))

    row_signs = [1 - 2 * R[i] for i in range(n_rows)]
    col_signs = [1 - 2 * C[j] for j in range(n_cols)]
    return cons, {"row_signs": row_signs, "col_signs": col_signs}, ("minimize", total)
