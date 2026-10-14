# Flip rows and columns (Einav's puzzle): choose, for every row and column,
# whether to flip its sign so that every row sum and every column sum is
# non-negative, with the smallest possible total of the whole matrix.
from ortools.sat.python import cp_model


def build(instance):
    matrix = instance["input_matrix"]
    rows, cols = len(matrix), len(matrix[0])

    model = cp_model.CpModel()

    # row_flipped[i] / col_flipped[j] is true when that row / column has its sign flipped
    row_flipped = [model.new_bool_var(f"row_flipped_{i}") for i in range(rows)]
    col_flipped = [model.new_bool_var(f"col_flipped_{j}") for j in range(cols)]
    # the signs themselves, -1 or +1 (never 0): reported as the outputs
    row_signs = [model.new_int_var_from_domain(cp_model.Domain.from_values([-1, 1]), f"row_sign_{i}") for i in range(rows)]
    col_signs = [model.new_int_var_from_domain(cp_model.Domain.from_values([-1, 1]), f"col_sign_{j}") for j in range(cols)]
    for i in range(rows):
        model.add(row_signs[i] == 1 - 2 * row_flipped[i])
    for j in range(cols):
        model.add(col_signs[j] == 1 - 2 * col_flipped[j])

    # x[i][j] = input value after both flips. A cell changes sign exactly when
    # its row or its column (not both) is flipped.
    x = [[None] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            cell_flipped = model.new_bool_var(f"cell_flipped_{i}_{j}")
            model.add_bool_xor([row_flipped[i], col_flipped[j], cell_flipped.negated()])
            x[i][j] = model.new_int_var(-100, 100, f"x_{i}_{j}")
            model.add(x[i][j] == matrix[i][j] * (1 - 2 * cell_flipped))

    # every row and column sums to at least 0; the reference's declared
    # domain for a sum is 0..300, which is mirrored here
    for i in range(rows):
        model.add(sum(x[i]) >= 0)
        model.add(sum(x[i]) <= 300)
    for j in range(cols):
        model.add(sum(x[i][j] for i in range(rows)) >= 0)
        model.add(sum(x[i][j] for i in range(rows)) <= 300)

    # total sum of the flipped matrix, to be minimised (declared range 0..1000)
    total_sum = model.new_int_var(0, 1000, "total_sum")
    model.add(total_sum == sum(sum(row) for row in x))
    model.minimize(total_sum)

    return model, {"row_signs": row_signs, "col_signs": col_signs}
