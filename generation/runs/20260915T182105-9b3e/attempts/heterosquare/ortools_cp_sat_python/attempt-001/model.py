from ortools.sat.python import cp_model


def build(instance):
    """Heterosquare: an n by n square of the distinct integers 1..n^2 whose
    row, column and diagonal sums are all different from each other.
    """
    n = instance["n"]

    model = cp_model.CpModel()
    x = [[model.new_int_var(1, n * n, f"x{i}_{j}") for j in range(n)]
         for i in range(n)]
    row_sums = [model.new_int_var(1, n ** 3, f"row{i}") for i in range(n)]
    col_sums = [model.new_int_var(1, n ** 3, f"col{j}") for j in range(n)]
    diag1 = model.new_int_var(1, n ** 3, "diag1")
    diag2 = model.new_int_var(1, n ** 3, "diag2")

    model.add_all_different([cell for row in x for cell in row])
    model.add_all_different(row_sums + col_sums + [diag1, diag2])

    for i in range(n):
        model.add(row_sums[i] == sum(x[i]))
    for j in range(n):
        model.add(col_sums[j] == sum(x[i][j] for i in range(n)))
    model.add(sum(x[i][i] for i in range(n)) == diag1)
    model.add(sum(x[i][n - i - 1] for i in range(n)) == diag2)

    return model, {"x": x}
