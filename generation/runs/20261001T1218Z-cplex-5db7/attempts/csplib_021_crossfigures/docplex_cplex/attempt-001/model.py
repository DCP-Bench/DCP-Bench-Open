"""CSPLib 21, crossfigures: fill a 9 x 9 grid with digits so that the numbers read across
and down answer the given arithmetic clues.
"""
import math

from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data. The grid, the clue positions and the clues are fixed
    # by the problem statement and mirrored from the reference.
    n = 9
    B = -2  # black square
    Z = -1  # white square
    valid = [[Z, Z, Z, Z, B, Z, Z, Z, Z],
             [Z, Z, B, Z, Z, Z, B, Z, Z],
             [Z, B, Z, Z, B, Z, Z, B, Z],
             [Z, Z, Z, Z, B, Z, Z, Z, Z],
             [B, Z, B, B, B, B, B, Z, B],
             [Z, Z, Z, Z, B, Z, Z, Z, Z],
             [Z, B, Z, Z, B, Z, Z, B, Z],
             [Z, Z, B, Z, Z, Z, B, Z, Z],
             [Z, Z, Z, Z, B, Z, Z, Z, Z]]
    # Clue -> (length, row, column), 1-based as in the puzzle.
    across_at = {1: (4, 1, 1), 4: (4, 1, 6), 7: (2, 2, 1), 8: (3, 2, 4), 9: (2, 2, 8),
                 10: (2, 3, 3), 11: (2, 3, 6), 13: (4, 4, 1), 15: (4, 4, 6), 17: (4, 6, 1),
                 20: (4, 6, 6), 23: (2, 7, 3), 24: (2, 7, 6), 25: (2, 8, 1), 27: (3, 8, 4),
                 28: (2, 8, 8), 29: (4, 9, 1), 30: (4, 9, 6)}
    down_at = {1: (4, 1, 1), 2: (2, 1, 2), 3: (4, 1, 4), 4: (4, 1, 6), 5: (2, 1, 8),
               6: (4, 1, 9), 10: (2, 3, 3), 12: (2, 3, 7), 14: (3, 4, 2), 16: (3, 4, 8),
               17: (4, 6, 1), 18: (2, 6, 3), 19: (4, 6, 4), 20: (4, 6, 6), 21: (2, 6, 7),
               22: (4, 6, 9), 26: (2, 8, 2), 28: (2, 8, 8)}

    model = Model("crossfigures")

    # M[i][j] is the digit in cell (i, j); a black square holds 0.
    M = [[model.integer_var(0, 0 if valid[i][j] == B else 9, name=f"M_{i}_{j}")
          for j in range(n)] for i in range(n)]

    # The number written by a clue's digits, most significant first (built fresh on every
    # call, so no expression is shared between constraints).
    def A(k):
        length, row, col = across_at[k]
        return model.sum(10 ** (length - 1 - t) * M[row - 1][col - 1 + t] for t in range(length))

    def D(k):
        length, row, col = down_at[k]
        return model.sum(10 ** (length - 1 - t) * M[row - 1 + t][col - 1] for t in range(length))

    def member(expr, values, name):
        # expr takes one of the given values: one indicator per value, exactly one on.
        pick = [model.binary_var(name=f"{name}_{v}") for v in values]
        model.add_constraint(model.sum(pick) == 1)
        model.add_constraint(expr == model.sum(v * b for v, b in zip(values, pick)))
        return pick

    def times_choice(factor, hi, pick, values, name):
        # factor * (the value chosen by pick), with factor in 0..hi: sum over the values of
        # value * (factor if that value is chosen, else 0), each product linearised as the
        # product of a binary and a bounded integer.
        terms = []
        for v, b in zip(values, pick):
            p = model.integer_var(0, hi, name=f"{name}_{v}")
            model.add_constraint(p <= hi * b)
            model.add_constraint(p <= factor)
            model.add_constraint(p >= factor - hi * (1 - b))
            terms.append(v * p)
        return model.sum(terms)

    # The reference allows numbers up to 9999; primes and squares in that range.
    top = 9999

    def is_prime(v):
        return v >= 2 and all(v % d for d in range(2, math.isqrt(v) + 1))

    def candidates(values, k):
        # Only values that fit in the clue's number of digits can be written there.
        return [v for v in values if v < 10 ** across_at[k][0]]

    primes = [v for v in range(2, top + 1) if is_prime(v)]
    squares = [v * v for v in range(1, 1 + math.ceil(math.sqrt(top)))]

    # Across clues.
    model.add_constraint(A(1) == 2 * A(27))                 # 27 across times two
    model.add_constraint(A(4) == D(4) + 71)                 # 4 down plus seventy-one
    model.add_constraint(A(7) == D(18) + 4)                 # 18 down plus four
    model.add_constraint(16 * A(8) == D(6))                 # 6 down divided by sixteen
    model.add_constraint(A(9) == D(2) - 18)                 # 2 down minus eighteen
    model.add_constraint(12 * A(10) == 6 * 144)             # dozen in six gross
    model.add_constraint(A(11) == D(5) - 70)                # 5 down minus seventy
    model.add_constraint(A(15) == D(6) - 350)               # 6 down minus 350
    square20 = candidates(squares, 20)
    member(A(20), square20, "square20")                     # a square number
    prime23 = candidates(primes, 23)
    is23 = member(A(23), prime23, "prime23")                # a prime number
    member(A(24), candidates(squares, 24), "square24")      # a square number
    model.add_constraint(17 * A(25) == A(20))               # 20 across divided by seventeen
    model.add_constraint(4 * A(27) == D(6))                 # 6 down divided by four
    model.add_constraint(A(28) == 4 * 12)                   # four dozen
    model.add_constraint(A(29) == 7 * 144)                  # seven gross
    model.add_constraint(A(30) == D(22) + 450)              # 22 down plus 450
    # 13 across is 26 down times 23 across, and 17 across is 25 across times 23 across.
    # Both are products of two unknowns, which CPLEX refuses; 23 across is one of the
    # listed primes, so each product is a sum over those primes. 26 down and 25 across are
    # two-digit numbers, at most 99.
    model.add_constraint(A(13) == times_choice(D(26), 99, is23, prime23, "d26_times"))
    model.add_constraint(A(17) == times_choice(A(25), 99, is23, prime23, "a25_times"))

    # Down clues.
    model.add_constraint(D(1) == A(1) + 27)                 # 1 across plus twenty-seven
    model.add_constraint(D(2) == 5 * 12)                    # five dozen
    model.add_constraint(D(3) == A(30) + 888)               # 30 across plus 888
    model.add_constraint(D(4) == 2 * A(17))                 # two times 17 across
    model.add_constraint(12 * D(5) == A(29))                # 29 across divided by twelve
    # 28 across times 23 across, a product of two unknowns written as a sum over the primes
    # 23 across can be, like 13 and 17 across; 28 across has two digits, at most 99.
    model.add_constraint(D(6) == times_choice(A(28), 99, is23, prime23, "a28_times"))
    model.add_constraint(D(10) == A(10) + 4)                # 10 across plus four
    model.add_constraint(D(12) == 3 * A(24))                # three times 24 across
    model.add_constraint(16 * D(14) == A(13))               # 13 across divided by sixteen
    model.add_constraint(D(16) == 15 * D(28))               # 28 down times fifteen
    model.add_constraint(D(17) == A(13) - 399)              # 13 across minus 399
    model.add_constraint(18 * D(18) == A(29))               # 29 across divided by eighteen
    model.add_constraint(D(19) == D(22) - 94)               # 22 down minus ninety-four
    model.add_constraint(D(20) == A(20) - 9)                # 20 across minus nine
    model.add_constraint(D(21) == A(25) - 52)               # 25 across minus fifty-two
    model.add_constraint(D(22) == 6 * D(20))                # 20 down times six
    model.add_constraint(D(26) == 5 * A(24))                # five times 24 across
    model.add_constraint(D(28) == D(21) + 27)               # 21 down plus twenty-seven

    return model, {"M": M}
