# Hidato: a grid is partly filled with numbers. Fill the empty cells so that
# the numbers 1 to R*C each appear once, the given numbers keep their cells,
# and consecutive numbers touch horizontally, vertically or diagonally.
# Empty cells in the puzzle are 0.
from cvc5.pythonic import Int, Distinct, Or, Implies


def any_of(items):
    if len(items) == 1:
        return items[0]
    return Or(items)


def build(instance):
    puzzle = instance["puzzle"]
    R = len(puzzle)
    C = len(puzzle[0])
    N = R * C

    x = [[Int(f"x_{i}_{j}") for j in range(C)] for i in range(R)]
    cells = [x[i][j] for i in range(R) for j in range(C)]

    constraints = [Distinct(cells)]

    # Every cell holds a number from 1 to N.
    for c in cells:
        constraints.append(c >= 1)
        constraints.append(c <= N)

    # The given numbers keep their cells.
    for i in range(R):
        for j in range(C):
            v = puzzle[i][j]
            if v != 0:
                constraints.append(x[i][j] == v)

    # Consecutive numbers touch: the cell holding k has a neighbour holding k + 1.
    def neighbours(i, j):
        return [
            (a, b)
            for a in range(i - 1, i + 2)
            for b in range(j - 1, j + 2)
            if (a, b) != (i, j) and 0 <= a < R and 0 <= b < C
        ]

    for i in range(R):
        for j in range(C):
            for k in range(1, N):
                constraints.append(
                    Implies(
                        x[i][j] == k,
                        any_of([x[a][b] == k + 1 for a, b in neighbours(i, j)]),
                    )
                )

    return constraints, {"x": x}
