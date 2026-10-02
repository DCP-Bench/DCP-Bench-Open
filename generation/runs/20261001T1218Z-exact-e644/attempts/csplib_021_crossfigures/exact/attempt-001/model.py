# Crossfigures (CSPLib prob021): a numerical crossword. Fill the white cells of a 9x9 grid with
# digits so that every across and down entry is a number that satisfies its clue (for example
# "27 across times two", "a square number", "a prime number"). Black cells hold 0.
from math import isqrt

from exact import Exact


def build(instance):
    # This problem has no instance data: the grid, the entries and the clues below are the puzzle.
    n = 9
    # '#' is a black box, '.' a white cell
    layout = ["....#....",
              "..#...#..",
              ".#..#..#.",
              "....#....",
              "#.#####.#",
              "....#....",
              ".#..#..#.",
              "..#...#..",
              "....#...."]
    # entries: name -> (length, row, column), rows and columns counted from 1 as in the clue numbers
    across = {"A1": (4, 1, 1), "A4": (4, 1, 6), "A7": (2, 2, 1), "A8": (3, 2, 4), "A9": (2, 2, 8),
              "A10": (2, 3, 3), "A11": (2, 3, 6), "A13": (4, 4, 1), "A15": (4, 4, 6),
              "A17": (4, 6, 1), "A20": (4, 6, 6), "A23": (2, 7, 3), "A24": (2, 7, 6),
              "A25": (2, 8, 1), "A27": (3, 8, 4), "A28": (2, 8, 8), "A29": (4, 9, 1),
              "A30": (4, 9, 6)}
    down = {"D1": (4, 1, 1), "D2": (2, 1, 2), "D3": (4, 1, 4), "D4": (4, 1, 6), "D5": (2, 1, 8),
            "D6": (4, 1, 9), "D10": (2, 3, 3), "D12": (2, 3, 7), "D14": (3, 4, 2),
            "D16": (3, 4, 8), "D17": (4, 6, 1), "D18": (2, 6, 3), "D19": (4, 6, 4),
            "D20": (4, 6, 6), "D21": (2, 6, 7), "D22": (4, 6, 9), "D26": (2, 8, 2),
            "D28": (2, 8, 8)}

    solver = Exact()

    # M[i][j] is the digit in cell (i, j); a black cell holds 0, a white cell a digit 0..9.
    M = [[f"M_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(M[i][j], 0, 0 if layout[i][j] == "#" else 9)

    # Each entry is a variable holding the number its digits spell (leading zeros are allowed, as
    # in the reference). The digits are linked to the number: number = sum of 10^k * digit.
    def entry(name, length, cells):
        solver.addVariable(name, 0, 10 ** length - 1)
        solver.addConstraint([(1, name)] + [(-(10 ** (length - 1 - k)), cells[k])
                                            for k in range(length)], True, 0, True, 0)

    for name, (length, row, col) in across.items():
        entry(name, length, [M[row - 1][col - 1 + k] for k in range(length)])
    for name, (length, row, col) in down.items():
        entry(name, length, [M[row - 1 + k][col - 1] for k in range(length)])
    length_of = {name: spec[0] for name, spec in {**across, **down}.items()}

    def equals(terms, value=0):
        # sum of coefficient * entry == value
        solver.addConstraint(terms, True, value, True, value)

    def times(result, factor_a, factor_b):
        # result == factor_a * factor_b, using Exact's multiplication constraint
        solver.addMultiplication([factor_a, factor_b], True, result, True, result)

    def one_of(name, allowed, label):
        # the entry takes one of the allowed values: a 0/1 variable per value that fits in the
        # entry's digits says which value is taken
        allowed = [v for v in allowed if v <= 10 ** length_of[name] - 1]
        picks = [f"{name}_is_{label}_{v}" for v in allowed]
        for pick in picks:
            solver.addVariable(pick, 0, 1)
        solver.addConstraint([(1, pick) for pick in picks], True, 1, True, 1)
        solver.addConstraint([(v, pick) for v, pick in zip(allowed, picks)] + [(-1, name)],
                             True, 0, True, 0)

    # The squares and the primes up to 9999, the largest number any entry can spell (4 digits).
    top = 9999
    squares = [i * i for i in range(1, isqrt(top) + 2)]
    primes = [p for p in range(2, top + 1)
              if all(p % d for d in range(2, isqrt(p) + 1))]

    # Across clues
    # 1: 27 across times two
    equals([(1, "A1"), (-2, "A27")])
    # 4: 4 down plus seventy-one
    equals([(1, "A4"), (-1, "D4")], 71)
    # 7: 18 down plus four
    equals([(1, "A7"), (-1, "D18")], 4)
    # 8: 6 down divided by sixteen
    equals([(16, "A8"), (-1, "D6")])
    # 9: 2 down minus eighteen
    equals([(1, "A9"), (-1, "D2")], -18)
    # 10: a dozen in six gross (6 * 144 / 12)
    equals([(12, "A10")], 6 * 144)
    # 11: 5 down minus seventy
    equals([(1, "A11"), (-1, "D5")], -70)
    # 13: 26 down times 23 across
    times("A13", "D26", "A23")
    # 15: 6 down minus 350
    equals([(1, "A15"), (-1, "D6")], -350)
    # 17: 25 across times 23 across
    times("A17", "A25", "A23")
    # 20: a square number
    one_of("A20", squares, "square")
    # 23: a prime number
    one_of("A23", primes, "prime")
    # 24: a square number
    one_of("A24", squares, "square")
    # 25: 20 across divided by seventeen
    equals([(17, "A25"), (-1, "A20")])
    # 27: 6 down divided by four
    equals([(4, "A27"), (-1, "D6")])
    # 28: four dozen
    equals([(1, "A28")], 4 * 12)
    # 29: seven gross
    equals([(1, "A29")], 7 * 144)
    # 30: 22 down plus 450
    equals([(1, "A30"), (-1, "D22")], 450)

    # Down clues
    # 1: 1 across plus twenty-seven
    equals([(1, "D1"), (-1, "A1")], 27)
    # 2: five dozen
    equals([(1, "D2")], 5 * 12)
    # 3: 30 across plus 888
    equals([(1, "D3"), (-1, "A30")], 888)
    # 4: two times 17 across
    equals([(1, "D4"), (-2, "A17")])
    # 5: 29 across divided by twelve
    equals([(12, "D5"), (-1, "A29")])
    # 6: 28 across times 23 across
    times("D6", "A28", "A23")
    # 10: 10 across plus four
    equals([(1, "D10"), (-1, "A10")], 4)
    # 12: three times 24 across
    equals([(1, "D12"), (-3, "A24")])
    # 14: 13 across divided by sixteen
    equals([(16, "D14"), (-1, "A13")])
    # 16: 28 down times fifteen
    equals([(1, "D16"), (-15, "D28")])
    # 17: 13 across minus 399
    equals([(1, "D17"), (-1, "A13")], -399)
    # 18: 29 across divided by eighteen
    equals([(18, "D18"), (-1, "A29")])
    # 19: 22 down minus ninety-four
    equals([(1, "D19"), (-1, "D22")], -94)
    # 20: 20 across minus nine
    equals([(1, "D20"), (-1, "A20")], -9)
    # 21: 25 across minus fifty-two
    equals([(1, "D21"), (-1, "A25")], -52)
    # 22: 20 down times six
    equals([(1, "D22"), (-6, "D20")])
    # 26: five times 24 across
    equals([(1, "D26"), (-5, "A24")])
    # 28: 21 down plus twenty-seven
    equals([(1, "D28"), (-1, "D21")], 27)

    return solver, {"M": M}
