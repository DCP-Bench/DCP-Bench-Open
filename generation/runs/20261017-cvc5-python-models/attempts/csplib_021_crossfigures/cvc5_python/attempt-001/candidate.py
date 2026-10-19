# csplib_021_crossfigures: a numerical crossword on a 9x9 grid. Each white cell holds one digit,
# and each across or down clue has a number as answer, written in its consecutive white cells
# (no leading zero). The grid layout and the clue texts come from the problem statement; the
# instance carries no fields, so they are mirrored here.

import cvc5.pythonic as cz

# Grid from the statement: X = black cell, _ = white cell without a clue number, n = clue number.
GRID = """
1 2 _ 3 X 4 _ 5 6
7 _ X 8 _ _ X 9 _
_ X 10 _ X 11 12 X _
13 14 _ _ X 15 _ 16 _
X _ X X X X X _ X
17 _ 18 19 X 20 21 _ 22
_ X 23 _ X 24 _ X _
25 26 X 27 _ _ X 28 _
29 _ _ _ X 30 _ _ _
"""

# Constants from the problem statement's definitions (not from the instance).
PRIMES2 = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
SQUARES2 = [16, 25, 36, 49, 64, 81]
SQUARES4 = [k * k for k in range(32, 100)]


def build(instance):
    rows = [line.split() for line in GRID.strip().splitlines()]
    R, C = len(rows), len(rows[0])

    def white(r, c):
        return rows[r][c] != "X"

    # One digit variable per white cell.
    M = {}
    cons = []
    for r in range(R):
        for c in range(C):
            if white(r, c):
                M[r, c] = cz.Int(f"m_{r}_{c}")
                cons += [M[r, c] >= 0, M[r, c] <= 9]

    # Entries: maximal runs of white cells of length >= 2, keyed by their clue number.
    across, down = {}, {}
    for r in range(R):
        c = 0
        while c < C:
            if white(r, c) and (c == 0 or not white(r, c - 1)):
                cells, k = [], c
                while k < C and white(r, k):
                    cells.append((r, k))
                    k += 1
                if len(cells) >= 2:
                    across[int(rows[r][c])] = cells
                c = k
            else:
                c += 1
    for c in range(C):
        r = 0
        while r < R:
            if white(r, c) and (r == 0 or not white(r - 1, c)):
                cells, k = [], r
                while k < R and white(k, c):
                    cells.append((k, c))
                    k += 1
                if len(cells) >= 2:
                    down[int(rows[r][c])] = cells
                r = k
            else:
                r += 1

    def num(cells):
        # the answer written in these cells, most significant digit first
        L = len(cells)
        return cz.Sum([M[rc] * 10 ** (L - 1 - i) for i, rc in enumerate(cells)])

    # Each answer is a number with no leading zero.
    for cells in list(across.values()) + list(down.values()):
        cons.append(M[cells[0]] != 0)

    A = {n: num(cells) for n, cells in across.items()}
    D = {n: num(cells) for n, cells in down.items()}

    # Across clues.
    # 1: 27 across times two
    cons.append(A[1] == 2 * A[27])
    # 4: 4 down plus seventy-one
    cons.append(A[4] == D[4] + 71)
    # 7: 18 down plus four
    cons.append(A[7] == D[18] + 4)
    # 8: 6 down divided by sixteen
    cons.append(D[6] == 16 * A[8])
    # 9: 2 down minus eighteen
    cons.append(A[9] == D[2] - 18)
    # 10: dozen in six gross (6 * 144 = 864 = 72 dozen)
    cons.append(A[10] == 72)
    # 11: 5 down minus seventy
    cons.append(A[11] == D[5] - 70)
    # 13: 26 down times 23 across. A23 is a prime, so the product is split over the primes.
    cons.append(cz.Or([cz.And(A[23] == p, A[13] == p * D[26]) for p in PRIMES2]))
    # 15: 6 down minus 350
    cons.append(A[15] == D[6] - 350)
    # 17: 25 across times 23 across. Same prime split.
    cons.append(cz.Or([cz.And(A[23] == p, A[17] == p * A[25]) for p in PRIMES2]))
    # 20: a square number (four digits)
    cons.append(cz.Or([A[20] == s for s in SQUARES4]))
    # 23: a prime number (two digits)
    cons.append(cz.Or([A[23] == p for p in PRIMES2]))
    # 24: a square number (two digits)
    cons.append(cz.Or([A[24] == s for s in SQUARES2]))
    # 25: 20 across divided by seventeen
    cons.append(A[20] == 17 * A[25])
    # 27: 6 down divided by four
    cons.append(D[6] == 4 * A[27])
    # 28: four dozen (= 48)
    cons.append(A[28] == 48)
    # 29: seven gross (= 1008)
    cons.append(A[29] == 1008)
    # 30: 22 down plus 450
    cons.append(A[30] == D[22] + 450)

    # Down clues.
    # 1: 1 across plus twenty-seven
    cons.append(D[1] == A[1] + 27)
    # 2: five dozen (= 60)
    cons.append(D[2] == 60)
    # 3: 30 across plus 888
    cons.append(D[3] == A[30] + 888)
    # 4: two times 17 across
    cons.append(D[4] == 2 * A[17])
    # 5: 29 across divided by twelve
    cons.append(A[29] == 12 * D[5])
    # 6: 28 across times 23 across (A28 = 48, so the product is linear)
    cons.append(D[6] == 48 * A[23])
    # 10: 10 across plus four
    cons.append(D[10] == A[10] + 4)
    # 12: three times 24 across
    cons.append(D[12] == 3 * A[24])
    # 14: 13 across divided by sixteen
    cons.append(A[13] == 16 * D[14])
    # 16: 28 down times fifteen
    cons.append(D[16] == 15 * D[28])
    # 17: 13 across minus 399
    cons.append(D[17] == A[13] - 399)
    # 18: 29 across divided by eighteen
    cons.append(A[29] == 18 * D[18])
    # 19: 22 down minus ninety-four
    cons.append(D[19] == D[22] - 94)
    # 20: 20 across minus nine
    cons.append(D[20] == A[20] - 9)
    # 21: 25 across minus fifty-two
    cons.append(D[21] == A[25] - 52)
    # 22: 20 down times six
    cons.append(D[22] == 6 * D[20])
    # 26: five times 24 across
    cons.append(D[26] == 5 * A[24])
    # 28: 21 down plus twenty-seven
    cons.append(D[28] == D[21] + 27)

    # Output: the solved grid, 0 for black cells.
    grid_out = [[M[r, c] if white(r, c) else 0 for c in range(C)] for r in range(R)]
    return cons, {"M": grid_out}
