# Magic square: fill an n x n grid with the different integers 1..n^2 so that
# every row, every column and both diagonals add up to the same sum.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]  # side of the square
    magic_sum = n * (n * n + 1) // 2  # the sum every line has to reach

    pool = IDPool()
    # square[i][j] = the number in cell (i, j); direct encoding, one literal per number
    square = [[Integer(f"square_{i}_{j}", 1, n * n, vpool=pool) for j in range(n)] for i in range(n)]
    cells = [cell for row in square for cell in row]
    engine = IntegerEngine(vars=cells, vpool=pool)

    # all numbers are different
    engine.add_alldifferent(cells)

    # each row and each column adds up to the magic sum
    for i in range(n):
        engine.add_linear(sum(square[i][j] for j in range(n)) == magic_sum)
        engine.add_linear(sum(square[j][i] for j in range(n)) == magic_sum)
    # both diagonals add up to the magic sum
    engine.add_linear(sum(square[i][i] for i in range(n)) == magic_sum)
    engine.add_linear(sum(square[i][n - 1 - i] for i in range(n)) == magic_sum)

    return engine.clausify(), {"square": square}
