# Flip rows and columns (Einav's puzzle): choose, for every row and column,
# whether to flip its sign so that every row sum and every column sum is
# non-negative, with the smallest possible total of the whole matrix.
from pychoco.model import Model


def build(instance):
    matrix = instance["input_matrix"]
    rows, cols = len(matrix), len(matrix[0])

    model = Model()

    # the signs of the rows and columns: -1 (flipped) or +1, never 0
    row_signs = [model.intvar([-1, 1], name=f"row_sign_{i}") for i in range(rows)]
    col_signs = [model.intvar([-1, 1], name=f"col_sign_{j}") for j in range(cols)]

    # cell_sign[i][j] = sign of cell (i, j) after both flips = row sign * column sign
    cell_sign = [[model.intvar([-1, 1], name=f"cell_sign_{i}_{j}") for j in range(cols)] for i in range(rows)]
    for i in range(rows):
        for j in range(cols):
            model.times(row_signs[i], col_signs[j], cell_sign[i][j]).post()

    # every row and column sums to at least 0; the reference's declared
    # domain for a sum is 0..300, which is mirrored here
    for i in range(rows):
        row_sum = model.intvar(0, 300, name=f"row_sum_{i}")
        model.scalar(cell_sign[i], matrix[i], "=", row_sum).post()
    for j in range(cols):
        col_sum = model.intvar(0, 300, name=f"col_sum_{j}")
        model.scalar([cell_sign[i][j] for i in range(rows)], [matrix[i][j] for i in range(rows)], "=", col_sum).post()

    # total sum of the flipped matrix, to be minimised (declared range 0..1000)
    total_sum = model.intvar(0, 1000, name="total_sum")
    model.scalar(
        [cell_sign[i][j] for i in range(rows) for j in range(cols)],
        [matrix[i][j] for i in range(rows) for j in range(cols)],
        "=",
        total_sum,
    ).post()

    return model, {"row_signs": row_signs, "col_signs": col_signs}, ("minimize", total_sum)
