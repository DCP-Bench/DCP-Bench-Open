# Crossfigure: fill a 9 x 9 grid with digits so that the numbers read across
# and down satisfy their clues (multiples of one another, sums, primes, squares).
# A black cell is written 0 in the answer. The grid and the clues are fixed by
# the problem, so they are mirrored here.
from ortools.sat.python import cp_model

MAX_NUMBER = 9999  # the longest entries have four digits
SIZE = 9
# the black boxes of the grid
BLACK = [(0, 4), (1, 2), (1, 6), (2, 1), (2, 4), (2, 7), (3, 4), (4, 0), (4, 2), (4, 3), (4, 4), (4, 5),
         (4, 6), (4, 8), (5, 4), (6, 1), (6, 4), (6, 7), (7, 2), (7, 6), (8, 4)]
# entries as clue number: (length, row, column), rows and columns counted from 1
ACROSS = {1: (4, 1, 1), 4: (4, 1, 6), 7: (2, 2, 1), 8: (3, 2, 4), 9: (2, 2, 8), 10: (2, 3, 3), 11: (2, 3, 6),
          13: (4, 4, 1), 15: (4, 4, 6), 17: (4, 6, 1), 20: (4, 6, 6), 23: (2, 7, 3), 24: (2, 7, 6),
          25: (2, 8, 1), 27: (3, 8, 4), 28: (2, 8, 8), 29: (4, 9, 1), 30: (4, 9, 6)}
DOWN = {1: (4, 1, 1), 2: (2, 1, 2), 3: (4, 1, 4), 4: (4, 1, 6), 5: (2, 1, 8), 6: (4, 1, 9), 10: (2, 3, 3),
        12: (2, 3, 7), 14: (3, 4, 2), 16: (3, 4, 8), 17: (4, 6, 1), 18: (2, 6, 3), 19: (4, 6, 4),
        20: (4, 6, 6), 21: (2, 6, 7), 22: (4, 6, 9), 26: (2, 8, 2), 28: (2, 8, 8)}


def is_prime(k):
    return k >= 2 and all(k % d for d in range(2, int(k**0.5) + 1))


def build(instance):
    model = cp_model.CpModel()

    # M[r][c] = the digit in the cell; the black boxes stay 0
    M = [[model.new_int_var(0, 9, f"M_{r}_{c}") for c in range(SIZE)] for r in range(SIZE)]
    for r, c in BLACK:
        model.add(M[r][c] == 0)

    # A[k] / D[k] = the number written across / down at clue k, read off the digits
    A = {k: model.new_int_var(0, MAX_NUMBER, f"A{k}") for k in ACROSS}
    D = {k: model.new_int_var(0, MAX_NUMBER, f"D{k}") for k in DOWN}
    for k, (length, row, col) in ACROSS.items():
        model.add(A[k] == sum(10 ** (length - i - 1) * M[row - 1][col - 1 + i] for i in range(length)))
    for k, (length, row, col) in DOWN.items():
        model.add(D[k] == sum(10 ** (length - i - 1) * M[row - 1 + i][col - 1] for i in range(length)))

    squares = cp_model.Domain.from_values([i * i for i in range(1, 101)])
    primes = cp_model.Domain.from_values([k for k in range(2, MAX_NUMBER + 1) if is_prime(k)])

    # across clues
    model.add(A[1] == 2 * A[27])  # 1: 27 across times two
    model.add(A[4] == D[4] + 71)  # 4: 4 down plus seventy-one
    model.add(A[7] == D[18] + 4)  # 7: 18 down plus four
    model.add(16 * A[8] == D[6])  # 8: 6 down divided by sixteen
    model.add(A[9] == D[2] - 18)  # 9: 2 down minus eighteen
    model.add(12 * A[10] == 6 * 144)  # 10: a dozen in six gross
    model.add(A[11] == D[5] - 70)  # 11: 5 down minus seventy
    model.add_multiplication_equality(A[13], [D[26], A[23]])  # 13: 26 down times 23 across
    model.add(A[15] == D[6] - 350)  # 15: 6 down minus 350
    model.add_multiplication_equality(A[17], [A[25], A[23]])  # 17: 25 across times 23 across
    model.add_linear_expression_in_domain(A[20], squares)  # 20: a square number
    model.add_linear_expression_in_domain(A[23], primes)  # 23: a prime number
    model.add_linear_expression_in_domain(A[24], squares)  # 24: a square number
    model.add(17 * A[25] == A[20])  # 25: 20 across divided by seventeen
    model.add(4 * A[27] == D[6])  # 27: 6 down divided by four
    model.add(A[28] == 4 * 12)  # 28: four dozen
    model.add(A[29] == 7 * 144)  # 29: seven gross
    model.add(A[30] == D[22] + 450)  # 30: 22 down plus 450

    # down clues
    model.add(D[1] == A[1] + 27)  # 1: 1 across plus twenty-seven
    model.add(D[2] == 5 * 12)  # 2: five dozen
    model.add(D[3] == A[30] + 888)  # 3: 30 across plus 888
    model.add(D[4] == 2 * A[17])  # 4: two times 17 across
    model.add(12 * D[5] == A[29])  # 5: 29 across divided by twelve
    model.add_multiplication_equality(D[6], [A[28], A[23]])  # 6: 28 across times 23 across
    model.add(D[10] == A[10] + 4)  # 10: 10 across plus four
    model.add(D[12] == 3 * A[24])  # 12: three times 24 across
    model.add(16 * D[14] == A[13])  # 14: 13 across divided by sixteen
    model.add(D[16] == 15 * D[28])  # 16: 28 down times fifteen
    model.add(D[17] == A[13] - 399)  # 17: 13 across minus 399
    model.add(18 * D[18] == A[29])  # 18: 29 across divided by eighteen
    model.add(D[19] == D[22] - 94)  # 19: 22 down minus ninety-four
    model.add(D[20] == A[20] - 9)  # 20: 20 across minus nine
    model.add(D[21] == A[25] - 52)  # 21: 25 across minus fifty-two
    model.add(D[22] == 6 * D[20])  # 22: 20 down times six
    model.add(D[26] == 5 * A[24])  # 26: five times 24 across
    model.add(D[28] == D[21] + 27)  # 28: 21 down plus twenty-seven

    return model, {"M": M}
