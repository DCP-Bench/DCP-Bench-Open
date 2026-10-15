# Crossfigures (CSPLib 021): fill the digit cells of a 9x9 grid so that every
# across and down clue holds. Output M gives each cell's digit, 0 for a black cell.
from pyscipopt import Model, quicksum

# The grid is part of the problem statement (the instance data is empty).
# X is a black cell, a number is a clue label on a white cell, _ is a plain white cell.
GRID = [
    "1 2 _ 3 X 4 _ 5 6",
    "7 _ X 8 _ _ X 9 _",
    "_ X 10 _ X 11 12 X _",
    "13 14 _ _ X 15 _ 16 _",
    "X _ X X X X X _ X",
    "17 _ 18 19 X 20 21 _ 22",
    "_ X 23 _ X 24 _ X _",
    "25 26 X 27 _ _ X 28 _",
    "29 _ _ _ X 30 _ _ _",
]


def build(instance):
    grid = [row.split() for row in GRID]
    R, C = len(grid), len(grid[0])

    def white(r, c):
        return 0 <= r < R and 0 <= c < C and grid[r][c] != "X"

    m = Model()

    # One digit variable per white cell.
    d = {}
    for r in range(R):
        for c in range(C):
            if white(r, c):
                d[r, c] = m.addVar(name=f"d_{r}_{c}", vtype="I", lb=0, ub=9)

    # Blank output for black cells: a variable fixed to 0.
    blank = m.addVar(name="blank", vtype="I", lb=0, ub=0)

    # Find the answer cells of each clue. A label cell starts an across (or down)
    # answer when the cell before it (or above it) is black or outside the grid.
    across_cells, down_cells = {}, {}
    for r in range(R):
        for c in range(C):
            tok = grid[r][c]
            if not tok.isdigit():
                continue
            n = int(tok)
            if white(r, c + 1) and not white(r, c - 1):
                cells, cc = [], c
                while white(r, cc):
                    cells.append((r, cc))
                    cc += 1
                across_cells[n] = cells
            if white(r + 1, c) and not white(r - 1, c):
                cells, rr = [], r
                while white(rr, c):
                    cells.append((rr, c))
                    rr += 1
                down_cells[n] = cells

    # Each clue answer is an integer with one digit per cell and no leading zero.
    def answer(name, cells):
        L = len(cells)
        v = m.addVar(name=name, vtype="I", lb=10 ** (L - 1), ub=10 ** L - 1)
        # the answer's decimal digits are the cells' digits, first cell most significant
        m.addCons(v == quicksum(d[cell] * 10 ** (L - 1 - i) for i, cell in enumerate(cells)))
        return v

    A = {n: answer(f"across_{n}", cells) for n, cells in across_cells.items()}
    D = {n: answer(f"down_{n}", cells) for n, cells in down_cells.items()}

    # Across clues
    # 1 across: 27 across times two
    m.addCons(A[1] == 2 * A[27])
    # 4 across: 4 down plus seventy-one
    m.addCons(A[4] == D[4] + 71)
    # 7 across: 18 down plus four
    m.addCons(A[7] == D[18] + 4)
    # 8 across: 6 down divided by sixteen
    m.addCons(D[6] == 16 * A[8])
    # 9 across: 2 down minus eighteen
    m.addCons(A[9] == D[2] - 18)
    # 10 across: dozen in six gross (six gross is 864 and a dozen is 12)
    m.addCons(A[10] == 72)
    # 11 across: 5 down minus seventy
    m.addCons(A[11] == D[5] - 70)
    # 13 across: 26 down times 23 across
    m.addCons(A[13] == D[26] * A[23])
    # 15 across: 6 down minus 350
    m.addCons(A[15] == D[6] - 350)
    # 17 across: 25 across times 23 across
    m.addCons(A[17] == A[25] * A[23])
    # 20 across: a square number
    s20 = m.addVar(name="root_20", vtype="I", lb=0, ub=99)
    m.addCons(A[20] == s20 * s20)
    # 23 across: a prime number (two digits, so no divisor from 2 to 9)
    for k in range(2, 10):
        q = m.addVar(name=f"prime23_q_{k}", vtype="I", lb=0, ub=99 // k)
        r = m.addVar(name=f"prime23_r_{k}", vtype="I", lb=1, ub=k - 1)
        m.addCons(A[23] == k * q + r)
    # 24 across: a square number
    s24 = m.addVar(name="root_24", vtype="I", lb=0, ub=9)
    m.addCons(A[24] == s24 * s24)
    # 25 across: 20 across divided by seventeen
    m.addCons(A[20] == 17 * A[25])
    # 27 across: 6 down divided by four
    m.addCons(D[6] == 4 * A[27])
    # 28 across: four dozen
    m.addCons(A[28] == 48)
    # 29 across: seven gross
    m.addCons(A[29] == 1008)
    # 30 across: 22 down plus 450
    m.addCons(A[30] == D[22] + 450)

    # Down clues
    # 1 down: 1 across plus twenty-seven
    m.addCons(D[1] == A[1] + 27)
    # 2 down: five dozen
    m.addCons(D[2] == 60)
    # 3 down: 30 across plus 888
    m.addCons(D[3] == A[30] + 888)
    # 4 down: two times 17 across
    m.addCons(D[4] == 2 * A[17])
    # 5 down: 29 across divided by twelve
    m.addCons(A[29] == 12 * D[5])
    # 6 down: 28 across times 23 across
    m.addCons(D[6] == A[28] * A[23])
    # 10 down: 10 across plus four
    m.addCons(D[10] == A[10] + 4)
    # 12 down: three times 24 across
    m.addCons(D[12] == 3 * A[24])
    # 14 down: 13 across divided by sixteen
    m.addCons(A[13] == 16 * D[14])
    # 16 down: 28 down times fifteen
    m.addCons(D[16] == D[28] * 15)
    # 17 down: 13 across minus 399
    m.addCons(D[17] == A[13] - 399)
    # 18 down: 29 across divided by eighteen
    m.addCons(A[29] == 18 * D[18])
    # 19 down: 22 down minus ninety-four
    m.addCons(D[19] == D[22] - 94)
    # 20 down: 20 across minus nine
    m.addCons(D[20] == A[20] - 9)
    # 21 down: 25 across minus fifty-two
    m.addCons(D[21] == A[25] - 52)
    # 22 down: 20 down times six
    m.addCons(D[22] == 6 * D[20])
    # 26 down: five times 24 across
    m.addCons(D[26] == 5 * A[24])
    # 28 down: 21 down plus twenty-seven
    m.addCons(D[28] == D[21] + 27)

    # Output: the 9x9 grid of digits, 0 for black cells.
    M = [[d[r, c] if white(r, c) else blank for c in range(C)] for r in range(R)]
    return m, {"M": M}
