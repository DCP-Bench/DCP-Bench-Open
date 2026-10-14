# Quasigroup completion: fill the empty cells of a partially filled N x N grid
# so that every row and every column contains each of 1..N exactly once (a
# Latin square).
from exact import Exact


def build(instance):
    n = instance["N"]  # size of the square
    start = instance["start"]  # given cells; 0 marks an empty cell

    solver = Exact()
    puzzle = [[f"puzzle_{i}_{j}" for j in range(n)] for i in range(n)]
    # is_[i][j][v] is 1 exactly when cell (i, j) holds v
    is_ = [[{} for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(puzzle[i][j], 1, n)
            for v in range(1, n + 1):
                is_[i][j][v] = f"is_{i}_{j}_{v}"
                solver.addVariable(is_[i][j][v], 0, 1)
            solver.addConstraint([(1, is_[i][j][v]) for v in range(1, n + 1)], True, 1, True, 1)
            solver.addConstraint([(v, is_[i][j][v]) for v in range(1, n + 1)] + [(-1, puzzle[i][j])],
                                 True, 0, True, 0)
            # the given cells keep their value
            if start[i][j] != 0:
                solver.addConstraint([(1, is_[i][j][start[i][j]])], True, 1, True, 1)

    # every row and every column holds each number exactly once
    for v in range(1, n + 1):
        for i in range(n):
            solver.addConstraint([(1, is_[i][j][v]) for j in range(n)], True, 1, True, 1)
            solver.addConstraint([(1, is_[j][i][v]) for j in range(n)], True, 1, True, 1)

    return solver, {"puzzle": puzzle}
