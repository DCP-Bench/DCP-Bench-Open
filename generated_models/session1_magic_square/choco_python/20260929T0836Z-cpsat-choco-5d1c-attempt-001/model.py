# Magic square: fill an n x n grid with the different integers 1..n^2 so that
# every row, every column and both diagonals add up to the same sum.
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # side of the square
    magic_sum = n * (n * n + 1) // 2  # the sum every line has to reach

    model = Model()

    # square[i][j] = the number in cell (i, j)
    square = [[model.intvar(1, n * n, name=f"square_{i}_{j}") for j in range(n)] for i in range(n)]

    # all numbers are different
    model.all_different([square[i][j] for i in range(n) for j in range(n)]).post()

    # each row adds up to the magic sum
    for i in range(n):
        model.sum(square[i], "=", magic_sum).post()
    # each column adds up to the magic sum
    for j in range(n):
        model.sum([square[i][j] for i in range(n)], "=", magic_sum).post()
    # the main diagonal adds up to the magic sum
    model.sum([square[i][i] for i in range(n)], "=", magic_sum).post()
    # the other diagonal adds up to the magic sum
    model.sum([square[i][n - 1 - i] for i in range(n)], "=", magic_sum).post()

    return model, {"square": square}
