# Magic square: fill an n x n grid with the distinct integers 1..n^2 so that every row, every
# column and both diagonals add up to the same sum.
import cpmpy as cp


def build(instance):
    n = instance["n"]

    # The common sum is fixed by the numbers used: n * (n^2 + 1) / 2 (the total of 1..n^2 is
    # n^2 * (n^2 + 1) / 2, shared between n rows).
    magic_sum = n * (n ** 2 + 1) // 2

    # square[i, j] = the number in row i, column j
    square = cp.intvar(1, n ** 2, shape=(n, n), name="square")

    model = cp.Model()

    # All numbers in the square are different.
    model += cp.AllDifferent(square)

    # Every row adds up to the magic sum.
    for i in range(n):
        model += cp.sum(square[i, :]) == magic_sum

    # Every column adds up to the magic sum.
    for j in range(n):
        model += cp.sum(square[:, j]) == magic_sum

    # The main diagonal adds up to the magic sum.
    model += cp.sum([square[i, i] for i in range(n)]) == magic_sum

    # The other diagonal adds up to the magic sum.
    model += cp.sum([square[i, n - 1 - i] for i in range(n)]) == magic_sum

    return model, {"square": square}
