# Magic square: fill an n x n grid with the different integers 1..n^2 so that
# every row, every column and both diagonals add up to the same sum.
from hermax.model import Model


def build(instance):
    n = instance["n"]  # side of the square
    magic_sum = n * (n * n + 1) // 2  # the sum every line has to reach

    m = Model()
    # square[i][j] = the number in cell (i, j)
    square = m.int_matrix("square", n, n, 1, n * n)

    # all numbers are different
    m &= m.vector([square[i][j] for i in range(n) for j in range(n)]).all_different()

    # each row and each column adds up to the magic sum
    for i in range(n):
        m &= (sum(square[i][j] for j in range(n)) == magic_sum)
        m &= (sum(square[j][i] for j in range(n)) == magic_sum)
    # both diagonals add up to the magic sum
    m &= (sum(square[i][i] for i in range(n)) == magic_sum)
    m &= (sum(square[i][n - 1 - i] for i in range(n)) == magic_sum)

    return m, {"square": square}
