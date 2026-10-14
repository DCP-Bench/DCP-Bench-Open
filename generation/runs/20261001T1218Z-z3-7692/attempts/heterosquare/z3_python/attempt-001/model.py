# Heterosquare: fill an n x n square with the distinct integers 1 to n^2 so that the sums of
# the rows, of the columns and of the two diagonals are all different from each other.
import z3


def build(instance):
    n = instance["n"]  # order of the square

    # x[i][j] is the number in row i, column j; the numbers are 1..n^2.
    x = [[z3.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    # Sums of the rows, of the columns and of the two diagonals. The reference lets each
    # sum range over 1..n^3.
    row_sums = [z3.Int(f"row_sums_{i}") for i in range(n)]
    col_sums = [z3.Int(f"col_sums_{j}") for j in range(n)]
    diag1 = z3.Int("diag1")
    diag2 = z3.Int("diag2")

    solver = z3.Solver()

    for i in range(n):
        for j in range(n):
            solver.add(x[i][j] >= 1, x[i][j] <= n * n)
    for s in row_sums + col_sums + [diag1, diag2]:
        solver.add(s >= 1, s <= n ** 3)

    # All the entries of the square are different.
    solver.add(z3.Distinct([x[i][j] for i in range(n) for j in range(n)]))

    # All the sums are different.
    solver.add(z3.Distinct(row_sums + col_sums + [diag1, diag2]))

    # Row sums, column sums and the sums of the main diagonal and the anti-diagonal.
    for i in range(n):
        solver.add(row_sums[i] == z3.Sum(x[i]))
    for j in range(n):
        solver.add(col_sums[j] == z3.Sum([x[i][j] for i in range(n)]))
    solver.add(diag1 == z3.Sum([x[i][i] for i in range(n)]))
    solver.add(diag2 == z3.Sum([x[i][n - i - 1] for i in range(n)]))

    return solver, {"x": x}
