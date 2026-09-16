from pychoco.model import Model


def build(instance):
    """Discrete tomography: reconstruct a 0/1 picture from its row and column
    sums.
    """
    row_sums = instance["row_sums"]
    col_sums = instance["col_sums"]
    rows = len(row_sums)
    cols = len(col_sums)

    model = Model()
    matrix = [[model.intvar(0, 1, name=f"m{i}_{j}") for j in range(cols)]
              for i in range(rows)]

    for i in range(rows):
        model.sum(matrix[i], "=", row_sums[i]).post()
    for j in range(cols):
        model.sum([matrix[i][j] for i in range(rows)], "=", col_sums[j]).post()

    return model, {"matrix": matrix}
