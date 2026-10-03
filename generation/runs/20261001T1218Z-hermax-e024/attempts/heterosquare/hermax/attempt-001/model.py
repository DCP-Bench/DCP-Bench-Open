# Heterosquare: fill an n x n square with the distinct integers 1..n^2 so that
# the n row sums, the n column sums and the two diagonal sums are all different.
from hermax.model import Model


def build(instance):
    n = instance["n"]  # order of the square

    m = Model()
    # x[i][j] = the entry in row i, column j; all entries are different
    x = m.int_matrix("x", n, n, 1, n * n)
    m &= x.flatten().all_different()

    # The line sums. Their range is bounded by the smallest and the largest sum
    # of n distinct numbers from 1..n^2; keeping it that narrow keeps the integer
    # encoding small.
    low = n * (n + 1) // 2
    high = sum(range(n * n - n + 1, n * n + 1))
    row_sums = m.int_vector("row_sums", n, low, high)
    col_sums = m.int_vector("col_sums", n, low, high)
    diag1 = m.int("diag1", low, high)
    diag2 = m.int("diag2", low, high)

    for i in range(n):
        m &= (sum(x[i][j] for j in range(n)) == row_sums[i])  # row i adds up to row_sums[i]
        m &= (sum(x[j][i] for j in range(n)) == col_sums[i])  # column i adds up to col_sums[i]
    m &= (sum(x[i][i] for i in range(n)) == diag1)  # main diagonal
    m &= (sum(x[i][n - i - 1] for i in range(n)) == diag2)  # anti-diagonal

    # all row, column and diagonal sums are different from each other
    sums = [row_sums[i] for i in range(n)] + [col_sums[i] for i in range(n)] + [diag1, diag2]
    for a in range(len(sums)):
        for b in range(a + 1, len(sums)):
            m &= (sums[a] != sums[b])

    return m, {"x": x}
