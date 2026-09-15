import cpmpy as cp


def build(instance):
    """Heterosquare: an n by n square of the distinct integers 1..n^2 whose
    row, column and diagonal sums are all different from each other.
    """
    n = instance["n"]

    x = cp.intvar(1, n * n, shape=(n, n), name="x")
    row_sums = cp.intvar(1, n ** 3, shape=n, name="row_sums")
    col_sums = cp.intvar(1, n ** 3, shape=n, name="col_sums")
    diag1 = cp.intvar(1, n ** 3, name="diag1")
    diag2 = cp.intvar(1, n ** 3, name="diag2")

    model = cp.Model(cp.AllDifferent(x))

    all_sums = list(row_sums) + list(col_sums) + [diag1, diag2]
    model += cp.AllDifferent(all_sums)

    for i in range(n):
        model += row_sums[i] == cp.sum(x[i, :])
    for j in range(n):
        model += col_sums[j] == cp.sum(x[:, j])
    model += cp.sum([x[i, i] for i in range(n)]) == diag1
    model += cp.sum([x[i, n - i - 1] for i in range(n)]) == diag2

    return model, {"x": x}
