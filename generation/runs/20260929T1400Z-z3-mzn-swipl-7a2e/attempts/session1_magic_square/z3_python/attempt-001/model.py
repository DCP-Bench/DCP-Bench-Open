# Magic square: fill an n x n grid with the different integers 1..n^2 so that
# every row, every column and both diagonals add up to the same sum.
import z3


def build(instance):
    n = instance["n"]  # side of the square
    magic_sum = n * (n * n + 1) // 2  # the sum every line has to reach

    solver = z3.Solver()

    # square[i][j] = the number in cell (i, j)
    square = [[z3.Int(f"square_{i}_{j}") for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.add(square[i][j] >= 1, square[i][j] <= n * n)

    # all numbers are different
    solver.add(z3.Distinct([square[i][j] for i in range(n) for j in range(n)]))

    # each row adds up to the magic sum
    for i in range(n):
        solver.add(z3.Sum(square[i]) == magic_sum)
    # each column adds up to the magic sum
    for j in range(n):
        solver.add(z3.Sum([square[i][j] for i in range(n)]) == magic_sum)
    # the main diagonal adds up to the magic sum
    solver.add(z3.Sum([square[i][i] for i in range(n)]) == magic_sum)
    # the other diagonal adds up to the magic sum
    solver.add(z3.Sum([square[i][n - 1 - i] for i in range(n)]) == magic_sum)

    return solver, {"square": square}
