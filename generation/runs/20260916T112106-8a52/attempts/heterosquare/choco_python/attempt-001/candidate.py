from pychoco.model import Model


def build(instance):
    """Heterosquare: an n by n square of the distinct integers 1..n^2 whose
    row, column and diagonal sums are all different from each other.
    """
    n = instance["n"]

    model = Model()
    x = [[model.intvar(1, n * n, name=f"x{i}_{j}") for j in range(n)]
         for i in range(n)]
    model.all_different([cell for row in x for cell in row]).post()

    row_sums = [model.intvar(1, n ** 3, name=f"row{i}") for i in range(n)]
    col_sums = [model.intvar(1, n ** 3, name=f"col{j}") for j in range(n)]
    diag1 = model.intvar(1, n ** 3, name="diag1")
    diag2 = model.intvar(1, n ** 3, name="diag2")

    for i in range(n):
        model.sum(x[i], "=", row_sums[i]).post()
        model.sum([x[k][i] for k in range(n)], "=", col_sums[i]).post()
    model.sum([x[i][i] for i in range(n)], "=", diag1).post()
    model.sum([x[i][n - i - 1] for i in range(n)], "=", diag2).post()

    model.all_different(row_sums + col_sums + [diag1, diag2]).post()

    return model, {"x": x}
