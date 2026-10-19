# Kakuro: fill digits 1-9 into the white cells of an n x n grid so that each
# clue's sum matches and no digit is repeated within an entry. Black cells are 0.

import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    white = {(r, c) for r, c in instance["blanks"]}  # 1-based coordinates
    clues = instance["problem"]  # [sum, [r, c], [r, c], ...] (across and down)

    x = [[cz.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    constraints = []

    # Cell values: white cells take a digit from 1 to 9. Black cells are fixed at 0.
    # Black cells are left as Python constants in the output.
    cell_out = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if (i + 1, j + 1) in white:
                constraints.append(x[i][j] >= 1)
                constraints.append(x[i][j] <= 9)
                cell_out[i][j] = x[i][j]

    # Clue sums: the sum of the numbers in each entry matches the clue associated with it.
    # No digit is duplicated in any entry.
    for clue in clues:
        total = clue[0]
        cells = [x[r - 1][c - 1] for r, c in clue[1:]]
        constraints.append(cz.Sum(cells) == total)
        if len(cells) >= 2:
            constraints.append(cz.Distinct(cells))

    return constraints, {"x": cell_out}
