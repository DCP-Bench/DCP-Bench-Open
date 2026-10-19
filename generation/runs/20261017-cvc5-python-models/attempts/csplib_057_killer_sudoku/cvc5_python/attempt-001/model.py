# Killer sudoku (csplib 057): fill the grid with the numbers 1 to n so that
# each row, column and nonet contains each number exactly once,
# the sum of all numbers in a cage matches the small number in its corner,
# and no number appears more than once in a cage.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    b = round(n ** 0.5)
    x = [[cz.Int(f"x_{r}_{c}") for c in range(n)] for r in range(n)]

    cons = []

    # Each cell holds a number from 1 to n.
    # The grid is the solution matrix, so every cell is constrained.
    for r in range(n):
        for c in range(n):
            cons.append(x[r][c] >= 1)
            cons.append(x[r][c] <= n)

    # Each row, column and nonet contains each number exactly once.
    # Each row and each column contains each number exactly once.
    for r in range(n):
        cons.append(cz.Distinct(x[r]))
        cons.append(cz.Distinct([x[k][r] for k in range(n)]))

    # Each nonet (3x3 block) contains each number exactly once.
    if b * b == n:
        for br in range(b):
            for bc in range(b):
                cells = [x[br * b + i][bc * b + j] for i in range(b) for j in range(b)]
                cons.append(cz.Distinct(cells))

    # The sum of all numbers in a cage must match the small number printed in its corner.
    # No number appears more than once in a cage.
    # Cage cells are 1-based (row, column) pairs in the data.
    for cage in instance["problem"]:
        total, cells = cage[0], cage[1]
        vals = [x[r - 1][c - 1] for r, c in cells]
        cons.append(cz.Sum(vals) == total)
        if len(vals) > 1:
            cons.append(cz.Distinct(vals))

    return cons, {"x": x}
