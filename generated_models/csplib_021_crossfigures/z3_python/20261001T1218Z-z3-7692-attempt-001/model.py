# Crossfigure (CSPLib 21): the numerical equivalent of a crossword. Fill a 9x9 grid
# with digits so that every across and down entry is a number that satisfies its
# clue ("27 across times two", "a prime number", ...).
import math

import z3


def build(instance):
    del instance  # the puzzle states its own grid and clues

    n = 9
    max_value = 9999  # every entry has at most four digits

    # Problem data: the grid from the puzzle, X marks a black box.
    grid = [
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

    # Problem data: the entries as (clue number, length, row, column), 1-based, with
    # the grid origin at the top left.
    across_entries = [
        (1, 4, 1, 1), (4, 4, 1, 6), (7, 2, 2, 1), (8, 3, 2, 4), (9, 2, 2, 8),
        (10, 2, 3, 3), (11, 2, 3, 6), (13, 4, 4, 1), (15, 4, 4, 6), (17, 4, 6, 1),
        (20, 4, 6, 6), (23, 2, 7, 3), (24, 2, 7, 6), (25, 2, 8, 1), (27, 3, 8, 4),
        (28, 2, 8, 8), (29, 4, 9, 1), (30, 4, 9, 6),
    ]
    down_entries = [
        (1, 4, 1, 1), (2, 2, 1, 2), (3, 4, 1, 4), (4, 4, 1, 6), (5, 2, 1, 8),
        (6, 4, 1, 9), (10, 2, 3, 3), (12, 2, 3, 7), (14, 3, 4, 2), (16, 3, 4, 8),
        (17, 4, 6, 1), (18, 2, 6, 3), (19, 4, 6, 4), (20, 4, 6, 6), (21, 2, 6, 7),
        (22, 4, 6, 9), (26, 2, 8, 2), (28, 2, 8, 8),
    ]

    solver = z3.Solver()

    # M[r][c] = digit in cell (r, c); a black box is shown as 0.
    M = [[z3.Int(f"M_{r}_{c}") for c in range(n)] for r in range(n)]
    for r in range(n):
        for c in range(n):
            solver.add(M[r][c] >= 0, M[r][c] <= 9)
            if grid[r][c] == "X":
                solver.add(M[r][c] == 0)

    # The number written by each entry, tied to its digits in the grid (read from
    # the most significant digit; leading zeros are allowed).
    across = {}
    down = {}
    for clue, length, row, col in across_entries:
        across[clue] = z3.Int(f"A{clue}")
        solver.add(across[clue] >= 0, across[clue] <= max_value)
        digits = [M[row - 1][col - 1 + i] for i in range(length)]
        solver.add(across[clue] == z3.Sum([10 ** (length - 1 - i) * d for i, d in enumerate(digits)]))
    for clue, length, row, col in down_entries:
        down[clue] = z3.Int(f"D{clue}")
        solver.add(down[clue] >= 0, down[clue] <= max_value)
        digits = [M[row - 1 + i][col - 1] for i in range(length)]
        solver.add(down[clue] == z3.Sum([10 ** (length - 1 - i) * d for i, d in enumerate(digits)]))

    A, D = across, down
    across_length = {clue: length for clue, length, _, _ in across_entries}

    def is_prime(k):
        return k >= 2 and all(k % i for i in range(2, math.isqrt(k) + 1))

    def one_of_squares(entry, length):
        # The entry is a perfect square (at least 1). Only squares below 10**length
        # can be written with `length` digits; Z3 has no table constraint, so the
        # candidates are listed.
        return z3.Or([entry == i * i for i in range(1, math.isqrt(10 ** length - 1) + 1)])

    def one_of_primes(entry, length):
        # The entry is a prime number below 10**length.
        return z3.Or([entry == k for k in range(2, 10 ** length) if is_prime(k)])

    # Across clues.
    solver.add(A[1] == 2 * A[27])        # 1  27 across times two
    solver.add(A[4] == D[4] + 71)        # 4  4 down plus seventy-one
    solver.add(A[7] == D[18] + 4)        # 7  18 down plus four
    solver.add(16 * A[8] == D[6])        # 8  6 down divided by sixteen
    solver.add(A[9] == D[2] - 18)        # 9  2 down minus eighteen
    solver.add(12 * A[10] == 6 * 144)    # 10 dozen in six gross
    solver.add(A[11] == D[5] - 70)       # 11 5 down minus seventy
    solver.add(A[13] == D[26] * A[23])   # 13 26 down times 23 across
    solver.add(A[15] == D[6] - 350)      # 15 6 down minus 350
    solver.add(A[17] == A[25] * A[23])   # 17 25 across times 23 across
    solver.add(one_of_squares(A[20], across_length[20]))  # 20 a square number
    solver.add(one_of_primes(A[23], across_length[23]))   # 23 a prime number
    solver.add(one_of_squares(A[24], across_length[24]))  # 24 a square number
    solver.add(17 * A[25] == A[20])      # 25 20 across divided by seventeen
    solver.add(4 * A[27] == D[6])        # 27 6 down divided by four
    solver.add(A[28] == 4 * 12)          # 28 four dozen
    solver.add(A[29] == 7 * 144)         # 29 seven gross
    solver.add(A[30] == D[22] + 450)     # 30 22 down plus 450

    # Down clues.
    solver.add(D[1] == A[1] + 27)        # 1  1 across plus twenty-seven
    solver.add(D[2] == 5 * 12)           # 2  five dozen
    solver.add(D[3] == A[30] + 888)      # 3  30 across plus 888
    solver.add(D[4] == 2 * A[17])        # 4  two times 17 across
    solver.add(12 * D[5] == A[29])       # 5  29 across divided by twelve
    solver.add(D[6] == A[28] * A[23])    # 6  28 across times 23 across
    solver.add(D[10] == A[10] + 4)       # 10 10 across plus four
    solver.add(D[12] == A[24] * 3)       # 12 three times 24 across
    solver.add(16 * D[14] == A[13])      # 14 13 across divided by sixteen
    solver.add(D[16] == 15 * D[28])      # 16 28 down times fifteen
    solver.add(D[17] == A[13] - 399)     # 17 13 across minus 399
    solver.add(18 * D[18] == A[29])      # 18 29 across divided by eighteen
    solver.add(D[19] == D[22] - 94)      # 19 22 down minus ninety-four
    solver.add(D[20] == A[20] - 9)       # 20 20 across minus nine
    solver.add(D[21] == A[25] - 52)      # 21 25 across minus fifty-two
    solver.add(D[22] == 6 * D[20])       # 22 20 down times six
    solver.add(D[26] == 5 * A[24])       # 26 five times 24 across
    solver.add(D[28] == D[21] + 27)      # 28 21 down plus twenty-seven

    return solver, {"M": M}
