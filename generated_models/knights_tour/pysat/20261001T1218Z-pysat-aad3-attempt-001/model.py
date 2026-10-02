# Knight's tour: number the squares of an n x n board 0..n*n-1, each once, so that the knight can
# go from square number k to square number k + 1 by one knight move. The tour does not have to
# return to its starting square.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

# the eight moves of a knight (a fact of chess, not of the instance)
KNIGHT_MOVES = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]


def build(instance):
    n = instance["n"]
    last = n * n - 1  # the move numbers run from 0 to last

    pool = IDPool()
    # x[i][j] = the number of the move in which the knight is on square (i, j)
    x = [[Integer(f"x_{i}_{j}", 0, last, vpool=pool) for j in range(n)] for i in range(n)]
    squares = [square for row in x for square in row]
    engine = IntegerEngine(vars=squares, vpool=pool)

    # every move number is used once, so every square is visited exactly once
    engine.add_alldifferent(squares)
    cnf = engine.clausify()

    for i in range(n):
        for j in range(n):
            reachable = [(i + di, j + dj) for di, dj in KNIGHT_MOVES
                         if 0 <= i + di < n and 0 <= j + dj < n]
            # if the knight is on square (i, j) in move k (not the last one), it is in move k + 1 on
            # one of the squares a knight move away (all numbers differ, so there is exactly one)
            for k in range(last):
                cnf.append([-x[i][j].equals(k)] + [x[a][b].equals(k + 1) for a, b in reachable])
            # and if it is there in move k (not the first one), it was in move k - 1 on one of those squares
            for k in range(1, last + 1):
                cnf.append([-x[i][j].equals(k)] + [x[a][b].equals(k - 1) for a, b in reachable])

    return cnf, {"x": x}
