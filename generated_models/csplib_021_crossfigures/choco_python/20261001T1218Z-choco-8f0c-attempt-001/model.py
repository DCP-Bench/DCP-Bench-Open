# Crossfigure (CSPLib 21): the numerical crossword. Fill the 9x9 grid with digits so that every
# across and down entry is a number satisfying its clue; black squares hold 0.
import math

from pychoco.model import Model

# The puzzle has no instance data: the grid, the entry positions and the clues are its statement.
N = 9
D = 9999  # the longest entry has 4 digits
B = 1  # black square
BLACK = [[0, 0, 0, 0, B, 0, 0, 0, 0],
         [0, 0, B, 0, 0, 0, B, 0, 0],
         [0, B, 0, 0, B, 0, 0, B, 0],
         [0, 0, 0, 0, B, 0, 0, 0, 0],
         [B, 0, B, B, B, B, B, 0, B],
         [0, 0, 0, 0, B, 0, 0, 0, 0],
         [0, B, 0, 0, B, 0, 0, B, 0],
         [0, 0, B, 0, 0, 0, B, 0, 0],
         [0, 0, 0, 0, B, 0, 0, 0, 0]]
# entry number: (length, row, column), 1-based as in the puzzle
ACROSS = {1: (4, 1, 1), 4: (4, 1, 6), 7: (2, 2, 1), 8: (3, 2, 4), 9: (2, 2, 8), 10: (2, 3, 3),
          11: (2, 3, 6), 13: (4, 4, 1), 15: (4, 4, 6), 17: (4, 6, 1), 20: (4, 6, 6),
          23: (2, 7, 3), 24: (2, 7, 6), 25: (2, 8, 1), 27: (3, 8, 4), 28: (2, 8, 8),
          29: (4, 9, 1), 30: (4, 9, 6)}
DOWN = {1: (4, 1, 1), 2: (2, 1, 2), 3: (4, 1, 4), 4: (4, 1, 6), 5: (2, 1, 8), 6: (4, 1, 9),
        10: (2, 3, 3), 12: (2, 3, 7), 14: (3, 4, 2), 16: (3, 4, 8), 17: (4, 6, 1), 18: (2, 6, 3),
        19: (4, 6, 4), 20: (4, 6, 6), 21: (2, 6, 7), 22: (4, 6, 9), 26: (2, 8, 2), 28: (2, 8, 8)}


def is_prime(v):
    return v >= 2 and all(v % k for k in range(2, math.isqrt(v) + 1))


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # M[i][j] = the digit in row i, column j; black squares hold 0
    M = [[model.intvar(0, 9, name=f"M_{i}_{j}") for j in range(N)] for i in range(N)]
    for i in range(N):
        for j in range(N):
            if BLACK[i][j]:
                model.arithm(M[i][j], "=", 0).post()

    # A[k] / Dn[k] = the number written in across / down entry k: its digits, read left to right
    # or top to bottom, spell the number.
    A = {k: model.intvar(0, D, name=f"A{k}", bounded_domain=True) for k in ACROSS}
    Dn = {k: model.intvar(0, D, name=f"D{k}", bounded_domain=True) for k in DOWN}
    for entries, var, di, dj in ((ACROSS, A, 0, 1), (DOWN, Dn, 1, 0)):
        for k, (length, row, col) in entries.items():
            cells = [M[row - 1 + di * t][col - 1 + dj * t] for t in range(length)]
            model.scalar(cells, [10 ** (length - t - 1) for t in range(length)], "=", var[k]).post()

    def eq(lhs, coeffs_vars, const=0):
        """lhs == sum(c * v) + const, as one linear equality."""
        coeffs = [1] + [-c for c, _ in coeffs_vars]
        model.scalar([lhs] + [v for _, v in coeffs_vars], coeffs, "=", const).post()

    def product(result, x, y):
        model.times(x, y, result).post()

    squares = [r * r for r in range(1, math.isqrt(D) + 2)]
    primes = [v for v in range(2, D + 1) if is_prime(v)]

    # Across clues
    eq(A[1], [(2, A[27])])                 # 1: 27 across times two
    eq(A[4], [(1, Dn[4])], 71)             # 4: 4 down plus seventy-one
    eq(A[7], [(1, Dn[18])], 4)             # 7: 18 down plus four
    eq(Dn[6], [(16, A[8])])                # 8: 6 down divided by sixteen
    eq(A[9], [(1, Dn[2])], -18)            # 9: 2 down minus eighteen
    model.arithm(A[10], "=", 6 * 144 // 12).post()  # 10: dozens in six gross
    eq(A[11], [(1, Dn[5])], -70)           # 11: 5 down minus seventy
    product(A[13], Dn[26], A[23])          # 13: 26 down times 23 across
    eq(A[15], [(1, Dn[6])], -350)          # 15: 6 down minus 350
    product(A[17], A[25], A[23])           # 17: 25 across times 23 across
    model.member(A[20], squares).post()    # 20: a square number
    model.member(A[23], primes).post()     # 23: a prime number
    model.member(A[24], squares).post()    # 24: a square number
    eq(A[20], [(17, A[25])])               # 25: 20 across divided by seventeen
    eq(Dn[6], [(4, A[27])])                # 27: 6 down divided by four
    model.arithm(A[28], "=", 4 * 12).post()   # 28: four dozen
    model.arithm(A[29], "=", 7 * 144).post()  # 29: seven gross
    eq(A[30], [(1, Dn[22])], 450)          # 30: 22 down plus 450

    # Down clues
    eq(Dn[1], [(1, A[1])], 27)             # 1: 1 across plus twenty-seven
    model.arithm(Dn[2], "=", 5 * 12).post()  # 2: five dozen
    eq(Dn[3], [(1, A[30])], 888)           # 3: 30 across plus 888
    eq(Dn[4], [(2, A[17])])                # 4: two times 17 across
    eq(A[29], [(12, Dn[5])])               # 5: 29 across divided by twelve
    product(Dn[6], A[28], A[23])           # 6: 28 across times 23 across
    eq(Dn[10], [(1, A[10])], 4)            # 10: 10 across plus four
    eq(Dn[12], [(3, A[24])])               # 12: three times 24 across
    eq(A[13], [(16, Dn[14])])              # 14: 13 across divided by sixteen
    eq(Dn[16], [(15, Dn[28])])             # 16: 28 down times fifteen
    eq(Dn[17], [(1, A[13])], -399)         # 17: 13 across minus 399
    eq(A[29], [(18, Dn[18])])              # 18: 29 across divided by eighteen
    eq(Dn[19], [(1, Dn[22])], -94)         # 19: 22 down minus ninety-four
    eq(Dn[20], [(1, A[20])], -9)           # 20: 20 across minus nine
    eq(Dn[21], [(1, A[25])], -52)          # 21: 25 across minus fifty-two
    eq(Dn[22], [(6, Dn[20])])              # 22: 20 down times six
    eq(Dn[26], [(5, A[24])])               # 26: five times 24 across
    eq(Dn[28], [(1, Dn[21])], 27)          # 28: 21 down plus twenty-seven

    return model, {"M": M}
