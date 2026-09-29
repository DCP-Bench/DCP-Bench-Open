# Quasigroup completion: fill the empty cells of a partially filled N x N grid
# so that every row and every column contains each of 1..N exactly once (a
# Latin square).
from pychoco.model import Model


def build(instance):
    n = instance["N"]  # size of the square
    start = instance["start"]  # given cells; 0 marks an empty cell

    model = Model()

    # puzzle[i][j] = the number in cell (i, j), from 1 to N
    puzzle = [[model.intvar(1, n, name=f"puzzle_{i}_{j}") for j in range(n)] for i in range(n)]

    # the given cells keep their value
    for i in range(n):
        for j in range(n):
            if start[i][j] != 0:
                model.arithm(puzzle[i][j], "=", start[i][j]).post()

    # each row holds different numbers
    for i in range(n):
        model.all_different(puzzle[i]).post()
    # each column holds different numbers
    for j in range(n):
        model.all_different([puzzle[i][j] for i in range(n)]).post()

    return model, {"puzzle": puzzle}
