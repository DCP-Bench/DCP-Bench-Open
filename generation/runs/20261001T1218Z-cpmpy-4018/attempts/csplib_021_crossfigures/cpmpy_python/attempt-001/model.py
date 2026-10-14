# CSPLib prob021, crossfigure: a numerical crossword. Digits are placed in a 9x9 grid so that every
# across and down entry spells a number that satisfies its arithmetic clue (for example "27 across
# times two", "a prime number", "a square number").
import math

import cpmpy as cp


def build(instance):
    # The grid and the clues are the problem statement itself (the instance has no fields), so
    # they are mirrored here from the problem description.
    grid = ["....#....",
            "..#...#..",
            ".#..#..#.",
            "....#....",
            "#.#####.#",
            "....#....",
            ".#..#..#.",
            "..#...#..",
            "....#...."]  # '#' = black cell
    n = len(grid)

    # Entries as clue number -> (length in digits, row, column), rows and columns counted from 1.
    across_entries = {1: (4, 1, 1), 4: (4, 1, 6), 7: (2, 2, 1), 8: (3, 2, 4), 9: (2, 2, 8),
                      10: (2, 3, 3), 11: (2, 3, 6), 13: (4, 4, 1), 15: (4, 4, 6), 17: (4, 6, 1),
                      20: (4, 6, 6), 23: (2, 7, 3), 24: (2, 7, 6), 25: (2, 8, 1), 27: (3, 8, 4),
                      28: (2, 8, 8), 29: (4, 9, 1), 30: (4, 9, 6)}
    down_entries = {1: (4, 1, 1), 2: (2, 1, 2), 3: (4, 1, 4), 4: (4, 1, 6), 5: (2, 1, 8),
                    6: (4, 1, 9), 10: (2, 3, 3), 12: (2, 3, 7), 14: (3, 4, 2), 16: (3, 4, 8),
                    17: (4, 6, 1), 18: (2, 6, 3), 19: (4, 6, 4), 20: (4, 6, 6), 21: (2, 6, 7),
                    22: (4, 6, 9), 26: (2, 8, 2), 28: (2, 8, 8)}

    # Numbers a clue may be: all primes and all squares below 10000 (the longest entry has 4 digits).
    max_number = 9999
    primes = [p for p in range(2, max_number + 1)
              if all(p % d for d in range(2, math.isqrt(p) + 1))]
    squares = [i * i for i in range(1, math.isqrt(max_number) + 1)]

    # M[r][c] = digit in cell (r, c); black cells hold 0
    M = cp.intvar(0, 9, shape=(n, n), name="M")

    model = cp.Model()

    # Black cells carry no digit.
    for r in range(n):
        for c in range(n):
            if grid[r][c] == "#":
                model += M[r, c] == 0

    # Each entry is a variable equal to the number its digits spell (leading zeros allowed).
    # A[k] / D[k] = value of the across / down entry numbered k.
    A, D = {}, {}
    for entries, values, direction in ((across_entries, A, "A"), (down_entries, D, "D")):
        for k, (length, row, col) in entries.items():
            if direction == "A":
                cells = [M[row - 1, col - 1 + i] for i in range(length)]
            else:
                cells = [M[row - 1 + i, col - 1] for i in range(length)]
            values[k] = cp.intvar(0, 10 ** length - 1, name=f"{direction}{k}")
            model += values[k] == cp.sum([10 ** (length - 1 - i) * cells[i] for i in range(length)])

    # Across clues.
    model += A[1] == 2 * A[27]            # 27 across times two
    model += A[4] == D[4] + 71            # 4 down plus seventy-one
    model += A[7] == D[18] + 4            # 18 down plus four
    model += 16 * A[8] == D[6]            # 6 down divided by sixteen
    model += A[9] == D[2] - 18            # 2 down minus eighteen
    model += 12 * A[10] == 6 * 144        # a dozen in six gross
    model += A[11] == D[5] - 70           # 5 down minus seventy
    model += A[13] == D[26] * A[23]       # 26 down times 23 across
    model += A[15] == D[6] - 350          # 6 down minus 350
    model += A[17] == A[25] * A[23]       # 25 across times 23 across
    model += cp.InDomain(A[20], squares)  # a square number
    model += cp.InDomain(A[23], primes)   # a prime number
    model += cp.InDomain(A[24], squares)  # a square number
    model += 17 * A[25] == A[20]          # 20 across divided by seventeen
    model += 4 * A[27] == D[6]            # 6 down divided by four
    model += A[28] == 4 * 12              # four dozen
    model += A[29] == 7 * 144             # seven gross
    model += A[30] == D[22] + 450         # 22 down plus 450

    # Down clues.
    model += D[1] == A[1] + 27            # 1 across plus twenty-seven
    model += D[2] == 5 * 12               # five dozen
    model += D[3] == A[30] + 888          # 30 across plus 888
    model += D[4] == 2 * A[17]            # two times 17 across
    model += 12 * D[5] == A[29]           # 29 across divided by twelve
    model += D[6] == A[28] * A[23]        # 28 across times 23 across
    model += D[10] == A[10] + 4           # 10 across plus four
    model += D[12] == A[24] * 3           # three times 24 across
    model += 16 * D[14] == A[13]          # 13 across divided by sixteen
    model += D[16] == 15 * D[28]          # 28 down times fifteen
    model += D[17] == A[13] - 399         # 13 across minus 399
    model += 18 * D[18] == A[29]          # 29 across divided by eighteen
    model += D[19] == D[22] - 94          # 22 down minus ninety-four
    model += D[20] == A[20] - 9           # 20 across minus nine
    model += D[21] == A[25] - 52          # 25 across minus fifty-two
    model += D[22] == 6 * D[20]           # 20 down times six
    model += D[26] == 5 * A[24]           # five times 24 across
    model += D[28] == D[21] + 27          # 21 down plus twenty-seven

    return model, {"M": M}
