# Hidato: fill a grid with the numbers 1..(rows * columns), each once, so that the given
# numbers stay in place and every number k + 1 lies in a cell touching the cell of k
# horizontally, vertically or diagonally.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    puzzle = instance["puzzle"]  # 0 = empty cell, otherwise the number already placed there
    rows, cols = len(puzzle), len(puzzle[0])
    last = rows * cols           # the numbers run from 1 to last

    pool = IDPool()
    # x[r][c] = the number in row r, column c
    x = [[Integer(f"x_{r}_{c}", 1, last, vpool=pool) for c in range(cols)] for r in range(rows)]
    engine = IntegerEngine(vars=[cell for row in x for cell in row], vpool=pool)

    # every number is used once
    engine.add_alldifferent([cell for row in x for cell in row])
    cnf = engine.clausify()

    # the given numbers
    for r in range(rows):
        for c in range(cols):
            if puzzle[r][c] > 0:
                cnf.append([x[r][c].equals(puzzle[r][c])])

    def touching(r, c):
        """The cells that touch (r, c) horizontally, vertically or diagonally."""
        return [(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                if (dr, dc) != (0, 0) and 0 <= r + dr < rows and 0 <= c + dc < cols]

    # consecutive numbers touch: if k is in a cell, k + 1 is in one of the cells touching it
    # (the cell itself is excluded, and the numbers are all different, so k + 1 is elsewhere)
    for r in range(rows):
        for c in range(cols):
            for k in range(1, last):
                cnf.append([-x[r][c].equals(k)] + [x[nr][nc].equals(k + 1) for nr, nc in touching(r, c)])
            # Redundant, stated to help the solver: the same chain read backwards, so if k + 1
            # is in a cell then k is in a cell touching it.
            for k in range(2, last + 1):
                cnf.append([-x[r][c].equals(k)] + [x[nr][nc].equals(k - 1) for nr, nc in touching(r, c)])

    return cnf, {"x": x}
