# Crossfigures (CSPLib 21): the numerical equivalent of a crossword. Fill a 9x9 grid (black
# cells hold 0) with digits so that every across and down clue, a number written in the grid,
# has the value its clue states (a multiple or sum of other answers, a dozen, a square, a prime).
from math import isqrt

from pysat.formula import CNF, IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    # The grid and the clues belong to the problem (there is no instance data).
    # '#' is a black box, '.' a cell that takes a digit.
    layout = ["....#....",
              "..#...#..",
              ".#..#..#.",
              "....#....",
              "#.#####.#",
              "....#....",
              ".#..#..#.",
              "..#...#..",
              "....#...."]
    n = len(layout)
    # clue number -> (number of digits, first row, first column), 1-based as in the puzzle
    across_cells = {1: (4, 1, 1), 4: (4, 1, 6), 7: (2, 2, 1), 8: (3, 2, 4), 9: (2, 2, 8),
                    10: (2, 3, 3), 11: (2, 3, 6), 13: (4, 4, 1), 15: (4, 4, 6), 17: (4, 6, 1),
                    20: (4, 6, 6), 23: (2, 7, 3), 24: (2, 7, 6), 25: (2, 8, 1), 27: (3, 8, 4),
                    28: (2, 8, 8), 29: (4, 9, 1), 30: (4, 9, 6)}
    down_cells = {1: (4, 1, 1), 2: (2, 1, 2), 3: (4, 1, 4), 4: (4, 1, 6), 5: (2, 1, 8),
                  6: (4, 1, 9), 10: (2, 3, 3), 12: (2, 3, 7), 14: (3, 4, 2), 16: (3, 4, 8),
                  17: (4, 6, 1), 18: (2, 6, 3), 19: (4, 6, 4), 20: (4, 6, 6), 21: (2, 6, 7),
                  22: (4, 6, 9), 26: (2, 8, 2), 28: (2, 8, 8)}

    pool = IDPool()
    # M[i][j] = the digit in row i, column j (0-based); black boxes hold 0
    M = [[Integer(f"M{i}_{j}", 0, 9, vpool=pool) for j in range(n)] for i in range(n)]
    engine = IntegerEngine(vars=[cell for row in M for cell in row], vpool=pool)
    cnf = engine.clausify()

    # black boxes hold 0
    for i in range(n):
        for j in range(n):
            if layout[i][j] == "#":
                cnf.append([M[i][j].equals(0)])

    # For every clue, is_value[clue][v] is a literal that is true exactly when the digits of the
    # clue's cells, read as a number (leading zeros allowed, as in the reference), are v.
    # PySAT cannot add or multiply variables, so the clue answers are linked to each other through
    # these literals value by value (see the clue constraints below).
    is_value = {}
    length = {}

    def define(name, digits, row, col, step):
        cells = [M[row - 1 + step[0] * k][col - 1 + step[1] * k] for k in range(digits)]
        length[name] = digits
        is_value[name] = []
        for v in range(10 ** digits):
            literal = pool.id(("value", name, v))
            is_value[name].append(literal)
            spelled = str(v).zfill(digits)
            # the cells spell v exactly when the literal holds
            cnf.append([-cell.equals(int(d)) for cell, d in zip(cells, spelled)] + [literal])
            for cell, d in zip(cells, spelled):
                cnf.append([-literal, cell.equals(int(d))])

    for number, (digits, row, col) in across_cells.items():
        define(f"A{number}", digits, row, col, (0, 1))
    for number, (digits, row, col) in down_cells.items():
        define(f"D{number}", digits, row, col, (1, 0))

    def linear(a, x, b, y, c):
        """a * x == b * y + c for two clue answers x and y."""
        for value in range(10 ** length[y]):
            rhs = b * value + c
            if rhs % a == 0 and 0 <= rhs // a < 10 ** length[x]:
                cnf.append([-is_value[y][value], is_value[x][rhs // a]])
            else:
                cnf.append([-is_value[y][value]])
        for value in range(10 ** length[x]):
            lhs = a * value - c
            if lhs % b == 0 and 0 <= lhs // b < 10 ** length[y]:
                cnf.append([-is_value[x][value], is_value[y][lhs // b]])
            else:
                cnf.append([-is_value[x][value]])

    def fixed(a, x, rhs):
        """a * x == rhs for a clue answer x (rhs is a constant of the clue)."""
        if rhs % a == 0 and 0 <= rhs // a < 10 ** length[x]:
            cnf.append([is_value[x][rhs // a]])
        else:
            cnf.append([])

    def product(x, y, z):
        """x == y * z for three clue answers."""
        for u in range(10 ** length[y]):
            for v in range(10 ** length[z]):
                if u * v < 10 ** length[x]:
                    cnf.append([-is_value[y][u], -is_value[z][v], is_value[x][u * v]])
                else:
                    cnf.append([-is_value[y][u], -is_value[z][v]])

    def member(x, values):
        """x is one of the given values."""
        cnf.append([is_value[x][v] for v in values if v < 10 ** length[x]])

    def is_prime(k):
        return k >= 2 and all(k % d for d in range(2, isqrt(k) + 1))

    largest = 9999  # the longest clue has four digits
    primes = [k for k in range(2, largest + 1) if is_prime(k)]
    squares = [k * k for k in range(1, 101)]  # 1 .. 10000

    # Across clues
    linear(1, "A1", 2, "A27", 0)             # 1  27 across times two
    linear(1, "A4", 1, "D4", 71)             # 4  4 down plus seventy-one
    linear(1, "A7", 1, "D18", 4)             # 7  18 down plus four
    linear(16, "A8", 1, "D6", 0)             # 8  6 down divided by sixteen
    linear(1, "A9", 1, "D2", -18)            # 9  2 down minus eighteen
    fixed(12, "A10", 6 * 144)                # 10 dozen in six gross
    linear(1, "A11", 1, "D5", -70)           # 11 5 down minus seventy
    product("A13", "D26", "A23")             # 13 26 down times 23 across
    linear(1, "A15", 1, "D6", -350)          # 15 6 down minus 350
    product("A17", "A25", "A23")             # 17 25 across times 23 across
    member("A20", squares)                   # 20 a square number
    member("A23", primes)                    # 23 a prime number
    member("A24", squares)                   # 24 a square number
    linear(17, "A25", 1, "A20", 0)           # 25 20 across divided by seventeen
    linear(4, "A27", 1, "D6", 0)             # 27 6 down divided by four
    fixed(1, "A28", 4 * 12)                  # 28 four dozen
    fixed(1, "A29", 7 * 144)                 # 29 seven gross
    linear(1, "A30", 1, "D22", 450)          # 30 22 down plus 450

    # Down clues
    linear(1, "D1", 1, "A1", 27)             # 1  1 across plus twenty-seven
    fixed(1, "D2", 5 * 12)                   # 2  five dozen
    linear(1, "D3", 1, "A30", 888)           # 3  30 across plus 888
    linear(1, "D4", 2, "A17", 0)             # 4  two times 17 across
    linear(12, "D5", 1, "A29", 0)            # 5  29 across divided by twelve
    product("D6", "A28", "A23")              # 6  28 across times 23 across
    linear(1, "D10", 1, "A10", 4)            # 10 10 across plus four
    linear(1, "D12", 3, "A24", 0)            # 12 three times 24 across
    linear(16, "D14", 1, "A13", 0)           # 14 13 across divided by sixteen
    linear(1, "D16", 15, "D28", 0)           # 16 28 down times fifteen
    linear(1, "D17", 1, "A13", -399)         # 17 13 across minus 399
    linear(18, "D18", 1, "A29", 0)           # 18 29 across divided by eighteen
    linear(1, "D19", 1, "D22", -94)          # 19 22 down minus ninety-four
    linear(1, "D20", 1, "A20", -9)           # 20 20 across minus nine
    linear(1, "D21", 1, "A25", -52)          # 21 25 across minus fifty-two
    linear(1, "D22", 6, "D20", 0)            # 22 20 down times six
    linear(1, "D26", 5, "A24", 0)            # 26 five times 24 across
    linear(1, "D28", 1, "D21", 27)           # 28 21 down plus twenty-seven

    return cnf, {"M": M}
