"""Flip rows and columns: choose a sign (+1 or -1) for every row and every column of a matrix,
each entry being multiplied by its row's and its column's sign, so that every row sum and
every column sum is non-negative and the total sum is as small as possible.

The model reports the row signs and the column signs.
"""
from docplex.mp.model import Model


def build(instance):
    matrix = instance["input_matrix"]  # the input matrix
    rows = range(len(matrix))
    cols = range(len(matrix[0]))

    # Bounds the reference gives its sums: row and column sums in 0..300, the total in 0..1000.
    sum_cap = 300
    total_cap = 1000

    model = Model("flip_rows_cols")

    # row_up[i] is 1 when row i keeps its sign (+1) and 0 when it is flipped (-1); col_up[j]
    # likewise for column j. A sign is never 0.
    row_up = [model.binary_var(name=f"row_up_{i}") for i in rows]
    col_up = [model.binary_var(name=f"col_up_{j}") for j in cols]
    row_signs = [2 * row_up[i] - 1 for i in rows]
    col_signs = [2 * col_up[j] - 1 for j in cols]

    # Each entry is the input entry times its row sign times its column sign. The product of
    # the two signs is 4 * both - 2 * row_up - 2 * col_up + 1, where both[i, j] is the product
    # row_up[i] * col_up[j], pinned down by three linear constraints (a product of two
    # variables would be a non-convex quadratic constraint, which CPLEX refuses).
    both = {}
    for i in rows:
        for j in cols:
            both[i, j] = model.continuous_var(0, 1, name=f"both_{i}_{j}")
            model.add_constraint(both[i, j] <= row_up[i])
            model.add_constraint(both[i, j] <= col_up[j])
            model.add_constraint(both[i, j] >= row_up[i] + col_up[j] - 1)
    x = {(i, j): matrix[i][j] * (4 * both[i, j] - 2 * row_up[i] - 2 * col_up[j] + 1)
         for i in rows for j in cols}

    # Every row sum and every column sum is non-negative (and within the reference's bound).
    for i in rows:
        model.add_range(0, model.sum(x[i, j] for j in cols), sum_cap)
    for j in cols:
        model.add_range(0, model.sum(x[i, j] for i in rows), sum_cap)

    # The total sum, to be minimised.
    total_sum = model.sum(x.values())
    model.add_range(0, total_sum, total_cap)
    model.minimize(total_sum)

    return model, {"row_signs": row_signs, "col_signs": col_signs}
