# Heterosquare of order n: an n*n square whose elements are distinct integers from
# 1 to n^2 such that the sums of the rows, columns and diagonals are all different.
# Output x is the square as a list of lists of integers. Satisfaction problem.
import mip


def build(instance):
    n = instance["n"]
    cells = n * n
    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    x = [[m.add_var(f"x_{i}_{j}", lb=1, ub=cells, var_type=mip.INTEGER)
          for j in range(n)] for i in range(n)]
    # p[i][j][v] = 1 when cell (i, j) holds the value v + 1
    p = [[[m.add_var(f"p_{i}_{j}_{v}", var_type=mip.BINARY)
           for v in range(cells)] for j in range(n)] for i in range(n)]

    # elements are distinct integers from 1 to n^2
    for i in range(n):
        for j in range(n):
            m += mip.xsum(p[i][j]) == 1
            m += x[i][j] == mip.xsum((v + 1) * p[i][j][v] for v in range(cells))
    for v in range(cells):
        m += mip.xsum(p[i][j][v] for i in range(n) for j in range(n)) == 1

    # the sums of the rows, columns and diagonals
    sums = []
    for i in range(n):
        sums.append(mip.xsum(x[i][j] for j in range(n)))
    for j in range(n):
        sums.append(mip.xsum(x[i][j] for i in range(n)))
    sums.append(mip.xsum(x[i][i] for i in range(n)))
    sums.append(mip.xsum(x[i][n - 1 - i] for i in range(n)))

    # every sum is between the smallest and largest possible sum of n distinct values in 1..n^2
    lo = n * (n + 1) // 2
    hi = n * cells - n * (n - 1) // 2
    big = hi - lo + 1

    # the sums of the rows, columns and diagonals are all different
    for a in range(len(sums)):
        for c in range(a + 1, len(sums)):
            side = m.add_var(f"side_{a}_{c}", var_type=mip.BINARY)
            m += sums[a] - sums[c] <= -1 + big * side
            m += sums[a] - sums[c] >= 1 - big * (1 - side)

    return m, {"x": x}
