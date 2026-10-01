# Flip rows and columns: choose a sign (+1 or -1) for every row and every column of a
# number matrix, flipping the signs of the entries accordingly, so that every row and
# every column of the flipped matrix sums to zero or more, and the total sum of the
# flipped matrix is as small as possible.
import cpmpy as cp


def build(instance):
    matrix = instance["input_matrix"]
    rows = len(matrix)
    cols = len(matrix[0])

    # Bounds derived from the data: no entry, row sum, column sum or total can exceed
    # the sum of the absolute values of the entries.
    total_abs = sum(abs(v) for row in matrix for v in row)
    max_abs = max(abs(v) for row in matrix for v in row)

    # Sign chosen for each row and each column. The domain is -1..1 and 0 is removed below.
    row_signs = cp.intvar(-1, 1, shape=rows, name="row_signs")
    col_signs = cp.intvar(-1, 1, shape=cols, name="col_signs")

    # x[i][j] is the entry (i, j) after flipping.
    x = cp.intvar(-max_abs, max_abs, shape=(rows, cols), name="x")
    # Sums of the flipped rows and columns; their domain starts at 0, so they must not be negative.
    row_sums = cp.intvar(0, total_abs, shape=rows, name="row_sums")
    col_sums = cp.intvar(0, total_abs, shape=cols, name="col_sums")
    # Total sum of the flipped matrix, to be minimised.
    total_sum = cp.intvar(0, total_abs, name="total_sum")

    model = cp.Model()

    # A sign is -1 or +1, never 0.
    for i in range(rows):
        model += row_signs[i] != 0
    for j in range(cols):
        model += col_signs[j] != 0

    # The flipped entry is the original entry times its row sign times its column sign.
    for i in range(rows):
        for j in range(cols):
            model += x[i, j] == matrix[i][j] * row_signs[i] * col_signs[j]

    # The total of the flipped matrix.
    model += total_sum == cp.sum(x)

    # Every flipped row sums to zero or more.
    for i in range(rows):
        model += row_sums[i] == cp.sum(x[i, :])

    # Every flipped column sums to zero or more.
    for j in range(cols):
        model += col_sums[j] == cp.sum(x[:, j])

    # Find the flip with the smallest total sum.
    model.minimize(total_sum)

    return model, {"row_signs": row_signs, "col_signs": col_signs}
