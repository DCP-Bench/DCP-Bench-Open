# Quasigroup completion (csplib 067): complete a partially filled order-N Latin square.
# Each cell holds a value from 1 to N, every row and every column contains each value once,
# and the pre-filled cells of the instance keep their values.

import cvc5.pythonic as cz


def build(instance):
    n = instance["N"]
    start = instance["start"]

    puzzle = [[cz.Int(f"q_{i}_{j}") for j in range(n)] for i in range(n)]

    constraints = []

    # Every cell takes a value from 1 to N.
    for i in range(n):
        for j in range(n):
            constraints.append(puzzle[i][j] >= 1)
            constraints.append(puzzle[i][j] <= n)

    # Each row contains each value from 1 to N exactly once.
    for i in range(n):
        constraints.append(cz.Distinct(puzzle[i]))

    # Each column contains each value from 1 to N exactly once.
    for j in range(n):
        constraints.append(cz.Distinct([puzzle[i][j] for i in range(n)]))

    # The pre-filled cells of the instance keep their given values; 0 marks an empty cell.
    # Given cells must agree with the completed square.
    for i in range(n):
        for j in range(n):
            if start[i][j] != 0:
                constraints.append(puzzle[i][j] == start[i][j])

    return constraints, {"puzzle": puzzle}
