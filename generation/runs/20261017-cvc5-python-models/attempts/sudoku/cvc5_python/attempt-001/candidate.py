# Sudoku: fill a 9x9 grid with digits 1 to 9 so that each row, each column and
# each 3x3 section contains all the digits. The input grid has some cells filled
# with numbers and some empty (0). The grid output is the solved grid.

import cvc5.pythonic as cz


def build(instance):
    given = instance["input_grid"]
    n = len(given)

    grid = [[cz.Int(f"g_{r}_{c}") for c in range(n)] for r in range(n)]

    constraints = []

    # Each cell holds a digit between 1 and 9.
    for r in range(n):
        for c in range(n):
            constraints.append(grid[r][c] >= 1)
            constraints.append(grid[r][c] <= 9)

    # Each row contains all the digits between 1 and 9.
    # each row contains all the digits between 1 and 9
    for r in range(n):
        constraints.append(cz.Distinct(grid[r]))

    # Each column contains all the digits between 1 and 9.
    # each column contains all the digits between 1 and 9
    for c in range(n):
        constraints.append(cz.Distinct([grid[r][c] for r in range(n)]))

    # Each 3x3 section contains all the digits between 1 and 9.
    # each 3x3 section contains all the digits between 1 and 9
    for br in range(0, n, 3):
        for bc in range(0, n, 3):
            constraints.append(
                cz.Distinct([grid[br + i][bc + j] for i in range(3) for j in range(3)])
            )

    # The input grid has some cells filled with numbers; those cells keep their value.
    # cells filled with numbers in the input keep their value
    for r in range(n):
        for c in range(n):
            v = given[r][c]
            if v != 0:
                constraints.append(grid[r][c] == v)

    return constraints, {"grid": grid}
