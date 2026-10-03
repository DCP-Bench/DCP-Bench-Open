"""Heterosquare: fill an n x n square with the distinct integers 1..n^2 so that the sums of
the n rows, the n columns and the two diagonals are all different from each other.

The model reports the square.
"""
import pulp


def build(instance):
    n = instance["n"]  # order of the square
    cells = n * n  # the entries are the numbers 1..cells

    problem = pulp.LpProblem("heterosquare", pulp.LpMinimize)  # satisfaction: no objective

    # put[r][c][v] = 1 if the cell in row r, column c holds the number v + 1. All the
    # entries are different and there are as many numbers as cells, so every number is
    # used exactly once. x reads the number of a cell back.
    put = pulp.LpVariable.dicts("put", (range(n), range(n), range(cells)), cat="Binary")
    x = [[pulp.LpVariable(f"x_{r}_{c}", 1, cells, cat="Integer") for c in range(n)]
         for r in range(n)]
    for r in range(n):
        for c in range(n):
            problem += pulp.lpSum(put[r][c][v] for v in range(cells)) == 1
            problem += x[r][c] == pulp.lpSum((v + 1) * put[r][c][v] for v in range(cells))
    for v in range(cells):
        problem += pulp.lpSum(put[r][c][v] for r in range(n) for c in range(n)) == 1

    # The 2n + 2 lines whose sums must differ: the rows, the columns, the diagonal and the
    # anti-diagonal. Each line has n cells.
    lines = [[(r, c) for c in range(n)] for r in range(n)]
    lines += [[(r, c) for r in range(n)] for c in range(n)]
    lines.append([(i, i) for i in range(n)])
    lines.append([(i, n - 1 - i) for i in range(n)])

    # Smallest and largest sum of n distinct numbers from 1..cells (derived here, so the
    # sums need no looser bound: the n smallest, respectively the n largest, numbers).
    low = n * (n + 1) // 2
    high = n * cells - n * (n - 1) // 2

    # The sums of the lines are all different. line_is[k][s - low] = 1 if the sum of line k
    # is s; a line has exactly one sum, and no sum is shared by two lines.
    line_is = pulp.LpVariable.dicts("line_is", (range(len(lines)), range(high - low + 1)),
                                    cat="Binary")
    for k, line in enumerate(lines):
        problem += pulp.lpSum(line_is[k][s] for s in range(high - low + 1)) == 1
        problem += pulp.lpSum(x[r][c] for r, c in line) == pulp.lpSum(
            (low + s) * line_is[k][s] for s in range(high - low + 1))
    for s in range(high - low + 1):
        problem += pulp.lpSum(line_is[k][s] for k in range(len(lines))) <= 1

    return problem, {"x": x}
