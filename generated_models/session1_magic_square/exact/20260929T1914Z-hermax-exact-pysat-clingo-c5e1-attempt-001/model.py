# Magic square: fill an n x n grid with the different integers 1..n^2 so that
# every row, every column and both diagonals add up to the same sum.
from exact import Exact


def build(instance):
    n = instance["n"]  # side of the square
    magic_sum = n * (n * n + 1) // 2  # the sum every line has to reach
    values = range(1, n * n + 1)

    solver = Exact()
    # square[i][j] = the number in cell (i, j), between 1 and n^2
    square = [[f"square_{i}_{j}" for j in range(n)] for i in range(n)]
    # is_[i][j][v] is 1 exactly when cell (i, j) holds v; they make "all different"
    # a count of at most one cell per value (the domain is n^2, so n^4 indicators)
    is_ = [[{} for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(square[i][j], 1, n * n)
            for v in values:
                is_[i][j][v] = f"is_{i}_{j}_{v}"
                solver.addVariable(is_[i][j][v], 0, 1)
            solver.addConstraint([(1, is_[i][j][v]) for v in values], True, 1, True, 1)
            solver.addConstraint([(v, is_[i][j][v]) for v in values] + [(-1, square[i][j])],
                                 True, 0, True, 0)

    # all numbers are different: each value sits in exactly one cell
    for v in values:
        solver.addConstraint([(1, is_[i][j][v]) for i in range(n) for j in range(n)], True, 1, True, 1)

    # each row and each column adds up to the magic sum
    for i in range(n):
        solver.addConstraint([(1, square[i][j]) for j in range(n)], True, magic_sum, True, magic_sum)
        solver.addConstraint([(1, square[j][i]) for j in range(n)], True, magic_sum, True, magic_sum)
    # both diagonals add up to the magic sum
    solver.addConstraint([(1, square[i][i]) for i in range(n)], True, magic_sum, True, magic_sum)
    solver.addConstraint([(1, square[i][n - 1 - i]) for i in range(n)], True, magic_sum, True, magic_sum)

    return solver, {"square": square}
