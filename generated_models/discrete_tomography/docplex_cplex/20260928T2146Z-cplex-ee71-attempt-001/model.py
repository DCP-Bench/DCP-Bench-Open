"""Discrete tomography: rebuild a 0/1 matrix from the number of ones in each row and each column."""
from docplex.mp.model import Model


def build(instance):
    row_sums = instance["row_sums"]
    col_sums = instance["col_sums"]
    rows = range(len(row_sums))
    cols = range(len(col_sums))

    model = Model("discrete_tomography")

    # matrix[i, j] is the 0/1 entry in row i, column j.
    matrix = model.binary_var_matrix(rows, cols, name="matrix")

    # Each row holds as many ones as its x-ray says.
    for i in rows:
        model.add_constraint(model.sum(matrix[i, j] for j in cols) == row_sums[i], ctname=f"row_{i}")

    # Each column holds as many ones as its x-ray says.
    for j in cols:
        model.add_constraint(model.sum(matrix[i, j] for i in rows) == col_sums[j], ctname=f"col_{j}")

    return model, {"matrix": [[matrix[i, j] for j in cols] for i in rows]}
