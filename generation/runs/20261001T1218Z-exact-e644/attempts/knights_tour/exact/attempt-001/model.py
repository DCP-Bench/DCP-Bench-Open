# Knight's tour: number the squares of an n x n chessboard 0..n*n-1, each once, so that squares
# with consecutive numbers are a knight's move apart. The tour visits every square exactly once
# and need not return to its start.
from exact import Exact


def build(instance):
    n = instance["n"]
    squares = n * n
    moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

    solver = Exact()

    # holds[i][j][k] = 1 when the knight is on square (i, j) as its move number k (k from 0).
    # Exact has no all-different or element constraint, so both "each square visited once" and
    # "the next move is a knight's move away" use these indicators.
    holds = [[[f"square_{i}_{j}_is_move_{k}" for k in range(squares)] for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            for name in holds[i][j]:
                solver.addVariable(name, 0, 1)
            # every square is visited at exactly one move
            solver.addConstraint([(1, name) for name in holds[i][j]], True, 1, True, 1)
    for k in range(squares):
        # every move number is made on exactly one square (the numbers are all different)
        solver.addConstraint([(1, holds[i][j][k]) for i in range(n) for j in range(n)], True, 1, True, 1)

    # x[i][j] is the move number at which square (i, j) is visited
    x = [[f"x_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(x[i][j], 0, squares - 1)
            solver.addConstraint([(k, holds[i][j][k]) for k in range(1, squares)] + [(-1, x[i][j])],
                                 True, 0, True, 0)

    # Knight's moves: the square visited at move k+1 is a knight's move from the square visited at
    # move k, so a square that holds k (other than the last move) has a knight neighbour that
    # holds k+1, and one that holds k (other than the first move) has a neighbour that holds k-1.
    for i in range(n):
        for j in range(n):
            neighbours = [(i + a, j + b) for a, b in moves if 0 <= i + a < n and 0 <= j + b < n]
            for k in range(squares - 1):
                solver.addConstraint([(1, holds[ni][nj][k + 1]) for ni, nj in neighbours]
                                     + [(-1, holds[i][j][k])], True, 0)
            for k in range(1, squares):
                solver.addConstraint([(1, holds[ni][nj][k - 1]) for ni, nj in neighbours]
                                     + [(-1, holds[i][j][k])], True, 0)

    return solver, {"x": x}
