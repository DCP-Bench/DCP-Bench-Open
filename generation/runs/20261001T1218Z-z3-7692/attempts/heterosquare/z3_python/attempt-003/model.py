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
    all_sums = row_sums + col_sums + [diag1, diag2]

    solver = z3.Solver()

    for i in range(n):
        for j in range(n):
            solver.add(x[i][j] >= 1, x[i][j] <= n * n)

    # All the entries of the square are different. As the n^2 entries take values among 1..n^2,
    # this says that every value 1..n^2 is used by exactly one entry. It is stated as a
    # pseudo-Boolean equality over "this entry holds this value" tests, which Z3 reasons about
    # far better than n^4 pairwise inequalities between integers.
    for v in range(1, n * n + 1):
        solver.add(z3.PbEq([(x[i][j] == v, 1) for i in range(n) for j in range(n)], 1))

    # Row sums, column sums and the sums of the main diagonal and the anti-diagonal.
    for i in range(n):
        solver.add(row_sums[i] == z3.Sum(x[i]))
    for j in range(n):
        solver.add(col_sums[j] == z3.Sum([x[i][j] for i in range(n)]))
    solver.add(diag1 == z3.Sum([x[i][i] for i in range(n)]))
    solver.add(diag2 == z3.Sum([x[i][n - i - 1] for i in range(n)]))

    # The reference's domain for a sum is 1..n^3. Tighter bounds follow from the entries
    # being different: n entries sum to at least 1 + ... + n and at most
    # n^2 + (n^2 - 1) + ... + (n^2 - n + 1).
    low = n * (n + 1) // 2
    high = n * n * n - n * (n - 1) // 2
    for s in all_sums:
        solver.add(s >= low, s <= high)

    # All the sums are different.
    solver.add(z3.Distinct(all_sums))

    return solver, {"x": x}
