# Killer sudoku (csplib 057): fill the grid with the numbers 1 to n so that
# each row, column and nonet contains each number exactly once,
# the sum of all numbers in a cage matches the small number in its corner,
# and no number appears more than once in a cage.
#
# The grid is encoded with one Boolean per cell and value (one-hot), so the
# all-different rules become exactly-one clauses that the SAT core propagates.
import cvc5.pythonic as cz


def at_most_one(lits):
    # Pairwise: no two of the literals are true together.
    out = []
    for i in range(len(lits)):
        for j in range(i + 1, len(lits)):
            out.append(cz.Or(cz.Not(lits[i]), cz.Not(lits[j])))
    return out


def exactly_one(lits):
    return [cz.Or(lits)] + at_most_one(lits)


def build(instance):
    n = instance["n"]
    b = round(n ** 0.5)
    vals = list(range(1, n + 1))
    p = [[[cz.Bool(f"p_{r}_{c}_{v}") for v in vals] for c in range(n)] for r in range(n)]
    x = [[cz.Int(f"x_{r}_{c}") for c in range(n)] for r in range(n)]

    cons = []

    # Each cell holds exactly one number from 1 to n.
    # The value of the cell is the number it holds.
    for r in range(n):
        for c in range(n):
            cons += exactly_one(p[r][c])
            cons.append(x[r][c] == cz.Sum([cz.If(p[r][c][k], vals[k], 0) for k in range(n)]))

    # Each row, column and nonet contains each number exactly once.
    units = []
    for r in range(n):
        units.append([(r, c) for c in range(n)])
        units.append([(k, r) for k in range(n)])
    if b * b == n:
        for br in range(b):
            for bc in range(b):
                units.append([(br * b + i, bc * b + j) for i in range(b) for j in range(b)])
    for unit in units:
        for k in range(n):
            cons += exactly_one([p[r][c][k] for r, c in unit])

    # The sum of all numbers in a cage must match the small number printed in its corner.
    # No number appears more than once in a cage.
    # Cage cells are 1-based (row, column) pairs in the data.
    for cage in instance["problem"]:
        total, cells = cage[0], cage[1]
        cage_cells = [(r - 1, c - 1) for r, c in cells]
        cons.append(cz.Sum([x[r][c] for r, c in cage_cells]) == total)
        if len(cage_cells) > 1:
            for k in range(n):
                cons += at_most_one([p[r][c][k] for r, c in cage_cells])

    return cons, {"x": x}
