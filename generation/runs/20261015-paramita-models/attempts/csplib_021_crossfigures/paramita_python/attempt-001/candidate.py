# Crossfigures (CSPLib prob021): fill the grid with digits so that every clue
# answer, read across or down, matches its clue. Print the solved grid as M.
# The puzzle is fixed by the problem statement and has no instance fields, so
# the grid and the clues below are the problem's own data.
from paramita.modelling import Bool, And, Or, If

# "X" = black cell, "_" = white cell without a clue number, n = white cell
# that starts clue n (across and/or down).
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
ROWS, COLS = 9, 9


def is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def bits_are(bits, digit):
    """A digit cell (4 bits, little end first) holds the value digit."""
    return And([bits[k] if (digit >> k) & 1 else ~bits[k] for k in range(4)])


def digits_are(cells, digits):
    """Conjunction: the cells hold exactly these digits, left to right."""
    return And([bits_are(cells[k], dg) for k, dg in enumerate(digits)])


def number_digits(n, length):
    s = str(n)
    return [int(ch) for ch in s] if len(s) == length else None


def build(instance):
    # binary digit per white cell: b[(r, c)][k] is bit k of the digit, value <= 9
    b = {}
    for r in range(ROWS):
        for c in range(COLS):
            if GRID[r].split()[c] != "X":
                b[(r, c)] = [Bool(f"b_{r}_{c}_{k}") for k in range(4)]
    cons = []

    # every white cell holds a digit from 0 to 9
    for cell, bits in b.items():
        cons.append(sum((2 ** k) * bits[k] for k in range(4)) <= 9)

    def digit(cell):
        return sum((2 ** k) * b[cell][k] for k in range(4))

    # the answer to a clue is the number its cells spell, read in order
    def runs(across):
        found = {}
        for r in range(ROWS):
            for c in range(COLS):
                tok = GRID[r].split()[c]
                if tok == "X":
                    continue
                # a run starts at a white cell with no white predecessor
                prev = (r, c - 1) if across else (r - 1, c)
                if prev in b:
                    continue
                cells = []
                rr, cc = r, c
                while rr < ROWS and cc < COLS and (rr, cc) in b:
                    cells.append((rr, cc))
                    if across:
                        cc += 1
                    else:
                        rr += 1
                if len(cells) >= 2:
                    assert tok != "_", "unnumbered run start"
                    found[int(tok)] = cells
        return found

    across_cells = runs(True)
    down_cells = runs(False)

    def value(cells):
        """The number spelled by the cells, as a linear integer expression."""
        L = len(cells)
        return sum(10 ** (L - 1 - k) * digit(cell) for k, cell in enumerate(cells))

    A = {n: value(cells) for n, cells in across_cells.items()}
    D = {n: value(cells) for n, cells in down_cells.items()}

    # the clue numbers in the statement are the run starts of the grid
    assert set(across_cells) == {1, 4, 7, 8, 9, 10, 11, 13, 15, 17, 20, 23, 24, 25, 27, 28, 29, 30}
    assert set(down_cells) == {1, 2, 3, 4, 5, 6, 10, 12, 14, 16, 17, 18, 19, 20, 21, 22, 26, 28}

    # Across clues
    # 1 across: 27 across times two
    cons.append(A[1] == 2 * A[27])
    # 4 across: 4 down plus seventy-one
    cons.append(A[4] == D[4] + 71)
    # 7 across: 18 down plus four
    cons.append(A[7] == D[18] + 4)
    # 8 across: 6 down divided by sixteen
    cons.append(16 * A[8] == D[6])
    # 9 across: 2 down minus eighteen
    cons.append(A[9] == D[2] - 18)
    # 10 across: Dozen in six gross (6 * 144 / 12)
    cons.append(A[10] == 72)
    # 11 across: 5 down minus seventy
    cons.append(A[11] == D[5] - 70)

    # 23 across is a two-digit prime; 13 across and 17 across multiply by it.
    # Allowed values are the two-digit primes, so the product is written per prime.
    primes = [p for p in range(10, 100) if is_prime(p)]
    cells23 = across_cells[23]
    # 23 across: A prime number
    cons.append(Or([digits_are([b[c] for c in cells23], number_digits(p, 2)) for p in primes]))

    # 13 across: 26 down times 23 across
    for p in primes:
        cons.append(If(digits_are([b[c] for c in cells23], number_digits(p, 2)), A[13] == p * D[26]))
    # 15 across: 6 down minus 350
    cons.append(A[15] == D[6] - 350)
    # 17 across: 25 across times 23 across
    for p in primes:
        cons.append(If(digits_are([b[c] for c in cells23], number_digits(p, 2)), A[17] == p * A[25]))

    # 20 across: A square number (the answer has four digits)
    squares4 = [s * s for s in range(32, 100)]
    cells20 = across_cells[20]
    cons.append(Or([digits_are([b[c] for c in cells20], number_digits(s, 4)) for s in squares4]))
    # 24 across: A square number (two digits)
    squares2 = [s * s for s in range(4, 10)]
    cells24 = across_cells[24]
    cons.append(Or([digits_are([b[c] for c in cells24], number_digits(s, 2)) for s in squares2]))

    # 25 across: 20 across divided by seventeen
    cons.append(17 * A[25] == A[20])
    # 27 across: 6 down divided by four
    cons.append(4 * A[27] == D[6])
    # 28 across: Four dozen
    cons.append(A[28] == 48)
    # 29 across: Seven gross
    cons.append(A[29] == 1008)
    # 30 across: 22 down plus 450
    cons.append(A[30] == D[22] + 450)

    # Down clues
    # 1 down: 1 across plus twenty-seven
    cons.append(D[1] == A[1] + 27)
    # 2 down: Five dozen
    cons.append(D[2] == 60)
    # 3 down: 30 across plus 888
    cons.append(D[3] == A[30] + 888)
    # 4 down: Two times 17 across
    cons.append(D[4] == 2 * A[17])
    # 5 down: 29 across divided by twelve
    cons.append(12 * D[5] == A[29])
    # 6 down: 28 across times 23 across (28 across is 48)
    cons.append(D[6] == 48 * A[23])
    # 10 down: 10 across plus four
    cons.append(D[10] == A[10] + 4)
    # 12 down: Three times 24 across
    cons.append(D[12] == 3 * A[24])
    # 14 down: 13 across divided by sixteen
    cons.append(16 * D[14] == A[13])
    # 16 down: 28 down times fifteen
    cons.append(D[16] == 15 * D[28])
    # 17 down: 13 across minus 399
    cons.append(D[17] == A[13] - 399)
    # 18 down: 29 across divided by eighteen
    cons.append(18 * D[18] == A[29])
    # 19 down: 22 down minus ninety-four
    cons.append(D[19] == D[22] - 94)
    # 20 down: 20 across minus nine
    cons.append(D[20] == A[20] - 9)
    # 21 down: 25 across minus fifty-two
    cons.append(D[21] == A[25] - 52)
    # 22 down: 20 down times six
    cons.append(D[22] == 6 * D[20])
    # 26 down: Five times 24 across
    cons.append(D[26] == 5 * A[24])
    # 28 down: 21 down plus twenty-seven
    cons.append(D[28] == D[21] + 27)

    # outputs: the digit of each cell, 0 for a black cell
    M = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            row.append(digit((r, c)) if (r, c) in b else 0)
        M.append(row)
    return cons, {"M": M}
