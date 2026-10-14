# Quasigroup completion: fill the empty cells of a partially filled N x N grid
# so that every row and every column contains each of 1..N exactly once (a
# Latin square).
from hermax.model import Model


def build(instance):
    n = instance["N"]  # size of the square
    start = instance["start"]  # given cells; 0 marks an empty cell

    m = Model()
    # puzzle[i][j] = the number in cell (i, j), from 1 to N
    puzzle = m.int_matrix("puzzle", n, n, 1, n)

    # the given cells keep their value
    for i in range(n):
        for j in range(n):
            if start[i][j] != 0:
                m &= (puzzle[i][j] == start[i][j])

    # each row and each column holds different numbers
    for i in range(n):
        m &= puzzle.row(i).all_different()
        m &= puzzle.col(i).all_different()

    return m, {"puzzle": puzzle}
