# Quasigroup completion: fill the empty cells of a partially filled N x N grid
# so that every row and every column contains each of 1..N exactly once (a
# Latin square).
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["N"]  # size of the square
    start = instance["start"]  # given cells; 0 marks an empty cell

    pool = IDPool()
    # puzzle[i][j] = the number in cell (i, j), from 1 to N
    puzzle = [[Integer(f"puzzle_{i}_{j}", 1, n, vpool=pool) for j in range(n)] for i in range(n)]
    engine = IntegerEngine(vars=[cell for row in puzzle for cell in row], vpool=pool)

    # the given cells keep their value
    for i in range(n):
        for j in range(n):
            if start[i][j] != 0:
                engine.add_linear(puzzle[i][j] == start[i][j])

    # each row and each column holds different numbers
    for i in range(n):
        engine.add_alldifferent(puzzle[i])
        engine.add_alldifferent([puzzle[j][i] for j in range(n)])

    return engine.clausify(), {"puzzle": puzzle}
