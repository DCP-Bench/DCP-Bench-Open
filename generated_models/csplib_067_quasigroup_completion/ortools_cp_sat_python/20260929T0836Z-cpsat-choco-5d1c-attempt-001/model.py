# Quasigroup completion: fill the empty cells of a partially filled N x N grid
# so that every row and every column contains each of 1..N exactly once (a
# Latin square).
from ortools.sat.python import cp_model


def build(instance):
    n = instance["N"]  # size of the square
    start = instance["start"]  # given cells; 0 marks an empty cell

    model = cp_model.CpModel()

    # puzzle[i][j] = the number in cell (i, j), from 1 to N
    puzzle = [[model.new_int_var(1, n, f"puzzle_{i}_{j}") for j in range(n)] for i in range(n)]

    # the given cells keep their value
    for i in range(n):
        for j in range(n):
            if start[i][j] != 0:
                model.add(puzzle[i][j] == start[i][j])

    # each row holds different numbers
    for i in range(n):
        model.add_all_different(puzzle[i])
    # each column holds different numbers
    for j in range(n):
        model.add_all_different([puzzle[i][j] for i in range(n)])

    return model, {"puzzle": puzzle}
