"""Crossfigure (CSPLib 21): fill a 9x9 grid with digits so that every across and down number satisfies its clue."""
import gurobipy as gp
from gurobipy import GRB

# The puzzle has no instance data: the grid, the clue positions and the clues
# are fixed by the problem statement and mirrored here from the reference.
N = 9
BLACK = [
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
# (number, length, row, column), rows and columns counted from 1.
ACROSS = [(1, 4, 1, 1), (4, 4, 1, 6), (7, 2, 2, 1), (8, 3, 2, 4), (9, 2, 2, 8),
          (10, 2, 3, 3), (11, 2, 3, 6), (13, 4, 4, 1), (15, 4, 4, 6), (17, 4, 6, 1),
          (20, 4, 6, 6), (23, 2, 7, 3), (24, 2, 7, 6), (25, 2, 8, 1), (27, 3, 8, 4),
          (28, 2, 8, 8), (29, 4, 9, 1), (30, 4, 9, 6)]
DOWN = [(1, 4, 1, 1), (2, 2, 1, 2), (3, 4, 1, 4), (4, 4, 1, 6), (5, 2, 1, 8),
        (6, 4, 1, 9), (10, 2, 3, 3), (12, 2, 3, 7), (14, 3, 4, 2), (16, 3, 4, 8),
        (17, 4, 6, 1), (18, 2, 6, 3), (19, 4, 6, 4), (20, 4, 6, 6), (21, 2, 6, 7),
        (22, 4, 6, 9), (26, 2, 8, 2), (28, 2, 8, 8)]


def _is_prime(n):
    return n >= 2 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def build(instance):
    model = gp.Model("crossfigures")

    # M[i][j] is the digit in each cell.
    M = [[model.addVar(lb=0, ub=9, vtype=GRB.INTEGER, name=f"M[{i},{j}]") for j in range(N)]
         for i in range(N)]

    # Black squares hold 0.
    for i in range(N):
        for j in range(N):
            if BLACK[i][j] == "#":
                model.addConstr(M[i][j] == 0, name=f"black[{i},{j}]")

    # Each across or down number is read from its digits, most significant first
    # (a leading zero is allowed, as in the reference).
    def number(length, row, col, across):
        cells = [M[row - 1][col - 1 + k] if across else M[row - 1 + k][col - 1] for k in range(length)]
        return gp.quicksum(10 ** (length - 1 - k) * cells[k] for k in range(length))

    A = {c: number(L, r, k, True) for c, L, r, k in ACROSS}
    D = {c: number(L, r, k, False) for c, L, r, k in DOWN}
    width = {("A", c): L for c, L, _, _ in ACROSS}
    width.update({("D", c): L for c, L, _, _ in DOWN})

    # 23 across is a prime number: it selects exactly one prime of its width,
    # which also lets the three clues that multiply by 23 across stay linear.
    primes = [p for p in range(2, 10 ** width[("A", 23)]) if _is_prime(p)]
    prime = model.addVars(len(primes), vtype=GRB.BINARY, name="prime")
    model.addConstr(prime.sum() == 1, name="a23_prime")
    model.addConstr(A[23] == gp.quicksum(p * prime[k] for k, p in enumerate(primes)), name="a23_value")

    def times_a23(expr, upper, name):
        """A linear expression equal to expr * (23 across), for 0 <= expr <= upper:
        each selected-prime binary times expr is linearised as the skill shows."""
        parts = []
        for k, p in enumerate(primes):
            z = model.addVar(lb=0, ub=upper, vtype=GRB.CONTINUOUS, name=f"{name}[{p}]")
            model.addConstr(z <= upper * prime[k])
            model.addConstr(z <= expr)
            model.addConstr(z >= expr - upper * (1 - prime[k]))
            parts.append(p * z)
        return gp.quicksum(parts)

    def square_of_width(expr, length, name):
        """expr is a square number (1, 4, 9, ...) of at most `length` digits."""
        squares = [i * i for i in range(1, 10 ** length) if i * i < 10 ** length]
        pick = model.addVars(len(squares), vtype=GRB.BINARY, name=name)
        model.addConstr(pick.sum() == 1)
        model.addConstr(expr == gp.quicksum(s * pick[k] for k, s in enumerate(squares)))

    # Across clues.
    model.addConstr(A[1] == 2 * A[27], name="a1")                  # 27 across times two
    model.addConstr(A[4] == D[4] + 71, name="a4")                  # 4 down plus seventy-one
    model.addConstr(A[7] == D[18] + 4, name="a7")                  # 18 down plus four
    model.addConstr(16 * A[8] == D[6], name="a8")                  # 6 down divided by sixteen
    model.addConstr(A[9] == D[2] - 18, name="a9")                  # 2 down minus eighteen
    model.addConstr(12 * A[10] == 6 * 144, name="a10")             # dozen in six gross
    model.addConstr(A[11] == D[5] - 70, name="a11")                # 5 down minus seventy
    model.addConstr(A[13] == times_a23(D[26], 99, "d26_a23"), name="a13")   # 26 down times 23 across
    model.addConstr(A[15] == D[6] - 350, name="a15")               # 6 down minus 350
    model.addConstr(A[17] == times_a23(A[25], 99, "a25_a23"), name="a17")   # 25 across times 23 across
    square_of_width(A[20], width[("A", 20)], "a20_square")         # a square number
    square_of_width(A[24], width[("A", 24)], "a24_square")         # a square number
    model.addConstr(17 * A[25] == A[20], name="a25")               # 20 across divided by seventeen
    model.addConstr(4 * A[27] == D[6], name="a27")                 # 6 down divided by four
    model.addConstr(A[28] == 4 * 12, name="a28")                   # four dozen
    model.addConstr(A[29] == 7 * 144, name="a29")                  # seven gross
    model.addConstr(A[30] == D[22] + 450, name="a30")              # 22 down plus 450

    # Down clues.
    model.addConstr(D[1] == A[1] + 27, name="d1")                  # 1 across plus twenty-seven
    model.addConstr(D[2] == 5 * 12, name="d2")                     # five dozen
    model.addConstr(D[3] == A[30] + 888, name="d3")                # 30 across plus 888
    model.addConstr(D[4] == 2 * A[17], name="d4")                  # two times 17 across
    model.addConstr(12 * D[5] == A[29], name="d5")                 # 29 across divided by twelve
    model.addConstr(D[6] == times_a23(A[28], 99, "a28_a23"), name="d6")     # 28 across times 23 across
    model.addConstr(D[10] == A[10] + 4, name="d10")                # 10 across plus four
    model.addConstr(D[12] == 3 * A[24], name="d12")                # three times 24 across
    model.addConstr(16 * D[14] == A[13], name="d14")               # 13 across divided by sixteen
    model.addConstr(D[16] == 15 * D[28], name="d16")               # 28 down times fifteen
    model.addConstr(D[17] == A[13] - 399, name="d17")              # 13 across minus 399
    model.addConstr(18 * D[18] == A[29], name="d18")               # 29 across divided by eighteen
    model.addConstr(D[19] == D[22] - 94, name="d19")               # 22 down minus ninety-four
    model.addConstr(D[20] == A[20] - 9, name="d20")                # 20 across minus nine
    model.addConstr(D[21] == A[25] - 52, name="d21")               # 25 across minus fifty-two
    model.addConstr(D[22] == 6 * D[20], name="d22")                # 20 down times six
    model.addConstr(D[26] == 5 * A[24], name="d26")                # five times 24 across
    model.addConstr(D[28] == D[21] + 27, name="d28")               # 21 down plus twenty-seven

    return model, {"M": M}
