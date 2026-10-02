# Calvin puzzle: fill an n x n grid with the numbers 1..n*n, each once, so that every number k + 1
# is placed exactly three squares away from k horizontally or vertically, or exactly two squares
# away diagonally (two squares along both directions).
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

# the moves from one number to the next: three squares along a row or a column, or two along both
# directions of a diagonal (the rule of the puzzle, not of the instance)
MOVES = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]


def build(instance):
    n = instance["n"]
    last = n * n  # the numbers run from 1 to last

    pool = IDPool()
    # x[i][j] = the number in row i, column j
    x = [[Integer(f"x_{i}_{j}", 1, last, vpool=pool) for j in range(n)] for i in range(n)]
    squares = [square for row in x for square in row]
    engine = IntegerEngine(vars=squares, vpool=pool)

    # every number is used once
    engine.add_alldifferent(squares)
    cnf = engine.clausify()

    for i in range(n):
        for j in range(n):
            reachable = [(i + di, j + dj) for di, dj in MOVES if 0 <= i + di < n and 0 <= j + dj < n]
            # if k is in square (i, j), then k + 1 is in a square reachable by one move
            for k in range(1, last):
                cnf.append([-x[i][j].equals(k)] + [x[a][b].equals(k + 1) for a, b in reachable])
            # Redundant, stated to help the solver: the moves are symmetric, so if k + 1 is in
            # square (i, j), then k is in a square reachable by one move.
            for k in range(2, last + 1):
                cnf.append([-x[i][j].equals(k)] + [x[a][b].equals(k - 1) for a, b in reachable])

    return cnf, {"x": x}
