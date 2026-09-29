# Quasigroup completion: fill the empty cells of a partially filled N x N grid
# so that every row and every column contains each of 1..N exactly once (a
# Latin square).
import z3


def build(instance):
    n = instance["N"]  # size of the square
    start = instance["start"]  # given cells; 0 marks an empty cell

    solver = z3.Solver()

    # puzzle[i][j] = the number in cell (i, j), from 1 to N
    puzzle = [[z3.Int(f"puzzle_{i}_{j}") for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.add(puzzle[i][j] >= 1, puzzle[i][j] <= n)

    # the given cells keep their value
    for i in range(n):
        for j in range(n):
            if start[i][j] != 0:
                solver.add(puzzle[i][j] == start[i][j])

    # each row holds different numbers
    for i in range(n):
        solver.add(z3.Distinct(puzzle[i]))
    # each column holds different numbers
    for j in range(n):
        solver.add(z3.Distinct([puzzle[i][j] for i in range(n)]))

    return solver, {"puzzle": puzzle}
