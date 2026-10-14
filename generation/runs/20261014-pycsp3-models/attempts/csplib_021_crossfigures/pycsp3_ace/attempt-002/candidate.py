from math import isqrt
from pycsp3 import *

# crossfigure: fill the digits of the grid so that every clue holds (0 marks a black or invalid cell)
# the grid: "." is a white cell, "X" is a black cell
GRID = [
    "....X....",
    "..X...X..",
    ".X..X..X.",
    "....X....",
    "X.XXXXX.X",
    "....X....",
    ".X..X..X.",
    "..X...X..",
    "....X....",
]
N = 9


def white(r, c):
    return 0 <= r < N and 0 <= c < N and GRID[r][c] == "."


def is_square(v):
    return isqrt(v) ** 2 == v


def is_prime(v):
    return v > 1 and all(v % p for p in range(2, isqrt(v) + 1))


# number the entries the usual way: a cell starts an across or a down entry when the run has two or more cells
label = {}
across = {}  # label -> list of cells of the across entry
down = {}  # label -> list of cells of the down entry
nxt = 1
for r in range(N):
    for c in range(N):
        if not white(r, c):
            continue
        starts_across = not white(r, c - 1) and white(r, c + 1)
        starts_down = not white(r - 1, c) and white(r + 1, c)
        if starts_across or starts_down:
            label[(r, c)] = nxt
            if starts_across:
                cells = []
                k = c
                while white(r, k):
                    cells.append((r, k))
                    k += 1
                across[nxt] = cells
            if starts_down:
                cells = []
                k = r
                while white(k, c):
                    cells.append((k, c))
                    k += 1
                down[nxt] = cells
            nxt += 1

# digits of the grid; black cells are 0
M = VarArray(size=[N, N], dom=range(10))


def entry_var(kind, k, cells):
    length = len(cells)
    lo, hi = 10 ** (length - 1), 10 ** length
    test = lambda v: True
    if kind == "A" and k in (20, 24):
        test = is_square
    if kind == "A" and k == 23:
        test = is_prime
    return Var(dom=[v for v in range(lo, hi) if test(v)], id=f"{kind}{k}")


A = {k: entry_var("A", k, cells) for k, cells in across.items()}
D = {k: entry_var("D", k, cells) for k, cells in down.items()}

entry_constraints = []
for kind, table, entries in (("A", A, across), ("D", D, down)):
    for k, cells in entries.items():
        length = len(cells)
        digits = [M[r][c] for (r, c) in cells]
        entry_constraints.append(table[k] == Sum(digits[i] * 10 ** (length - 1 - i) for i in range(length)))

satisfy(
    # black cells hold no digit
    [M[r][c] == 0 for r in range(N) for c in range(N) if not white(r, c)],
    # a white cell that starts an entry holds a non-zero digit
    [M[r][c] >= 1 for (r, c) in label],
    # every entry reads as the number formed by its digits
    entry_constraints,
    # across 1: 27 across times two
    A[1] == 2 * A[27],
    # across 4: 4 down plus seventy-one
    A[4] == D[4] + 71,
    # across 7: 18 down plus four
    A[7] == D[18] + 4,
    # across 8: 6 down divided by sixteen
    D[6] == 16 * A[8],
    # across 9: 2 down minus eighteen
    A[9] == D[2] - 18,
    # across 10: dozen in six gross
    A[10] == 72,
    # across 11: 5 down minus seventy
    A[11] == D[5] - 70,
    # across 13: 26 down times 23 across
    A[13] == D[26] * A[23],
    # across 15: 6 down minus 350
    A[15] == D[6] - 350,
    # across 17: 25 across times 23 across
    A[17] == A[25] * A[23],
    # across 25: 20 across divided by seventeen
    A[20] == 17 * A[25],
    # across 27: 6 down divided by four
    D[6] == 4 * A[27],
    # across 28: four dozen
    A[28] == 48,
    # across 29: seven gross
    A[29] == 1008,
    # across 30: 22 down plus 450
    A[30] == D[22] + 450,
    # down 1: 1 across plus twenty-seven
    D[1] == A[1] + 27,
    # down 2: five dozen
    D[2] == 60,
    # down 3: 30 across plus 888
    D[3] == A[30] + 888,
    # down 4: two times 17 across
    D[4] == 2 * A[17],
    # down 5: 29 across divided by twelve
    A[29] == 12 * D[5],
    # down 6: 28 across times 23 across
    D[6] == A[28] * A[23],
    # down 10: 10 across plus four
    D[10] == A[10] + 4,
    # down 12: three times 24 across
    D[12] == 3 * A[24],
    # down 14: 13 across divided by sixteen
    A[13] == 16 * D[14],
    # down 16: 28 down times fifteen
    D[16] == 15 * D[28],
    # down 17: 13 across minus 399
    D[17] == A[13] - 399,
    # down 18: 29 across divided by eighteen
    A[29] == 18 * D[18],
    # down 19: 22 down minus ninety-four
    D[19] == D[22] - 94,
    # down 20: 20 across minus nine
    D[20] == A[20] - 9,
    # down 21: 25 across minus fifty-two
    D[21] == A[25] - 52,
    # down 22: 20 down times six
    D[22] == 6 * D[20],
    # down 26: five times 24 across
    D[26] == 5 * A[24],
    # down 28: 21 down plus twenty-seven
    D[28] == D[21] + 27,
)
