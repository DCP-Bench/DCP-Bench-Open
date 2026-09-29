# Magic square: fill an n x n grid with the different integers 1..n^2 so that
# every row, every column and both diagonals add up to the same sum.
from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]  # side of the square
    magic_sum = n * (n * n + 1) // 2  # the sum every line has to reach

    model = cp_model.CpModel()

    # square[i][j] = the number in cell (i, j)
    square = [[model.new_int_var(1, n * n, f"square_{i}_{j}") for j in range(n)] for i in range(n)]

    # all numbers are different
    model.add_all_different([square[i][j] for i in range(n) for j in range(n)])

    # each row adds up to the magic sum
    for i in range(n):
        model.add(sum(square[i]) == magic_sum)
    # each column adds up to the magic sum
    for j in range(n):
        model.add(sum(square[i][j] for i in range(n)) == magic_sum)
    # the main diagonal adds up to the magic sum
    model.add(sum(square[i][i] for i in range(n)) == magic_sum)
    # the other diagonal adds up to the magic sum
    model.add(sum(square[i][n - 1 - i] for i in range(n)) == magic_sum)

    return model, {"square": square}
