# Heterosquare: fill an n x n square with the distinct integers 1..n^2 so that the sums of the n
# rows, the n columns and the two diagonals are all different.
from exact import Exact


def build(instance):
    n = instance["n"]
    cells = n * n

    solver = Exact()

    # x[i][j] is the number in row i, column j
    x = [[f"x_{i}_{j}" for j in range(n)] for i in range(n)]
    # holds[i][j][v] = 1 when cell (i, j) holds the number v. Exact has no all-different
    # constraint, so the entries are made distinct through these indicators.
    holds = [[[f"cell_{i}_{j}_holds_{v}" for v in range(1, cells + 1)] for j in range(n)]
             for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(x[i][j], 1, cells)
            for name in holds[i][j]:
                solver.addVariable(name, 0, 1)
            # every cell holds one number, and x[i][j] is that number
            solver.addConstraint([(1, name) for name in holds[i][j]], True, 1, True, 1)
            solver.addConstraint([(v, holds[i][j][v - 1]) for v in range(1, cells + 1)] + [(-1, x[i][j])],
                                 True, 0, True, 0)
    # all the entries are different: each number 1..n^2 is in at most one cell (hence exactly one)
    for v in range(cells):
        solver.addConstraint([(1, holds[i][j][v]) for i in range(n) for j in range(n)], False, 0, True, 1)

    # The line sums: n rows, n columns and the two diagonals. A sum of n distinct entries lies
    # between 1 + ... + n and (n^2 - n + 1) + ... + n^2; this narrows the reference's 1..n^3.
    low = n * (n + 1) // 2
    high = n * cells - n * (n - 1) // 2
    lines = [[(1, x[i][j]) for j in range(n)] for i in range(n)]  # rows
    lines += [[(1, x[i][j]) for i in range(n)] for j in range(n)]  # columns
    lines.append([(1, x[i][i]) for i in range(n)])  # diagonal
    lines.append([(1, x[i][n - i - 1]) for i in range(n)])  # anti-diagonal
    sums = [f"line_sum_{k}" for k in range(len(lines))]
    for name, line in zip(sums, lines):
        solver.addVariable(name, low, high)
        solver.addConstraint(line + [(-1, name)], True, 0, True, 0)

    # all the line sums are different. The sums have a wide range, so instead of one indicator per
    # value, each pair of sums gets one Boolean saying which of the two is larger.
    big_m = high - low + 1
    for a in range(len(sums)):
        for b in range(a + 1, len(sums)):
            larger = f"sum_{a}_exceeds_{b}"
            solver.addVariable(larger, 0, 1)
            # larger = 1  ->  sum a >= sum b + 1
            solver.addConstraint([(1, sums[a]), (-1, sums[b]), (-big_m, larger)], True, 1 - big_m)
            # larger = 0  ->  sum b >= sum a + 1
            solver.addConstraint([(1, sums[b]), (-1, sums[a]), (big_m, larger)], True, 1)

    return solver, {"x": x}
