# Heterosquare: fill an n x n square with the distinct integers 1..n^2 so that
# the n row sums, the n column sums and the two diagonal sums are all different.
from hermax.model import Model


def build(instance):
    n = instance["n"]  # order of the square

    m = Model()
    # x[i][j] = the entry in row i, column j; all entries are different
    x = m.int_matrix("x", n, n, 1, n * n)
    m &= x.flatten().all_different()

    # The line sums. m.sum_var adds integers through narrow partial sums, which
    # is much cheaper to encode than one equation over seven or more wide integers.
    row_sums = [m.sum_var([x[i][j] for j in range(n)]) for i in range(n)]  # row i
    col_sums = [m.sum_var([x[j][i] for j in range(n)]) for i in range(n)]  # column i
    diag1 = m.sum_var([x[i][i] for i in range(n)])  # main diagonal
    diag2 = m.sum_var([x[i][n - i - 1] for i in range(n)])  # anti-diagonal

    # all row, column and diagonal sums are different from each other
    sums = row_sums + col_sums + [diag1, diag2]
    for a in range(len(sums)):
        for b in range(a + 1, len(sums)):
            m &= (sums[a] != sums[b])

    return m, {"x": x}
