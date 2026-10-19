# Futoshiki: fill an n x n grid with the digits 1..n so that every row and every column
# contains each digit once. Some digits are given at the start, and some neighbouring
# squares carry an inequality (one must be lower than the other). Output: the completed
# grid as a list of lists of integers.
import mip


def build(instance):
    values = instance["values"]
    lt = instance["lt"]
    n = len(values)
    digits = range(1, n + 1)

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # p[i][j][v] is 1 when square (i, j) holds the digit v
    p = [[{v: m.add_var(f"p_{i}_{j}_{v}", var_type=mip.BINARY) for v in digits}
          for j in range(n)] for i in range(n)]
    grid = [[m.add_var(f"x_{i}_{j}", lb=1, ub=n, var_type=mip.INTEGER)
             for j in range(n)] for i in range(n)]

    # the grid is filled with the numbers 1 to n: each square holds exactly one digit,
    # and the grid value is that digit
    for i in range(n):
        for j in range(n):
            m += mip.xsum(p[i][j][v] for v in digits) == 1
            m += grid[i][j] == mip.xsum(v * p[i][j][v] for v in digits)

    # each row, and column contains each of the digits 1 to n
    for i in range(n):
        for v in digits:
            m += mip.xsum(p[i][j][v] for j in range(n)) == 1
    for j in range(n):
        for v in digits:
            m += mip.xsum(p[i][j][v] for i in range(n)) == 1

    # some digits may be given at the start
    for i in range(n):
        for j in range(n):
            if values[i][j] != 0:
                m += p[i][j][values[i][j]] == 1

    # inequality constraints are specified between some of the squares, such that one
    # must be higher or lower than its neighbour (1-based cell coordinates; the first
    # square is the lower one)
    for r1, c1, r2, c2 in lt:
        m += grid[r1 - 1][c1 - 1] + 1 <= grid[r2 - 1][c2 - 1]

    # satisfaction problem: no objective is set
    return m, {"grid": grid}
