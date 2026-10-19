# Kakuro: fill digits 1-9 into the white cells of an n x n grid so that each
# clue's sum matches and no digit is repeated within an entry. Blank cells (clue
# cells and black cells) are 0 in the output.

import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    blank = {(r, c) for r, c in instance["blanks"]}  # 1-based coordinates
    clues = instance["problem"]  # [sum, [r, c], [r, c], ...] (across and down entries)

    x = [[cz.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    constraints = []
    out = [[0] * n for _ in range(n)]

    # Each white cell takes a digit from 1 to 9. Blank cells stay the constant 0.
    for i in range(n):
        for j in range(n):
            if (i + 1, j + 1) not in blank:
                constraints.append(x[i][j] >= 1)
                constraints.append(x[i][j] <= 9)
                out[i][j] = x[i][j]

    # The sum of the numbers in each entry matches the clue associated with it.
    # No digit is duplicated in any entry.
    for clue in clues:
        total = clue[0]
        cells = [x[r - 1][c - 1] for r, c in clue[1:]]
        constraints.append(cz.Sum(cells) == total)
        if len(cells) >= 2:
            constraints.append(cz.Distinct(cells))

    return constraints, {"x": out}
