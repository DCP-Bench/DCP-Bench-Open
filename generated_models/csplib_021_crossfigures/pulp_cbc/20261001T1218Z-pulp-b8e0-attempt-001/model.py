"""Crossfigures (CSPLib 21): the numerical equivalent of a crossword. Fill a 9 by 9 grid with
digits so that the numbers read across and down satisfy the given clues.

The model reports the grid M, with 0 in the black squares.
"""
import math

import pulp


def build(instance):
    del instance  # the puzzle has no instance data; its grid and clues are below

    n = 9

    # The grid, mirrored from the reference: 0 marks a black square.
    black = [
        "....#....",
        "..#...#..",
        ".#..#..#.",
        "....#....",
        "#.#####.#",
        "....#....",
        ".#..#..#.",
        "..#...#..",
        "....#....",
    ]

    problem = pulp.LpProblem("crossfigures", pulp.LpMinimize)  # satisfaction

    # M[i][j] is the digit in row i, column j; black squares hold 0
    M = [[pulp.LpVariable(f"M_{i}_{j}", 0, 9, cat="Integer") for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            if black[i][j] == "#":
                problem += M[i][j] == 0

    # A number of the given length read from the grid, starting at (row, col) counted
    # from 1 as in the puzzle, across or down.
    def across(length, row, col):
        return pulp.lpSum(10 ** (length - 1 - k) * M[row - 1][col - 1 + k] for k in range(length))

    def down(length, row, col):
        return pulp.lpSum(10 ** (length - 1 - k) * M[row - 1 + k][col - 1] for k in range(length))

    A1, A4, A7, A8 = across(4, 1, 1), across(4, 1, 6), across(2, 2, 1), across(3, 2, 4)
    A9, A10, A11, A13 = across(2, 2, 8), across(2, 3, 3), across(2, 3, 6), across(4, 4, 1)
    A15, A17, A20, A23 = across(4, 4, 6), across(4, 6, 1), across(4, 6, 6), across(2, 7, 3)
    A24, A25, A27, A28 = across(2, 7, 6), across(2, 8, 1), across(3, 8, 4), across(2, 8, 8)
    A29, A30 = across(4, 9, 1), across(4, 9, 6)

    D1, D2, D3, D4 = down(4, 1, 1), down(2, 1, 2), down(4, 1, 4), down(4, 1, 6)
    D5, D6, D10, D12 = down(2, 1, 8), down(4, 1, 9), down(2, 3, 3), down(2, 3, 7)
    D14, D16, D17, D18 = down(3, 4, 2), down(3, 4, 8), down(4, 6, 1), down(2, 6, 3)
    D19, D20, D21, D22 = down(4, 6, 4), down(4, 6, 6), down(2, 6, 7), down(4, 6, 9)
    D26, D28 = down(2, 8, 2), down(2, 8, 8)

    # 23 across is a prime number. Products with it are not linear, so it is chosen from
    # the two-digit primes and each product is built from that choice.
    primes = [p for p in range(2, 100) if all(p % q for q in range(2, math.isqrt(p) + 1))]
    prime = {p: pulp.LpVariable(f"prime_{p}", cat="Binary") for p in primes}
    problem += pulp.lpSum(prime.values()) == 1
    problem += A23 == pulp.lpSum(p * var for p, var in prime.items())

    def times_a23(other, name, other_top):
        """other * A23, for an expression other in 0..other_top: share[p] is other when
        prime p is chosen and 0 otherwise (the standard product of a binary and a bounded
        integer), and the product is the sum of p * share[p]."""
        share = {p: pulp.LpVariable(f"{name}_{p}", 0, other_top) for p in primes}
        for p, var in prime.items():
            problem.addConstraint(share[p] <= other_top * var)
            problem.addConstraint(share[p] <= other)
            problem.addConstraint(share[p] >= other - other_top * (1 - var))
        return pulp.lpSum(p * share[p] for p in primes)

    # 20 across and 24 across are square numbers (of a root at least 1, as in the
    # reference); each is chosen from the squares that fit its digits.
    def square_of(expression, digits, name):
        roots = range(1, math.isqrt(10 ** digits - 1) + 1)
        root = {r: pulp.LpVariable(f"{name}_{r}", cat="Binary") for r in roots}
        problem.addConstraint(pulp.lpSum(root.values()) == 1)
        problem.addConstraint(expression == pulp.lpSum(r * r * var for r, var in root.items()))

    # Across
    problem += A1 == 2 * A27                     # 1: 27 across times two
    problem += A4 == D4 + 71                     # 4: 4 down plus seventy-one
    problem += A7 == D18 + 4                     # 7: 18 down plus four
    problem += 16 * A8 == D6                     # 8: 6 down divided by sixteen
    problem += A9 == D2 - 18                     # 9: 2 down minus eighteen
    problem += 12 * A10 == 6 * 144               # 10: dozen in six gross
    problem += A11 == D5 - 70                    # 11: 5 down minus seventy
    problem += A13 == times_a23(D26, "d26xa23", 99)  # 13: 26 down times 23 across
    problem += A15 == D6 - 350                   # 15: 6 down minus 350
    problem += A17 == times_a23(A25, "a25xa23", 99)  # 17: 25 across times 23 across
    square_of(A20, 4, "root20")                  # 20: a square number
    # 23: a prime number (stated above)
    square_of(A24, 2, "root24")                  # 24: a square number
    problem += 17 * A25 == A20                   # 25: 20 across divided by seventeen
    problem += 4 * A27 == D6                     # 27: 6 down divided by four
    problem += A28 == 4 * 12                     # 28: four dozen
    problem += A29 == 7 * 144                    # 29: seven gross
    problem += A30 == D22 + 450                  # 30: 22 down plus 450

    # Down
    problem += D1 == A1 + 27                     # 1: 1 across plus twenty-seven
    problem += D2 == 5 * 12                      # 2: five dozen
    problem += D3 == A30 + 888                   # 3: 30 across plus 888
    problem += D4 == 2 * A17                     # 4: two times 17 across
    problem += 12 * D5 == A29                    # 5: 29 across divided by twelve
    # 6: 28 across times 23 across; 28 across is fixed at four dozen by its own clue,
    # so the product is 48 times 23 across
    problem += D6 == 4 * 12 * A23
    problem += D10 == A10 + 4                    # 10: 10 across plus four
    problem += D12 == 3 * A24                    # 12: three times 24 across
    problem += 16 * D14 == A13                   # 14: 13 across divided by sixteen
    problem += D16 == 15 * D28                   # 16: 28 down times fifteen
    problem += D17 == A13 - 399                  # 17: 13 across minus 399
    problem += 18 * D18 == A29                   # 18: 29 across divided by eighteen
    problem += D19 == D22 - 94                   # 19: 22 down minus ninety-four
    problem += D20 == A20 - 9                    # 20: 20 across minus nine
    problem += D21 == A25 - 52                   # 21: 25 across minus fifty-two
    problem += D22 == 6 * D20                    # 22: 20 down times six
    problem += D26 == 5 * A24                    # 26: five times 24 across
    problem += D28 == D21 + 27                   # 28: 21 down plus twenty-seven

    return problem, {"M": M}
